import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

def test_get_all_books(test_db):
    books = database.get_all_books()
    assert len(books) == 2
    assert books[0]['title'] == 'Another Book'

def test_get_all_books_empty(test_db):
    conn = database.get_db_connection()
    conn.execute('DELETE FROM books')
    conn.commit()
    conn.close()
    
    books = database.get_all_books()
    assert len(books) == 0

def test_get_book_by_id_exists(test_db):
    book = database.get_book_by_id(1)
    assert book is not None
    assert book['title'] == 'Test Book'

def test_get_book_by_id_not_exists(test_db):
    book = database.get_book_by_id(999)
    assert book is None

def test_get_book_by_isbn_exists(test_db):
    book = database.get_book_by_isbn('1234567890123')
    assert book is not None
    assert book['title'] == 'Test Book'

def test_get_book_by_isbn_not_exists(test_db):
    book = database.get_book_by_isbn('9999999999999')
    assert book is None

def test_get_patron_borrow_count_zero(test_db):
    count = database.get_patron_borrow_count('123456')
    assert count == 0

def test_get_patron_borrow_count_with_borrows(test_db):
    conn = database.get_db_connection()
    conn.execute("INSERT INTO borrow_records (patron_id, book_id, borrow_date, due_date) VALUES ('123456', 1, '2024-01-01', '2024-01-15')")
    conn.commit()
    conn.close()
    
    count = database.get_patron_borrow_count('123456')
    assert count == 1

def test_insert_book_success(test_db):
    success = database.insert_book('New Book', 'New Author', '3333333333333', 1, 1)
    assert success == True
    
    book = database.get_book_by_isbn('3333333333333')
    assert book['title'] == 'New Book'

def test_insert_book_duplicate_isbn(test_db):
    success = database.insert_book('Duplicate', 'Author', '1234567890123', 1, 1)
    assert success == False

def test_update_book_availability_increase(test_db):
    success = database.update_book_availability(1, 1)
    assert success == True
    
    book = database.get_book_by_id(1)
    assert book['available_copies'] == 3

def test_update_book_availability_decrease(test_db):
    success = database.update_book_availability(1, -1)
    assert success == True
    
    book = database.get_book_by_id(1)
    assert book['available_copies'] == 1