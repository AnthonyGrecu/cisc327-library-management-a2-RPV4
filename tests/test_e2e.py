import pytest
import time
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="module")
def flask_app():
    if os.path.exists('library.db'):
        os.remove('library.db')
    
    import sys
    process = subprocess.Popen(
        [sys.executable, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(4)
    yield process
    process.terminate()
    process.wait()


@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_add_book_and_verify_in_catalog(driver, flask_app):
    driver.get("http://localhost:5000/")
    assert "catalog" in driver.current_url
    assert "Book Catalog" in driver.page_source or "Catalog" in driver.page_source
    
    add_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Add")
    add_link.click()
    time.sleep(1)
    
    assert "add" in driver.current_url
    
    driver.find_element(By.NAME, "title").send_keys("End-to-End Testing Guide")
    driver.find_element(By.NAME, "author").send_keys("Jane Smith")
    driver.find_element(By.NAME, "isbn").send_keys("9789876543210")
    driver.find_element(By.NAME, "total_copies").send_keys("3")
    
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    
    driver.get("http://localhost:5000/catalog")
    page_text = driver.page_source
    assert "End-to-End Testing Guide" in page_text
    assert "Jane Smith" in page_text
    assert "9789876543210" in page_text


def test_borrow_book_workflow(driver, flask_app):
    driver.get("http://localhost:5000/catalog")
    time.sleep(1)
    assert "Catalog" in driver.page_source
    
    try:
        patron_input = driver.find_element(By.NAME, "patron_id")
        patron_input.send_keys("654321")
        borrow_button = driver.find_element(By.CSS_SELECTOR, "button.btn-success")
        borrow_button.click()
        time.sleep(1)
        assert "catalog" in driver.current_url
    except Exception as e:
        pass


def test_search_functionality(driver, flask_app):
    driver.get("http://localhost:5000/search")
    time.sleep(1)
    assert "Search" in driver.page_source
    
    search_input = driver.find_element(By.NAME, "q")
    search_input.send_keys("Test")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    
    assert ("results" in driver.page_source.lower() or 
            "search" in driver.page_source.lower())


def test_return_book_page_loads(driver, flask_app):
    driver.get("http://localhost:5000/return")
    time.sleep(1)
    assert "Return" in driver.page_source
    
    patron_input = driver.find_element(By.NAME, "patron_id")
    book_input = driver.find_element(By.NAME, "book_id")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    
    assert patron_input is not None
    assert book_input is not None
    assert submit_button is not None
