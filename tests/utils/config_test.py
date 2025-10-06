import pytest


@pytest.fixture(autouse=True)
def clear_config_module(monkeypatch):
    monkeypatch.delenv("DYNAMO_TABLE", raising=False)
    monkeypatch.delenv("REGION", raising=False)

def make_config():
    from utils import config
    import importlib
    importlib.reload(config)
    return config.Config

def test_config_defaults(monkeypatch):
    cfg = make_config()
    assert cfg.DYNAMO_TABLE == "messages_table"
    assert cfg.REGION == "us-east-1"

def test_config_env_variables(monkeypatch):
    monkeypatch.setenv("DYNAMO_TABLE", "processed-messages")
    monkeypatch.setenv("REGION", "us-west-2")

    cfg = make_config()
    assert cfg.DYNAMO_TABLE == "processed-messages"
    assert cfg.REGION == "us-west-2"

def test_config_partial_env(monkeypatch):
    monkeypatch.setenv("DYNAMO_TABLE", "processed-messages")

    cfg = make_config()
    assert cfg.DYNAMO_TABLE == "processed-messages"
