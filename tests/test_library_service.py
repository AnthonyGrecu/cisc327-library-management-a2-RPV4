import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import library_service

def test_add_book_valid(test_db):
    success, message = library_service.add_book_to_catalog("New Book", "New Author", "9999999999999", 2)
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_empty_title(test_db):
    success, message = library_service.add_book_to_catalog("", "Author", "9999999999999", 1)
    assert success == False
    assert "required" in message.lower()

def test_add_book_long_title(test_db):
    long_title = "x" * 201
    success, message = library_service.add_book_to_catalog(long_title, "Author", "9999999999999", 1)
    assert success == False
    assert "200" in message

def test_add_book_short_isbn(test_db):
    success, message = library_service.add_book_to_catalog("Title", "Author", "123", 1)
    assert success == False
    assert "13 digits" in message

def test_add_book_duplicate_isbn(test_db):
    success, message = library_service.add_book_to_catalog("Title", "Author", "1234567890123", 1)
    assert success == False
    assert "exists" in message.lower()

def test_borrow_book_valid(test_db):
    success, message = library_service.borrow_book_by_patron("123456", 1)
    assert success == True
    assert "borrowed" in message.lower()

def test_borrow_book_short_patron_id(test_db):
    success, message = library_service.borrow_book_by_patron("12345", 1)
    assert success == False
    assert "6 digits" in message

def test_borrow_book_long_patron_id(test_db):
    success, message = library_service.borrow_book_by_patron("1234567", 1)
    assert success == False
    assert "6 digits" in message

def test_borrow_book_nonexistent(test_db):
    success, message = library_service.borrow_book_by_patron("123456", 999)
    assert success == False
    assert "not found" in message.lower()

def test_borrow_book_unavailable(test_db):
    success, message = library_service.borrow_book_by_patron("123456", 2)
    assert success == False
    assert "not available" in message.lower()

def test_return_book_no_borrow_record(test_db):
    success, message = library_service.return_book_by_patron("123456", 1)
    assert success == False
    assert "no active borrow record" in message.lower()

def test_return_book_with_different_inputs(test_db):
    success1, message1 = library_service.return_book_by_patron("123456", 2)
    success2, message2 = library_service.return_book_by_patron("999999", 1)
    assert success1 == False
    assert success2 == False

def test_search_by_title(test_db):
    results = library_service.search_books_in_catalog("test", "title")
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_books_different_types(test_db):
    results1 = library_service.search_books_in_catalog("book", "title")
    results2 = library_service.search_books_in_catalog("author", "author")
    results3 = library_service.search_books_in_catalog("123", "isbn")
    assert all(isinstance(r, list) for r in [results1, results2, results3])

def test_patron_status_returns_empty(test_db):
    result = library_service.get_patron_status_report("123456")
    assert isinstance(result, dict)
    assert len(result) == 0

def test_patron_status_different_patrons(test_db):
    result1 = library_service.get_patron_status_report("123456")
    result2 = library_service.get_patron_status_report("999999")
    assert isinstance(result1, dict)
    assert isinstance(result2, dict)

def test_late_fee_basic(test_db):
    result = library_service.calculate_late_fee_for_book("123456", 1)
    assert result is not None
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result