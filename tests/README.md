# Unit Tests for Library Management System

This folder has tests for the library system functions.

## Files

- `conftest.py` - Test setup
- `test_database.py` - Tests for database functions  
- `test_library_service.py` - Tests for business logic
- `test_routes.py` - Tests for web pages
- `requirements_test.txt` - What to install for testing

## How to Run Tests

First install pytest:
```bash
pip install pytest pytest-flask
```

Run tests:
```bash
pytest tests/
```

Run with more details:
```bash  
pytest tests/ -v
```

## What the Tests Do

Each test file checks different parts:

- Database tests check if data is saved and retrieved correctly
- Service tests check the main functions like adding books and borrowing
- Route tests check if the web pages work

Each function has about 4-5 tests including good inputs and bad inputs.