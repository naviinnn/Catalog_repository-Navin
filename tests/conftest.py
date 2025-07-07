import sys
import os

# Add the parent directory (project root) to sys.path so Python can find app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app  # Now this should work


import pytest
from app import app
from unittest.mock import patch

@pytest.fixture(scope='session')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def bypass_jwt_auth(monkeypatch):
    # Patch these functions globally during tests to bypass JWT auth
    monkeypatch.setattr('app.verify_jwt_in_request', lambda: None)
    monkeypatch.setattr('app.get_jwt_identity', lambda: 1)
