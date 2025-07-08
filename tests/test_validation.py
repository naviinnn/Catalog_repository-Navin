"""
Pytest tests for input validation utility functions.

Tests cover:
- Alphanumeric string validation (content, length, type)
- Date format and future date validation
- Status field validation (case-insensitive, allowed values)
- Appropriate error raising for invalid inputs
"""

import pytest
from datetime import date, timedelta
from utils.validation import (
    validate_alphanumeric_string,
    validate_date,
    validate_future_date,
    validate_status
)
from exception.catalog_exception import ValidationError

def test_validate_alphanumeric_string_valid():
    valid_str = "Hello World! This is a test - 123."
    assert validate_alphanumeric_string(valid_str, "TestField") == valid_str.strip()

def test_validate_alphanumeric_string_empty():
    with pytest.raises(ValidationError) as exc:
        validate_alphanumeric_string("   ", "TestField")
    assert "cannot be empty" in str(exc.value)

def test_validate_alphanumeric_string_invalid_chars():
    invalid_str = "Hello@World$"
    with pytest.raises(ValidationError) as exc:
        validate_alphanumeric_string(invalid_str, "TestField")
    assert "invalid characters" in str(exc.value)

def test_validate_alphanumeric_string_wrong_type():
    with pytest.raises(ValidationError) as exc:
        validate_alphanumeric_string(12345, "TestField")
    assert "must be a string" in str(exc.value)

def test_validate_alphanumeric_string_length_bounds():
    with pytest.raises(ValidationError):
        validate_alphanumeric_string("", "TestField")
    too_long = "a" * 256
    with pytest.raises(ValidationError):
        validate_alphanumeric_string(too_long, "TestField")
    valid_length = "a" * 10
    assert validate_alphanumeric_string(valid_length, "TestField") == valid_length

def test_validate_date_valid():
    valid_date = "2025-12-31"
    assert validate_date(valid_date, "StartDate") == valid_date

def test_validate_date_invalid_format():
    invalid_date = "31-12-2025"
    with pytest.raises(ValidationError) as exc:
        validate_date(invalid_date, "StartDate")
    assert "YYYY-MM-DD" in str(exc.value)

def test_validate_date_wrong_type():
    with pytest.raises(ValidationError):
        validate_date(20251231, "StartDate")

def test_validate_future_date_valid_today_or_later():
    today_str = date.today().strftime("%Y-%m-%d")
    assert validate_future_date(today_str, "StartDate") == today_str

    future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert validate_future_date(future_date, "StartDate") == future_date

def test_validate_future_date_past_date():
    past_date = "2000-01-01"
    with pytest.raises(ValidationError) as exc:
        validate_future_date(past_date, "StartDate")
    assert "cannot be in the past" in str(exc.value)

def test_validate_status_valid():
    assert validate_status("active") == "active"
    assert validate_status("Inactive") == "inactive"
    assert validate_status(" ACTIVE  ") == "active"

def test_validate_status_invalid():
    with pytest.raises(ValidationError) as exc:
        validate_status("pending")
    assert "Invalid status" in str(exc.value)

def test_validate_status_wrong_type():
    with pytest.raises(ValidationError):
        validate_status(123)
