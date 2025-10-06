import pytest
from datetime import timedelta


@pytest.fixture(autouse=True)
def clear_config_module(monkeypatch):
    monkeypatch.delenv("APP_USER_EMAIL", raising=False)
    monkeypatch.delenv("APP_USER_PASSWORD", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_ACCESS_TOKEN_EXPIRES", raising=False)
    monkeypatch.delenv("REGION", raising=False)
    monkeypatch.delenv("SQS_NAME", raising=False)
    monkeypatch.delenv("DLQ_NAME", raising=False)

def make_config():
    from utils import config
    import importlib
    importlib.reload(config)
    return config.Config

def test_config_defaults(monkeypatch):
    cfg = make_config()
    assert cfg.APP_USER_EMAIL == "user@example.com"
    assert cfg.APP_USER_PASSWORD == "strongpassword123"
    assert cfg.JWT_SECRET_KEY == "<random_secret_key>"
    assert cfg.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=6)
    assert cfg.REGION == "us-east-1"
    assert cfg.SQS_NAME == "main_queue.fifo"
    assert cfg.DLQ_NAME == "dlq_queue.fifo"

def test_config_env_variables(monkeypatch):
    monkeypatch.setenv("APP_USER_EMAIL", "env_user@test.com")
    monkeypatch.setenv("APP_USER_PASSWORD", "envpassword")
    monkeypatch.setenv("JWT_SECRET_KEY", "envsecret")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRES", "12")
    monkeypatch.setenv("REGION", "us-west-2")
    monkeypatch.setenv("SQS_NAME", "env_queue.fifo")
    monkeypatch.setenv("DLQ_NAME", "env_dlq.fifo")

    cfg = make_config()
    assert cfg.APP_USER_EMAIL == "env_user@test.com"
    assert cfg.APP_USER_PASSWORD == "envpassword"
    assert cfg.JWT_SECRET_KEY == "envsecret"
    assert cfg.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=12)
    assert cfg.REGION == "us-west-2"
    assert cfg.SQS_NAME == "env_queue.fifo"
    assert cfg.DLQ_NAME == "env_dlq.fifo"

def test_config_partial_env(monkeypatch):
    monkeypatch.setenv("APP_USER_EMAIL", "partial@test.com")
    monkeypatch.delenv("APP_USER_PASSWORD", raising=False)
    monkeypatch.delenv("JWT_ACCESS_TOKEN_EXPIRES", raising=False)

    cfg = make_config()
    assert cfg.APP_USER_EMAIL == "partial@test.com"
    assert cfg.APP_USER_PASSWORD == "strongpassword123"
    assert cfg.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=6)
