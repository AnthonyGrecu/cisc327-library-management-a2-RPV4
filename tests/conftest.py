import pytest
import sqlite3
import os

@pytest.fixture
def test_db():
    test_db_name = 'test_library.db'
    
    if os.path.exists(test_db_name):
        os.remove(test_db_name)
    
    conn = sqlite3.connect(test_db_name)
    
    conn.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            isbn TEXT,
            total_copies INTEGER,
            available_copies INTEGER
        )
    ''')
    
    conn.execute('''
        CREATE TABLE borrow_records (
            id INTEGER PRIMARY KEY,
            patron_id TEXT,
            book_id INTEGER,
            borrow_date TEXT,
            due_date TEXT,
            return_date TEXT
        )
    ''')
    
    conn.execute("INSERT INTO books VALUES (1, 'Test Book', 'Test Author', '1234567890123', 2, 2)")
    conn.execute("INSERT INTO books VALUES (2, 'Another Book', 'Another Author', '2234567890123', 1, 0)")
    
    conn.commit()
    conn.close()
    
    import database
    old_db = database.DATABASE
    database.DATABASE = test_db_name
    
    yield test_db_name
    
    database.DATABASE = old_db
    if os.path.exists(test_db_name):
        os.remove(test_db_name)