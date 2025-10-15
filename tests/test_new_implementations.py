import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import library_service
import database
from datetime import datetime, timedelta

def test_return_book_valid(test_db):
    database.insert_borrow_record("123456", 1, datetime.now(), datetime.now() + timedelta(days=14))
    success, message = library_service.return_book_by_patron("123456", 1)
    assert success == True
    assert "returned successfully" in message.lower()

def test_return_book_invalid_patron_id_short(test_db):
    success, message = library_service.return_book_by_patron("12345", 1)
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_book_invalid_patron_id_long(test_db):
    success, message = library_service.return_book_by_patron("1234567", 1)
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_book_invalid_patron_id_non_numeric(test_db):
    success, message = library_service.return_book_by_patron("12345a", 1)
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_book_nonexistent_book(test_db):
    success, message = library_service.return_book_by_patron("123456", 999)
    assert success == False
    assert "not found" in message.lower()

def test_return_book_no_active_borrow(test_db):
    success, message = library_service.return_book_by_patron("999999", 1)
    assert success == False
    assert "no active borrow record" in message.lower()

def test_return_book_with_late_fee(test_db):
    past_date = datetime.now() - timedelta(days=20)
    due_date = past_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, past_date, due_date)
    success, message = library_service.return_book_by_patron("123456", 1)
    assert success == True
    assert "late fee" in message.lower()
    assert "$" in message

def test_return_book_on_time(test_db):
    borrow_date = datetime.now() - timedelta(days=10)
    due_date = borrow_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, borrow_date, due_date)
    success, message = library_service.return_book_by_patron("123456", 1)
    assert success == True
    assert "no late fees" in message.lower()

def test_calculate_late_fee_not_overdue(test_db):
    borrow_date = datetime.now() - timedelta(days=5)
    due_date = borrow_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, borrow_date, due_date)
    result = library_service.calculate_late_fee_for_book("123456", 1)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert result['status'] == 'Book not overdue'

def test_calculate_late_fee_overdue_within_7_days(test_db):
    past_date = datetime.now() - timedelta(days=18)
    due_date = past_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, past_date, due_date)
    result = library_service.calculate_late_fee_for_book("123456", 1)
    assert result['fee_amount'] == 2.00
    assert result['days_overdue'] == 4
    assert result['status'] == 'Overdue'

def test_calculate_late_fee_overdue_more_than_7_days(test_db):
    past_date = datetime.now() - timedelta(days=25)
    due_date = past_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, past_date, due_date)
    result = library_service.calculate_late_fee_for_book("123456", 1)
    assert result['fee_amount'] == 7.50
    assert result['days_overdue'] == 11
    assert result['status'] == 'Overdue'

def test_calculate_late_fee_maximum_cap(test_db):
    past_date = datetime.now() - timedelta(days=40)
    due_date = past_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, past_date, due_date)
    result = library_service.calculate_late_fee_for_book("123456", 1)
    assert result['fee_amount'] == 15.00
    assert result['days_overdue'] == 26

def test_calculate_late_fee_no_active_borrow(test_db):
    result = library_service.calculate_late_fee_for_book("999999", 1)
    assert result['fee_amount'] == 0.00
    assert result['status'] == 'No active borrow record found'

def test_search_books_by_title_exact(test_db):
    results = library_service.search_books_in_catalog("Test Book", "title")
    assert len(results) >= 1
    assert any(book['title'] == 'Test Book' for book in results)

def test_search_books_by_title_partial(test_db):
    results = library_service.search_books_in_catalog("test", "title")
    assert len(results) >= 1

def test_search_books_by_title_case_insensitive(test_db):
    results = library_service.search_books_in_catalog("TEST", "title")
    assert len(results) >= 1

def test_search_books_by_author_partial(test_db):
    results = library_service.search_books_in_catalog("Author", "author")
    assert len(results) >= 1

def test_search_books_by_author_case_insensitive(test_db):
    results = library_service.search_books_in_catalog("AUTHOR", "author")
    assert len(results) >= 1

def test_search_books_by_isbn_exact(test_db):
    results = library_service.search_books_in_catalog("1234567890123", "isbn")
    assert len(results) == 1
    assert results[0]['isbn'] == '1234567890123'

def test_search_books_empty_term(test_db):
    results = library_service.search_books_in_catalog("", "title")
    assert len(results) == 0

def test_search_books_no_results(test_db):
    results = library_service.search_books_in_catalog("NonexistentBook123", "title")
    assert len(results) == 0

def test_patron_status_valid_patron(test_db):
    status = library_service.get_patron_status_report("123456")
    assert 'error' not in status
    assert 'patron_id' in status
    assert status['patron_id'] == "123456"
    assert 'currently_borrowed' in status
    assert 'total_late_fees' in status

def test_patron_status_invalid_patron_id_short(test_db):
    status = library_service.get_patron_status_report("12345")
    assert 'error' in status

def test_patron_status_invalid_patron_id_long(test_db):
    status = library_service.get_patron_status_report("1234567")
    assert 'error' in status

def test_patron_status_invalid_patron_id_non_numeric(test_db):
    status = library_service.get_patron_status_report("12345a")
    assert 'error' in status

def test_patron_status_with_active_borrows(test_db):
    database.insert_borrow_record("123456", 1, datetime.now(), datetime.now() + timedelta(days=14))
    status = library_service.get_patron_status_report("123456")
    assert status['total_books_borrowed'] >= 1
    assert len(status['currently_borrowed']) >= 1

def test_patron_status_no_active_borrows(test_db):
    status = library_service.get_patron_status_report("999999")
    assert status['total_books_borrowed'] == 0
    assert len(status['currently_borrowed']) == 0

def test_patron_status_with_late_fees(test_db):
    past_date = datetime.now() - timedelta(days=20)
    due_date = past_date + timedelta(days=14)
    database.insert_borrow_record("123456", 1, past_date, due_date)
    status = library_service.get_patron_status_report("123456")
    assert status['total_late_fees'] > 0

def test_patron_status_borrowing_history(test_db):
    database.insert_borrow_record("123456", 1, datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=9))
    status = library_service.get_patron_status_report("123456")
    assert 'borrowing_history' in status
    assert len(status['borrowing_history']) >= 1
