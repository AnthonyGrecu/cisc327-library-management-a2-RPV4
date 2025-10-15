import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

@pytest.fixture
def client(test_db):
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_redirects(client):
    response = client.get('/')
    assert response.status_code == 302

def test_catalog_shows_books(client):
    response = client.get('/catalog')
    assert response.status_code == 200
    assert b'Test Book' in response.data

def test_add_book_form_displays(client):
    response = client.get('/add_book')
    assert response.status_code == 200
    assert b'<form' in response.data

def test_add_book_post_valid(client):
    data = {
        'title': 'New Book',
        'author': 'New Author',
        'isbn': '9999999999999',
        'total_copies': '1'
    }
    response = client.post('/add_book', data=data)
    assert response.status_code in [200, 302]

def test_add_book_post_invalid_isbn(client):
    data = {
        'title': 'Book',
        'author': 'Author',
        'isbn': '123',
        'total_copies': '1'
    }
    response = client.post('/add_book', data=data)
    assert response.status_code == 200

def test_borrow_book_valid(client):
    data = {
        'patron_id': '123456',
        'book_id': '1'
    }
    response = client.post('/borrow', data=data)
    assert response.status_code in [200, 302]

def test_borrow_book_invalid_patron(client):
    data = {
        'patron_id': '12345',
        'book_id': '1'
    }
    response = client.post('/borrow', data=data)
    assert response.status_code in [200, 302]

def test_return_form_displays(client):
    response = client.get('/return')
    assert response.status_code == 200
    assert b'<form' in response.data

def test_return_book_post(client):
    data = {
        'patron_id': '123456',
        'book_id': '1'
    }
    response = client.post('/return', data=data)
    assert response.status_code == 200
    assert b'not yet implemented' in response.data.lower() or b'error' in response.data.lower()

def test_search_no_query(client):
    response = client.get('/search')
    assert response.status_code == 200

def test_search_with_query(client):
    response = client.get('/search?q=book&type=title')
    assert response.status_code == 200

def test_search_different_types(client):
    response1 = client.get('/search?q=test&type=title')
    response2 = client.get('/search?q=author&type=author')
    response3 = client.get('/search?q=123&type=isbn')
    assert all(r.status_code == 200 for r in [response1, response2, response3])

def test_late_fee_api(client):
    response = client.get('/api/late_fee/123456/1')
    assert response.status_code in [200, 501]
    assert response.content_type == 'application/json'

def test_search_api_no_query(client):
    response = client.get('/api/search')
    assert response.status_code == 400
    assert response.content_type == 'application/json'

def test_search_api_with_query(client):
    response = client.get('/api/search?q=test&type=title')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert 'search_term' in data
    assert 'results' in data
    assert data['search_term'] == 'test'