# Assignment 1 - Library Management System Analysis

**Name:** Anthony Grecu  
**Student ID:** 22RPV4  
**Group Number:** 2  
**Date:** September 23, 2025

## Function Implementation Status

| Function Name | Implementation Status | What is Missing (if any) |
|---------------|----------------------|---------------------------|
| `add_book_to_catalog()` | Complete | Working, adds books with validation |
| `borrow_book_by_patron()` | Complete | Working, borrows books with patron ID check |
| `return_book_by_patron()` | Partial | Says "not yet implemented", needs return logic |
| `calculate_late_fee_for_book()` | Partial | Function exists but no calculation logic |
| `search_books_in_catalog()` | Partial | Returns empty list, needs search implementation |
| `get_patron_status_report()` | Partial | Returns empty dict, needs status logic |
| `get_all_books()` | Complete | Gets all books from database |
| `get_book_by_id()` | Complete | Finds books by ID |
| `get_book_by_isbn()` | Complete | Finds books by ISBN |
| `insert_book()` | Complete | Adds new books to database |
| `update_book_availability()` | Complete | Updates book copies count |
| `catalog()` route | Complete | Shows all books on webpage |
| `add_book()` route | Complete | Web form for adding books |
| `borrow_book()` route | Complete | Web form for borrowing |
| `return_book()` route | Partial | Form exists but return function not working |
| `search_books()` route | Partial | Search page exists but no results |
| API endpoints | Partial | JSON endpoints exist but some functions incomplete |

## Summary

**Working Functions:** 11  
**Not Working/Incomplete:** 6  
**Total Functions:** 17

## What Still Needs to be Done

1. **Book Return (R4)** Need to implement returning books and updating availability
2. **Late Fee Calculation (R5)** Need to calculate fees for overdue books
3. **Book Search (R6)** Need to search by title, author, or ISBN
4. **Patron Status (R7)** Need to show what books a patron has borrowed and any fees owed

## Unit Test Scripts Summary

I wrote unit tests for the library system using pytest. The tests are in the `tests/` folder.

```bash
# Install pytest
pip install pytest pytest-flask

# Run all tests  
pytest tests/

# See more details
pytest tests/ -v
```

### Test Results
- **Total Tests:** 44 test cases
- **Functions Tested:** All database, business logic, and web functions
- **Requirements Coverage:** Tests for R1-R7 functionality
- **Pass/Fail:** 42 tests pass, 2 tests fail (revealing bugs in duplicate ISBN handling and late fee API)
