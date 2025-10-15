"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_db_connection
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4: Book Return Processing
    """
    if not patron_id or len(patron_id) != 6 or not patron_id.isdigit():
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, f"Book with ID {book_id} not found."
    
    conn = get_db_connection()
    borrow_record = conn.execute(
        'SELECT * FROM borrow_records WHERE patron_id = ? AND book_id = ? AND return_date IS NULL',
        (patron_id, book_id)
    ).fetchone()
    conn.close()
    
    if not borrow_record:
        return False, f"No active borrow record found for patron {patron_id} and book ID {book_id}."
    
    return_date = datetime.now()
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE borrow_records SET return_date = ? WHERE patron_id = ? AND book_id = ? AND return_date IS NULL',
        (return_date.strftime('%Y-%m-%d'), patron_id, book_id)
    )
    conn.commit()
    conn.close()
    
    update_book_availability(book_id, 1)
    
    due_date_str = borrow_record['due_date'].split('T')[0] if 'T' in borrow_record['due_date'] else borrow_record['due_date']
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    days_late = (return_date - due_date).days
    
    if days_late > 0:
        if days_late <= 7:
            late_fee = days_late * 0.50
        else:
            late_fee = (7 * 0.50) + ((days_late - 7) * 1.00)
        late_fee = min(late_fee, 15.00)
        return True, f'Book returned successfully. Late fee: ${late_fee:.2f} ({days_late} days overdue).'
    else:
        return True, f'Book returned successfully. No late fees.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5: Late Fee Calculation API
    """
    conn = get_db_connection()
    borrow_record = conn.execute(
        'SELECT * FROM borrow_records WHERE patron_id = ? AND book_id = ? AND return_date IS NULL',
        (patron_id, book_id)
    ).fetchone()
    conn.close()
    
    if not borrow_record:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No active borrow record found'
        }
    
    due_date_str = borrow_record['due_date'].split('T')[0] if 'T' in borrow_record['due_date'] else borrow_record['due_date']
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
    current_date = datetime.now()
    days_overdue = (current_date - due_date).days
    
    if days_overdue <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not overdue'
        }
    
    if days_overdue <= 7:
        fee_amount = days_overdue * 0.50
    else:
        fee_amount = (7 * 0.50) + ((days_overdue - 7) * 1.00)
    
    fee_amount = min(fee_amount, 15.00)
    
    return {
        'fee_amount': round(fee_amount, 2),
        'days_overdue': days_overdue,
        'status': 'Overdue'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6: Book Search Functionality
    """
    if not search_term:
        return []
    
    conn = get_db_connection()
    
    if search_type == 'isbn':
        books = conn.execute(
            'SELECT * FROM books WHERE isbn = ?',
            (search_term,)
        ).fetchall()
    elif search_type == 'author':
        books = conn.execute(
            'SELECT * FROM books WHERE LOWER(author) LIKE LOWER(?)',
            (f'%{search_term}%',)
        ).fetchall()
    else:
        books = conn.execute(
            'SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?)',
            (f'%{search_term}%',)
        ).fetchall()
    
    conn.close()
    
    return [dict(book) for book in books]

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7: Patron Status Report
    """
    if not patron_id or len(patron_id) != 6 or not patron_id.isdigit():
        return {'error': 'Invalid patron ID'}
    
    conn = get_db_connection()
    
    active_borrows = conn.execute(
        '''SELECT br.*, b.title, b.author, b.isbn 
           FROM borrow_records br
           JOIN books b ON br.book_id = b.id
           WHERE br.patron_id = ? AND br.return_date IS NULL''',
        (patron_id,)
    ).fetchall()
    
    all_borrows = conn.execute(
        '''SELECT br.*, b.title, b.author 
           FROM borrow_records br
           JOIN books b ON br.book_id = b.id
           WHERE br.patron_id = ?
           ORDER BY br.borrow_date DESC''',
        (patron_id,)
    ).fetchall()
    
    conn.close()
    
    total_late_fees = 0.0
    currently_borrowed = []
    
    for record in active_borrows:
        due_date_str = record['due_date'].split('T')[0] if 'T' in record['due_date'] else record['due_date']
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        current_date = datetime.now()
        days_overdue = (current_date - due_date).days
        
        late_fee = 0.0
        if days_overdue > 0:
            if days_overdue <= 7:
                late_fee = days_overdue * 0.50
            else:
                late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
            late_fee = min(late_fee, 15.00)
            total_late_fees += late_fee
        
        currently_borrowed.append({
            'book_id': record['book_id'],
            'title': record['title'],
            'author': record['author'],
            'isbn': record['isbn'],
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date'],
            'days_overdue': max(0, days_overdue),
            'late_fee': round(late_fee, 2)
        })
    
    borrowing_history = []
    for record in all_borrows:
        borrowing_history.append({
            'book_id': record['book_id'],
            'title': record['title'],
            'author': record['author'],
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date'],
            'return_date': record['return_date'] if record['return_date'] else 'Not returned'
        })
    
    return {
        'patron_id': patron_id,
        'currently_borrowed': currently_borrowed,
        'total_books_borrowed': len(currently_borrowed),
        'total_late_fees': round(total_late_fees, 2),
        'borrowing_history': borrowing_history
    }
