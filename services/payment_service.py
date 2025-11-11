"""
Payment Service - Simulated External Payment Gateway
"""

from typing import Dict, Optional
import random


class PaymentGatewayError(Exception):
    pass


class PaymentGateway:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "test_api_key_12345"
        self.transaction_log = []
    
    def process_payment(self, patron_id: str, amount: float, description: str = "") -> Dict:
        # Validate inputs
        if not patron_id or not isinstance(patron_id, str):
            raise PaymentGatewayError("Invalid patron ID")
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise PaymentGatewayError("Amount must be a positive number")
        
        # Simulate payment processing (90% success rate)
        success = random.random() > 0.1
        
        if success:
            transaction_id = f"txn_{random.randint(100000, 999999)}"
            transaction = {
                'transaction_id': transaction_id,
                'status': 'success',
                'amount': round(amount, 2),
                'patron_id': patron_id,
                'description': description,
                'message': 'Payment processed successfully'
            }
            self.transaction_log.append(transaction)
            return transaction
        else:
            raise PaymentGatewayError("Payment processing failed - insufficient funds or card declined")
    
    def process_refund(self, transaction_id: str, amount: float) -> Dict:
        # Validate inputs
        if not transaction_id or not isinstance(transaction_id, str):
            raise PaymentGatewayError("Invalid transaction ID")
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise PaymentGatewayError("Refund amount must be a positive number")
        
        # Find original transaction
        original_transaction = None
        for txn in self.transaction_log:
            if txn.get('transaction_id') == transaction_id:
                original_transaction = txn
                break
        
        if not original_transaction:
            raise PaymentGatewayError(f"Transaction {transaction_id} not found")
        
        if amount > original_transaction['amount']:
            raise PaymentGatewayError("Refund amount cannot exceed original transaction amount")
        
        # Simulate refund processing (95% success rate)
        success = random.random() > 0.05
        
        if success:
            refund_id = f"ref_{random.randint(100000, 999999)}"
            refund = {
                'refund_id': refund_id,
                'status': 'success',
                'amount': round(amount, 2),
                'original_transaction_id': transaction_id,
                'message': 'Refund processed successfully'
            }
            return refund
        else:
            raise PaymentGatewayError("Refund processing failed - gateway error")
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        for txn in self.transaction_log:
            if txn.get('transaction_id') == transaction_id:
                return txn.copy()
        return None
