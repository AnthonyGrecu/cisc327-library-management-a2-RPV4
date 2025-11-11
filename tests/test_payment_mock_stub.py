"""
Tests for payment functions using mocking and stubbing
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway, PaymentGatewayError


# pay_late_fees()

class TestPayLateFees:
    
    def test_pay_late_fees_successful_payment(self):
        # Create a mock PaymentGateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub the process_payment method to return a successful response
        mock_gateway.process_payment.return_value = {
            'transaction_id': 'txn_123456',
            'status': 'success',
            'amount': 5.00,
            'patron_id': '123456',
            'message': 'Payment processed successfully'
        }
        
        # Call the function with the mocked gateway
        success, message, transaction_id = pay_late_fees('123456', 5.00, mock_gateway)
        
        # Assertions
        assert success is True
        assert 'successfully' in message.lower()
        assert transaction_id == 'txn_123456'
        assert '$5.00' in message
        
        # Verify the mock was called correctly
        mock_gateway.process_payment.assert_called_once_with(
            patron_id='123456',
            amount=5.00,
            description='Library late fees for patron 123456'
        )
    
    def test_pay_late_fees_invalid_patron_id_short(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, transaction_id = pay_late_fees('12345', 5.00, mock_gateway)
        
        assert success is False
        assert 'invalid patron id' in message.lower()
        assert '6 digits' in message
        assert transaction_id is None
        
        # Gateway should NOT be called for invalid input
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_invalid_patron_id_long(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, transaction_id = pay_late_fees('1234567', 5.00, mock_gateway)
        
        assert success is False
        assert 'invalid patron id' in message.lower()
        assert transaction_id is None
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_invalid_patron_id_non_numeric(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, transaction_id = pay_late_fees('12345a', 5.00, mock_gateway)
        
        assert success is False
        assert 'invalid patron id' in message.lower()
        assert transaction_id is None
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_negative_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, transaction_id = pay_late_fees('123456', -5.00, mock_gateway)
        
        assert success is False
        assert 'positive' in message.lower()
        assert transaction_id is None
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_zero_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, transaction_id = pay_late_fees('123456', 0, mock_gateway)
        
        assert success is False
        assert 'positive' in message.lower()
        assert transaction_id is None
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_amount_exceeds_maximum(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, transaction_id = pay_late_fees('123456', 20.00, mock_gateway)
        
        assert success is False
        assert 'exceeds maximum' in message.lower()
        assert '$15.00' in message
        assert transaction_id is None
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_gateway_raises_error(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub the method to raise an exception
        mock_gateway.process_payment.side_effect = PaymentGatewayError("Card declined")
        
        success, message, transaction_id = pay_late_fees('123456', 5.00, mock_gateway)
        
        assert success is False
        assert 'payment gateway error' in message.lower()
        assert 'card declined' in message.lower()
        assert transaction_id is None
    
    def test_pay_late_fees_gateway_raises_generic_exception(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub the method to raise a generic exception
        mock_gateway.process_payment.side_effect = Exception("Network error")
        
        success, message, transaction_id = pay_late_fees('123456', 5.00, mock_gateway)
        
        assert success is False
        assert 'unexpected error' in message.lower()
        assert 'network error' in message.lower()
        assert transaction_id is None
    
    def test_pay_late_fees_without_gateway_parameter(self):
        
        # Use patch to mock the PaymentGateway class
        with patch('services.library_service.PaymentGateway') as MockGatewayClass:
            mock_instance = Mock()
            MockGatewayClass.return_value = mock_instance
            
            mock_instance.process_payment.return_value = {
                'transaction_id': 'txn_789',
                'status': 'success',
                'amount': 3.50,
                'patron_id': '654321',
                'message': 'Payment processed successfully'
            }
            
            success, message, transaction_id = pay_late_fees('654321', 3.50)
            
            assert success is True
            assert transaction_id == 'txn_789'
            
            # Verify that PaymentGateway was instantiated
            MockGatewayClass.assert_called_once()
            mock_instance.process_payment.assert_called_once()
    
    def test_pay_late_fees_maximum_allowed_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_payment.return_value = {
            'transaction_id': 'txn_max',
            'status': 'success',
            'amount': 15.00,
            'patron_id': '123456',
            'message': 'Payment processed successfully'
        }
        
        success, message, transaction_id = pay_late_fees('123456', 15.00, mock_gateway)
        
        assert success is True
        assert transaction_id == 'txn_max'
        assert '$15.00' in message
    
    def test_pay_late_fees_small_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_payment.return_value = {
            'transaction_id': 'txn_small',
            'status': 'success',
            'amount': 0.50,
            'patron_id': '123456',
            'message': 'Payment processed successfully'
        }
        
        success, message, transaction_id = pay_late_fees('123456', 0.50, mock_gateway)
        
        assert success is True
        assert transaction_id == 'txn_small'
        mock_gateway.process_payment.assert_called_once()


# refund_late_fee_payment()

class TestRefundLateFeePayment:
    
    
    def test_refund_successful(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub the process_refund method to return a successful response
        mock_gateway.process_refund.return_value = {
            'refund_id': 'ref_123456',
            'status': 'success',
            'amount': 5.00,
            'original_transaction_id': 'txn_123456',
            'message': 'Refund processed successfully'
        }
        
        success, message, refund_id = refund_late_fee_payment('txn_123456', 5.00, mock_gateway)
        
        assert success is True
        assert 'successfully' in message.lower()
        assert refund_id == 'ref_123456'
        assert '$5.00' in message
        
        # Verify the mock was called correctly
        mock_gateway.process_refund.assert_called_once_with(
            transaction_id='txn_123456',
            amount=5.00
        )
    
    def test_refund_invalid_transaction_id_empty(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, refund_id = refund_late_fee_payment('', 5.00, mock_gateway)
        
        assert success is False
        assert 'invalid transaction id' in message.lower()
        assert refund_id is None
        mock_gateway.process_refund.assert_not_called()
    
    def test_refund_invalid_transaction_id_none(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, refund_id = refund_late_fee_payment(None, 5.00, mock_gateway)
        
        assert success is False
        assert 'invalid transaction id' in message.lower()
        assert refund_id is None
        mock_gateway.process_refund.assert_not_called()
    
    def test_refund_negative_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, refund_id = refund_late_fee_payment('txn_123', -5.00, mock_gateway)
        
        assert success is False
        assert 'positive' in message.lower()
        assert refund_id is None
        mock_gateway.process_refund.assert_not_called()
    
    def test_refund_zero_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, refund_id = refund_late_fee_payment('txn_123', 0, mock_gateway)
        
        assert success is False
        assert 'positive' in message.lower()
        assert refund_id is None
        mock_gateway.process_refund.assert_not_called()
    
    def test_refund_amount_exceeds_maximum(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        success, message, refund_id = refund_late_fee_payment('txn_123', 20.00, mock_gateway)
        
        assert success is False
        assert 'exceeds maximum' in message.lower()
        assert '$15.00' in message
        assert refund_id is None
        mock_gateway.process_refund.assert_not_called()
    
    def test_refund_gateway_raises_error_transaction_not_found(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_refund.side_effect = PaymentGatewayError("Transaction txn_999 not found")
        
        success, message, refund_id = refund_late_fee_payment('txn_999', 5.00, mock_gateway)
        
        assert success is False
        assert 'payment gateway error' in message.lower()
        assert 'not found' in message.lower()
        assert refund_id is None
    
    def test_refund_gateway_raises_error_amount_exceeds_original(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_refund.side_effect = PaymentGatewayError(
            "Refund amount cannot exceed original transaction amount"
        )
        
        success, message, refund_id = refund_late_fee_payment('txn_123', 10.00, mock_gateway)
        
        assert success is False
        assert 'payment gateway error' in message.lower()
        assert refund_id is None
    
    def test_refund_gateway_raises_generic_exception(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_refund.side_effect = Exception("Database connection lost")
        
        success, message, refund_id = refund_late_fee_payment('txn_123', 5.00, mock_gateway)
        
        assert success is False
        assert 'unexpected error' in message.lower()
        assert 'database connection lost' in message.lower()
        assert refund_id is None
    
    def test_refund_without_gateway_parameter(self):
        
        with patch('services.library_service.PaymentGateway') as MockGatewayClass:
            mock_instance = Mock()
            MockGatewayClass.return_value = mock_instance
            
            mock_instance.process_refund.return_value = {
                'refund_id': 'ref_auto',
                'status': 'success',
                'amount': 3.50,
                'original_transaction_id': 'txn_auto',
                'message': 'Refund processed successfully'
            }
            
            success, message, refund_id = refund_late_fee_payment('txn_auto', 3.50)
            
            assert success is True
            assert refund_id == 'ref_auto'
            
            # Verify that PaymentGateway was instantiated
            MockGatewayClass.assert_called_once()
            mock_instance.process_refund.assert_called_once()
    
    def test_refund_maximum_allowed_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_refund.return_value = {
            'refund_id': 'ref_max',
            'status': 'success',
            'amount': 15.00,
            'original_transaction_id': 'txn_max',
            'message': 'Refund processed successfully'
        }
        
        success, message, refund_id = refund_late_fee_payment('txn_max', 15.00, mock_gateway)
        
        assert success is True
        assert refund_id == 'ref_max'
        assert '$15.00' in message
    
    def test_refund_partial_amount(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        mock_gateway.process_refund.return_value = {
            'refund_id': 'ref_partial',
            'status': 'success',
            'amount': 2.50,
            'original_transaction_id': 'txn_123',
            'message': 'Refund processed successfully'
        }
        
        success, message, refund_id = refund_late_fee_payment('txn_123', 2.50, mock_gateway)
        
        assert success is True
        assert refund_id == 'ref_partial'
        mock_gateway.process_refund.assert_called_once()


# Integration-style tests with more realistic mocking

class TestPaymentIntegration:
    
    
    def test_pay_and_refund_workflow(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        # First payment
        mock_gateway.process_payment.return_value = {
            'transaction_id': 'txn_workflow',
            'status': 'success',
            'amount': 7.50,
            'patron_id': '123456',
            'message': 'Payment processed successfully'
        }
        
        success, message, transaction_id = pay_late_fees('123456', 7.50, mock_gateway)
        assert success is True
        assert transaction_id == 'txn_workflow'
        
        # Then refund
        mock_gateway.process_refund.return_value = {
            'refund_id': 'ref_workflow',
            'status': 'success',
            'amount': 7.50,
            'original_transaction_id': transaction_id,
            'message': 'Refund processed successfully'
        }
        
        success, message, refund_id = refund_late_fee_payment(transaction_id, 7.50, mock_gateway)
        assert success is True
        assert refund_id == 'ref_workflow'
        
        # Verify both methods were called
        assert mock_gateway.process_payment.call_count == 1
        assert mock_gateway.process_refund.call_count == 1
    
    def test_multiple_payments_different_patrons(self):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Configure side_effect for multiple calls
        mock_gateway.process_payment.side_effect = [
            {
                'transaction_id': 'txn_001',
                'status': 'success',
                'amount': 3.00,
                'patron_id': '111111',
                'message': 'Payment processed successfully'
            },
            {
                'transaction_id': 'txn_002',
                'status': 'success',
                'amount': 5.50,
                'patron_id': '222222',
                'message': 'Payment processed successfully'
            },
            {
                'transaction_id': 'txn_003',
                'status': 'success',
                'amount': 1.00,
                'patron_id': '333333',
                'message': 'Payment processed successfully'
            }
        ]
        
        # Process three payments
        success1, msg1, txn1 = pay_late_fees('111111', 3.00, mock_gateway)
        success2, msg2, txn2 = pay_late_fees('222222', 5.50, mock_gateway)
        success3, msg3, txn3 = pay_late_fees('333333', 1.00, mock_gateway)
        
        assert all([success1, success2, success3])
        assert txn1 == 'txn_001'
        assert txn2 == 'txn_002'
        assert txn3 == 'txn_003'
        
        # Verify all calls were made
        assert mock_gateway.process_payment.call_count == 3


# ASSIGNMENT 3 REQUIREMENTS - Advanced Stubbing and Mocking Tests

class TestPayLateFees_Assignment3:
    
    
    def test_successful_payment_with_stubs_and_mocks(self, mocker):
        
        # STUBBING: Stub database functions with fake data (no verification needed)
        mocker.patch('services.library_service.calculate_late_fee_for_book', 
                    return_value={
                        'fee_amount': 5.00,
                        'days_overdue': 10,
                        'status': 'Overdue'
                    })
        
        mocker.patch('services.library_service.get_book_by_id',
                    return_value={
                        'id': 1,
                        'title': 'Test Book',
                        'author': 'Test Author'
                    })
        
        # MOCKING: Create mock PaymentGateway (verification required)
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = {
            'transaction_id': 'txn_success_001',
            'status': 'success',
            'amount': 5.00,
            'patron_id': '123456',
            'message': 'Payment processed successfully'
        }
        
        # Execute
        success, message, transaction_id = pay_late_fees('123456', 5.00, mock_gateway)
        
        # Assertions
        assert success is True
        assert 'successfully' in message.lower()
        assert transaction_id == 'txn_success_001'
        assert '$5.00' in message
        
        # MOCK VERIFICATION: Verify the mock was called with correct parameters
        mock_gateway.process_payment.assert_called_once_with(
            patron_id='123456',
            amount=5.00,
            description='Library late fees for patron 123456'
        )
    
    def test_payment_declined_by_gateway(self, mocker):
        
        # STUBBING: Stub database functions
        mocker.patch('services.library_service.calculate_late_fee_for_book',
                    return_value={'fee_amount': 3.50, 'days_overdue': 7, 'status': 'Overdue'})
        
        # MOCKING: Mock gateway to simulate declined payment
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = PaymentGatewayError("Card declined - insufficient funds")
        
        # Execute
        success, message, transaction_id = pay_late_fees('123456', 3.50, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'payment gateway error' in message.lower()
        assert 'card declined' in message.lower()
        assert transaction_id is None
        
        # MOCK VERIFICATION: Verify the mock was called despite failure
        mock_gateway.process_payment.assert_called_once()
    
    def test_invalid_patron_id_mock_not_called(self, mocker):
        
        # MOCKING: Create mock gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Execute with invalid patron ID (too short)
        success, message, transaction_id = pay_late_fees('12345', 5.00, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'invalid patron id' in message.lower()
        assert '6 digits' in message
        assert transaction_id is None
        
        # MOCK VERIFICATION: Gateway should NOT have been called for invalid input
        mock_gateway.process_payment.assert_not_called()
    
    def test_zero_late_fees_mock_not_called(self, mocker):
        
        # MOCKING: Create mock gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Execute with zero amount
        success, message, transaction_id = pay_late_fees('123456', 0, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'positive' in message.lower()
        assert transaction_id is None
        
        # MOCK VERIFICATION: Gateway should NOT have been called
        mock_gateway.process_payment.assert_not_called()
    
    def test_network_error_exception_handling(self, mocker):
        
        # STUBBING: Stub database functions
        mocker.patch('services.library_service.calculate_late_fee_for_book',
                    return_value={'fee_amount': 7.50, 'days_overdue': 15, 'status': 'Overdue'})
        
        # MOCKING: Mock gateway to simulate network error
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = Exception("Network timeout - unable to reach payment server")
        
        # Execute
        success, message, transaction_id = pay_late_fees('654321', 7.50, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'unexpected error' in message.lower()
        assert 'network timeout' in message.lower()
        assert transaction_id is None
        
        # MOCK VERIFICATION: Verify the mock was called before exception occurred
        mock_gateway.process_payment.assert_called_once_with(
            patron_id='654321',
            amount=7.50,
            description='Library late fees for patron 654321'
        )
    
    def test_invalid_patron_id_variations_mock_not_called(self, mocker):
        
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Test case 1: Patron ID too long
        success, msg, txn = pay_late_fees('1234567', 5.00, mock_gateway)
        assert success is False
        assert 'invalid patron id' in msg.lower()
        
        # Test case 2: Non-numeric patron ID
        success, msg, txn = pay_late_fees('12345a', 5.00, mock_gateway)
        assert success is False
        assert 'invalid patron id' in msg.lower()
        
        # Test case 3: Empty patron ID
        success, msg, txn = pay_late_fees('', 5.00, mock_gateway)
        assert success is False
        
        # MOCK VERIFICATION: Gateway should NEVER have been called
        mock_gateway.process_payment.assert_not_called()
        assert mock_gateway.process_payment.call_count == 0


class TestRefundLateFeePayment_Assignment3:
    
    
    def test_successful_refund(self, mocker):
        
        # MOCKING: Create mock PaymentGateway
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_refund.return_value = {
            'refund_id': 'ref_success_001',
            'status': 'success',
            'amount': 5.00,
            'original_transaction_id': 'txn_123456',
            'message': 'Refund processed successfully'
        }
        
        # Execute
        success, message, refund_id = refund_late_fee_payment('txn_123456', 5.00, mock_gateway)
        
        # Assertions
        assert success is True
        assert 'successfully' in message.lower()
        assert refund_id == 'ref_success_001'
        assert '$5.00' in message
        
        # MOCK VERIFICATION: Verify the mock was called with correct parameters
        mock_gateway.process_refund.assert_called_once_with(
            transaction_id='txn_123456',
            amount=5.00
        )
    
    def test_invalid_transaction_id_rejection_mock_not_called(self, mocker):
        
        # MOCKING: Create mock gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Test case 1: Empty transaction ID
        success, message, refund_id = refund_late_fee_payment('', 5.00, mock_gateway)
        assert success is False
        assert 'invalid transaction id' in message.lower()
        assert refund_id is None
        
        # Test case 2: None transaction ID
        success, message, refund_id = refund_late_fee_payment(None, 5.00, mock_gateway)
        assert success is False
        assert 'invalid transaction id' in message.lower()
        assert refund_id is None
        
        # MOCK VERIFICATION: Gateway should NOT have been called
        mock_gateway.process_refund.assert_not_called()
        assert mock_gateway.process_refund.call_count == 0
    
    def test_invalid_refund_amounts_negative(self, mocker):
        
        # MOCKING: Create mock gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Execute with negative amount
        success, message, refund_id = refund_late_fee_payment('txn_123', -5.00, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'positive' in message.lower()
        assert refund_id is None
        
        # MOCK VERIFICATION: Gateway should NOT have been called
        mock_gateway.process_refund.assert_not_called()
    
    def test_invalid_refund_amounts_zero(self, mocker):
        
        # MOCKING: Create mock gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Execute with zero amount
        success, message, refund_id = refund_late_fee_payment('txn_123', 0, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'positive' in message.lower()
        assert refund_id is None
        
        # MOCK VERIFICATION: Gateway should NOT have been called
        mock_gateway.process_refund.assert_not_called()
    
    def test_invalid_refund_amounts_exceeds_maximum(self, mocker):
        
        # MOCKING: Create mock gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Execute with amount exceeding maximum
        success, message, refund_id = refund_late_fee_payment('txn_123', 20.00, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'exceeds maximum' in message.lower()
        assert '$15.00' in message
        assert refund_id is None
        
        # MOCK VERIFICATION: Gateway should NOT have been called
        mock_gateway.process_refund.assert_not_called()
    
    def test_refund_transaction_not_found_error(self, mocker):
        
        # MOCKING: Mock gateway to simulate transaction not found
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_refund.side_effect = PaymentGatewayError("Transaction txn_notfound not found")
        
        # Execute
        success, message, refund_id = refund_late_fee_payment('txn_notfound', 5.00, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'payment gateway error' in message.lower()
        assert 'not found' in message.lower()
        assert refund_id is None
        
        # MOCK VERIFICATION: Verify the mock was called
        mock_gateway.process_refund.assert_called_once_with(
            transaction_id='txn_notfound',
            amount=5.00
        )
    
    def test_refund_amount_exceeds_original_transaction(self, mocker):
        
        # MOCKING: Mock gateway to simulate refund exceeding original
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_refund.side_effect = PaymentGatewayError(
            "Refund amount cannot exceed original transaction amount"
        )
        
        # Execute
        success, message, refund_id = refund_late_fee_payment('txn_123', 10.00, mock_gateway)
        
        # Assertions
        assert success is False
        assert 'payment gateway error' in message.lower()
        assert refund_id is None
        
        # MOCK VERIFICATION: Verify the mock was called
        mock_gateway.process_refund.assert_called_once()


# Advanced Stubbing and Mocking Scenarios

class TestAdvancedStubbingAndMocking:
    
    
    def test_stubs_vs_mocks_demonstration(self, mocker):
        
        # STUBBING: Database functions - no verification needed
        stub_calculate_fee = mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'fee_amount': 4.50, 'days_overdue': 9, 'status': 'Overdue'}
        )
        
        stub_get_book = mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={'id': 1, 'title': 'Mocking Guide', 'author': 'Test Author'}
        )
        
        # MOCKING: Payment gateway - verification required
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = {
            'transaction_id': 'txn_demo',
            'status': 'success',
            'amount': 4.50,
            'patron_id': '999999',
            'message': 'Payment processed successfully'
        }
        
        # Execute
        success, message, txn_id = pay_late_fees('999999', 4.50, mock_gateway)
        
        # Verify success
        assert success is True
        assert txn_id == 'txn_demo'
        
        # MOCK VERIFICATION (required for mocks)
        mock_gateway.process_payment.assert_called_once()
        
        # Note: Stubs don't need verification - they just provide data
        # We could verify stub calls, but it's not required for stubbing pattern
    
    def test_multiple_payment_attempts_mock_call_count(self, mocker):
        
        # STUBBING
        mocker.patch('services.library_service.calculate_late_fee_for_book',
                    return_value={'fee_amount': 2.00, 'days_overdue': 4, 'status': 'Overdue'})
        
        # MOCKING: Configure multiple return values
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = [
            {'transaction_id': 'txn_1', 'status': 'success', 'amount': 2.00, 'patron_id': '111111', 'message': 'OK'},
            {'transaction_id': 'txn_2', 'status': 'success', 'amount': 2.00, 'patron_id': '222222', 'message': 'OK'},
            {'transaction_id': 'txn_3', 'status': 'success', 'amount': 2.00, 'patron_id': '333333', 'message': 'OK'}
        ]
        
        # Execute multiple payments
        pay_late_fees('111111', 2.00, mock_gateway)
        pay_late_fees('222222', 2.00, mock_gateway)
        pay_late_fees('333333', 2.00, mock_gateway)
        
        # MOCK VERIFICATION: Verify call count
        assert mock_gateway.process_payment.call_count == 3
        
        # MOCK VERIFICATION: Verify specific calls
        expected_calls = [
            call(patron_id='111111', amount=2.00, description='Library late fees for patron 111111'),
            call(patron_id='222222', amount=2.00, description='Library late fees for patron 222222'),
            call(patron_id='333333', amount=2.00, description='Library late fees for patron 333333')
        ]
        mock_gateway.process_payment.assert_has_calls(expected_calls)
    
    def test_payment_retry_after_failure(self, mocker):
        
        # STUBBING
        mocker.patch('services.library_service.calculate_late_fee_for_book',
                    return_value={'fee_amount': 6.00, 'days_overdue': 12, 'status': 'Overdue'})
        
        # MOCKING: First call fails, second succeeds
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = [
            PaymentGatewayError("Temporary network error"),
            {'transaction_id': 'txn_retry', 'status': 'success', 'amount': 6.00, 
             'patron_id': '555555', 'message': 'Payment processed successfully'}
        ]
        
        # Execute: First attempt fails
        success1, msg1, txn1 = pay_late_fees('555555', 6.00, mock_gateway)
        assert success1 is False
        assert 'network error' in msg1.lower()
        
        # Execute: Retry succeeds
        success2, msg2, txn2 = pay_late_fees('555555', 6.00, mock_gateway)
        assert success2 is True
        assert txn2 == 'txn_retry'
        
        # MOCK VERIFICATION: Verify both calls were made
        assert mock_gateway.process_payment.call_count == 2

