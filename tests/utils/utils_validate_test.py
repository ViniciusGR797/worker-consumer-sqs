import pytest
from pydantic import ValidationError
from utils.validate import validate
from schemas.transactions import TransactionSchema


def test_validate_success():
    data = {
        "transaction_id": "txn-123",
        "payer_id": "user-1",
        "receiver_id": "user-2",
        "amount": 100.50,
        "currency": "USD",
        "description": "Test transaction"
    }
    validated, err = validate(TransactionSchema, data)
    assert err is None
    assert validated.transaction_id == data["transaction_id"]
    assert validated.amount == data["amount"]


def test_validate_missing_required_field():
    data = {
        "payer_id": "user-1",
        "receiver_id": "user-2",
        "amount": 50.0,
        "currency": "BRL"
    }  # falta transaction_id
    validated, err = validate(TransactionSchema, data)
    assert validated is None
    assert isinstance(err, list)
    assert any(e['loc'] == ('transaction_id',) for e in err)


def test_validate_invalid_amount_type():
    data = {
        "transaction_id": "txn-456",
        "payer_id": "user-1",
        "receiver_id": "user-2",
        "amount": -10,
        "currency": "BRL"
    }
    validated, err = validate(TransactionSchema, data)
    assert validated is None
    assert isinstance(err, list)
    assert any(e['loc'] == ('amount',) for e in err)


def test_validate_extra_field_ignored():
    data = {
        "transaction_id": "txn-789",
        "payer_id": "user-1",
        "receiver_id": "user-2",
        "amount": 75.0,
        "currency": "USD",
        "extra_field": "ignore me"
    }
    validated, err = validate(TransactionSchema, data)
    assert err is None
    assert hasattr(validated, "transaction_id")
    assert not hasattr(validated, "extra_field")


def test_validate_generic_exception(monkeypatch):
    def fake_init(self, **kwargs):
        raise Exception("Unexpected error")

    monkeypatch.setattr(TransactionSchema, "__init__", fake_init)
    data = {
        "transaction_id": "txn-000",
        "payer_id": "user-1",
        "receiver_id": "user-2",
        "amount": 10,
        "currency": "USD"
    }
    validated, err = validate(TransactionSchema, data)
    assert validated is None
    assert err == "Unexpected error"
