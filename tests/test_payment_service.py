import pytest
import sys
import os
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.payment_service import PaymentGateway, PaymentGatewayError


def test_process_payment_success():
    with patch('random.random', return_value=0.5):
        gateway = PaymentGateway()
        result = gateway.process_payment('123456', 5.00, 'Late fee')
        assert result['status'] == 'success'
        assert result['amount'] == 5.00

def test_process_payment_invalid_patron_id():
    gateway = PaymentGateway()
    with pytest.raises(PaymentGatewayError):
        gateway.process_payment('', 5.00)

def test_process_payment_invalid_amount():
    gateway = PaymentGateway()
    with pytest.raises(PaymentGatewayError):
        gateway.process_payment('123456', -5.00)

def test_process_refund_success():
    with patch('random.random', return_value=0.5):
        gateway = PaymentGateway()
        payment = gateway.process_payment('123456', 10.00)
        refund = gateway.process_refund(payment['transaction_id'], 5.00)
        assert refund['status'] == 'success'

def test_process_refund_invalid_transaction():
    gateway = PaymentGateway()
    with pytest.raises(PaymentGatewayError):
        gateway.process_refund('invalid', 5.00)

def test_process_refund_excessive_amount():
    with patch('random.random', return_value=0.5):
        gateway = PaymentGateway()
        payment = gateway.process_payment('123456', 5.00)
        with pytest.raises(PaymentGatewayError):
            gateway.process_refund(payment['transaction_id'], 10.00)

def test_get_transaction():
    with patch('random.random', return_value=0.5):
        gateway = PaymentGateway()
        payment = gateway.process_payment('123456', 5.00)
        txn = gateway.get_transaction(payment['transaction_id'])
        assert txn is not None
        assert txn['amount'] == 5.00
