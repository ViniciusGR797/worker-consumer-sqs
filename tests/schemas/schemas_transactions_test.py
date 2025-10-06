import pytest
from pydantic import ValidationError
from schemas.transactions import TransactionSchema

def test_transaction_schema_success_with_description():
    data = {
        "transaction_id": "txn-001",
        "payer_id": "payer001",
        "receiver_id": "receiver001",
        "amount": 100.5,
        "currency": "USD",
        "description": "Test payment"
    }
    tx = TransactionSchema(**data)
    assert tx.transaction_id == "txn-001"
    assert tx.description == "Test payment"

def test_transaction_schema_success_without_description():
    data = {
        "transaction_id": "txn-002",
        "payer_id": "payer002",
        "receiver_id": "receiver002",
        "amount": 250,
        "currency": "BRL"
    }
    tx = TransactionSchema(**data)
    assert tx.description is None

@pytest.mark.parametrize("invalid_data", [
    {"payer_id": "payer003", "receiver_id": "receiver003", "amount": 50, "currency": "EUR"},
    {"transaction_id": "txn-004", "receiver_id": "receiver004", "amount": 75, "currency": "USD"},
    {"transaction_id": "txn-005", "payer_id": "payer005", "amount": 100, "currency": "USD"},
    {"transaction_id": "txn-006", "payer_id": "payer006", "receiver_id": "receiver006", "currency": "BRL"},
    {"transaction_id": "txn-007", "payer_id": "payer007", "receiver_id": "receiver007", "amount": 120}
])
def test_transaction_schema_missing_required_fields(invalid_data):
    with pytest.raises(ValidationError):
        TransactionSchema(**invalid_data)

@pytest.mark.parametrize("invalid_data", [
    {"transaction_id": "txn-008", "payer_id": "payer008", "receiver_id": "receiver008", "amount": -10, "currency": "USD"},
    {"transaction_id": "txn-009", "payer_id": "payer009", "receiver_id": "receiver009", "amount": 0, "currency": "USD"},
])
def test_transaction_schema_invalid_amount(invalid_data):
    with pytest.raises(ValidationError):
        TransactionSchema(**invalid_data)

@pytest.mark.parametrize("invalid_data", [
    {"transaction_id": 123, "payer_id": "payer010", "receiver_id": "receiver010", "amount": 50, "currency": "USD"},
    {"transaction_id": "txn-011", "payer_id": None, "receiver_id": "receiver011", "amount": 50, "currency": "USD"},
    {"transaction_id": "txn-012", "payer_id": "payer012", "receiver_id": 123, "amount": 50, "currency": "USD"},
])
def test_transaction_schema_invalid_types(invalid_data):
    with pytest.raises(ValidationError):
        TransactionSchema(**invalid_data)
