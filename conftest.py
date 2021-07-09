import pytest
from app import app
from selenium import webdriver
import os

START_LINK = '127.0.0.1:5000'


@pytest.fixture(autouse=True, scope="function")
def go_to_home(browser):
    """go to the home page before each test case."""
    # app.run(debug=True)
    # browser.get(START_LINK)


@pytest.fixture(scope="session")
def browser():
    """Open the browser once for all tests."""
    try:
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        bro = webdriver.Chrome(options=options)
        bro.wait = 5
        bro.implicitly_wait(bro.wait)
        yield bro
    except Exception as ex:
        print(ex)
    finally:
        bro.quit()
