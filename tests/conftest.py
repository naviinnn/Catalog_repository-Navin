import sys
import os
import pytest
import logging
from app import app

# Ensure app can be imported from the root directory when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def bypass_jwt_auth(monkeypatch):
    # Automatically mock JWT auth for all tests to bypass authentication
    monkeypatch.setattr('app.verify_jwt_in_request', lambda: None)
    monkeypatch.setattr('app.get_jwt_identity', lambda: 1)


@pytest.fixture(autouse=True)
def disable_logging():
    logging.disable(logging.CRITICAL)  
    yield
    logging.disable(logging.NOTSET) 
