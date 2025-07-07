import sys
import os
import pytest
from unittest.mock import patch
from app import app

# Ensure app can be imported from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def bypass_jwt_auth(monkeypatch):
    # Automatically mock JWT auth for all tests
    monkeypatch.setattr('app.verify_jwt_in_request', lambda: None)
    monkeypatch.setattr('app.get_jwt_identity', lambda: 1)
