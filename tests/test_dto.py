from datetime import datetime
import pytest
from dto.catalog import Catalog
from dto.user import User

# Tests for Catalog DTO
def test_catalog_dto_creation():
    catalog = Catalog(
        catalog_id=10,
        name='Summer Sale',
        description='Discounts on all summer items',
        start_date='2025-06-01',
        end_date='2025-06-30',
        status='active'
    )

    assert catalog.catalog_id == 10
    assert catalog.name == 'Summer Sale'
    assert catalog.description == 'Discounts on all summer items'
    assert catalog.start_date == '2025-06-01'
    assert catalog.end_date == '2025-06-30'
    assert catalog.status == 'active'

def test_catalog_to_dict():
    catalog = Catalog(
        catalog_id=5,
        name='Winter Deals',
        description='Clearance sale for winter',
        start_date='2025-12-01',
        end_date='2025-12-31',
        status='inactive'
    )
    expected = {
        'catalog_id': 5,
        'catalog_name': 'Winter Deals',
        'catalog_description': 'Clearance sale for winter',
        'start_date': '2025-12-01',
        'end_date': '2025-12-31',
        'status': 'inactive'
    }
    assert catalog.to_dict() == expected

# Tests for User DTO
def test_user_dto_creation():
    created = datetime(2025, 7, 7, 15, 30, 0)
    user = User(
        user_id=1,
        username='navin',
        password_hash='hashed_password',
        email='navin@example.com',
        created_at=created
    )

    assert user.user_id == 1
    assert user.username == 'navin'
    assert user.password_hash == 'hashed_password'
    assert user.email == 'navin@example.com'
    assert user.created_at == created

def test_user_to_dict_with_created_at():
    created = datetime(2025, 7, 7, 15, 30, 0)
    user = User(
        user_id=42,
        username='ajith',
        password_hash='pwdhash',
        email='ajith@example.com',
        created_at=created
    )
    expected = {
        "user_id": 42,
        "username": "ajith",
        "email": "ajith@example.com",
        "created_at": created.isoformat()
    }
    assert user.to_dict() == expected

def test_user_to_dict_without_created_at():
    user = User(
        user_id=99,
        username='testuser',
        password_hash='somehash',
        email='test@example.com',
        created_at=None
    )
    expected = {
        "user_id": 99,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": None
    }
    assert user.to_dict() == expected
