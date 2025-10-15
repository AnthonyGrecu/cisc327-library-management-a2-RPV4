# CISC 327 Library Management System - Assignment 2

[![Library Management Tests](https://github.com/YOUR_USERNAME/cisc327-library-management-a2-rpv4/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/cisc327-library-management-a2-rpv4/actions/workflows/tests.yml)

## Student Information
- **Name:** Anthony Grecu
- **Student ID:** 22RPV4
- **Course:** CISC 327 - Software Quality Assurance

## Project Overview
Flask-based Library Management System with SQLite database, implementing 7 functional requirements (R1-R7) with comprehensive test coverage.

## Requirements Implemented
- **R1:** Add Book To Catalog
- **R2:** Book Catalog Display
- **R3:** Book Borrowing Interface
- **R4:** Book Return Processing *(Assignment 2 - New)*
- **R5:** Late Fee Calculation API *(Assignment 2 - New)*
- **R6:** Book Search Functionality *(Assignment 2 - New)*
- **R7:** Patron Status Report *(Assignment 2 - New)*

## Test Suite
- **Total Tests:** 77 test cases
- **Manual Tests:** 44 tests (Assignment 1)
- **AI-Generated Tests:** 33 tests (Assignment 2 - using GitHub Copilot)
- **Test Coverage:** 88% line coverage, 82% branch coverage
- **All Tests Passing:** ✅

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/cisc327-library-management-a2-rpv4.git
cd cisc327-library-management-a2-rpv4

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
python app.py
```
Visit `http://localhost:5000` in your web browser.

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_library_service.py -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

## CI/CD Pipeline
This project uses GitHub Actions for automated testing. Every push to `main` branch triggers:
1. Python environment setup
2. Dependency installation
3. Full test suite execution
4. Test result reporting

See `.github/workflows/tests.yml` for workflow configuration.

## Project Structure
```
├── app.py                          # Flask application entry point
├── database.py                     # Database layer
├── library_service.py              # Business logic layer
├── routes/                         # Flask routes
│   ├── __init__.py
│   ├── api_routes.py
│   ├── borrowing_routes.py
│   ├── catalog_routes.py
│   └── search_routes.py
├── templates/                      # HTML templates
│   ├── base.html
│   ├── catalog.html
│   ├── add_book.html
│   ├── return_book.html
│   └── search.html
├── tests/                          # Test suite
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_library_service.py
│   ├── test_new_implementations.py
│   └── test_routes.py
├── .github/workflows/tests.yml     # CI/CD configuration
└── requirements.txt                # Python dependencies
```

## Assignment 2 Deliverables
1. ✅ Implementation of R4-R7 functions
2. ✅ 33 AI-generated test cases with documentation
3. ✅ Test comparison and analysis report
4. ✅ CI/CD pipeline with GitHub Actions
5. ✅ Complete documentation

## AI Tool Usage
This project used **GitHub Copilot** (approved by Queen's University) to generate test cases for newly implemented functions. See `Test_Comparison_Analysis.md` for detailed analysis of AI vs. manual test cases.

## License
Educational project for CISC 327 at Queen's University.
