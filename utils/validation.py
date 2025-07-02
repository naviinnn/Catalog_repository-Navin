# utils/validation.py

from datetime import datetime, date
from exception.catalog_exception import ValidationError

def validate_alphanumeric_string(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
    """Validates if a string is alphanumeric (allowing spaces and common punctuation) and within length limits."""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string.")
    
    stripped_value = value.strip()
    if not stripped_value:
        raise ValidationError(f"{field_name} cannot be empty.")
    
    if len(stripped_value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long.")
    
    if len(stripped_value) > max_length:
        raise ValidationError(f"{field_name} cannot exceed {max_length} characters.")
    
    # Allow letters, numbers, spaces, and common punctuation for descriptions/names
    # This regex allows alphanumeric, spaces, and basic punctuation like .,!?'"-
    if not all(c.isalnum() or c.isspace() or c in ".,!?'\"-" for c in stripped_value):
        # Refined error message to be more specific
        raise ValidationError(f"{field_name} contains invalid characters. Only alphanumeric, spaces, and basic punctuation (.,!?'\"-) are allowed.")
        
    return stripped_value

def validate_date(date_str: str, field_name: str) -> str:
    """Validates if a string is a valid date in `YYYY-MM-DD` format."""
    if not isinstance(date_str, str):
        raise ValidationError(f"{field_name} must be a string.")
    try:
        # Attempt to parse the date string
        datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_str
    except ValueError:
        raise ValidationError(f"{field_name} must be in `YYYY-MM-DD` format.")

def validate_future_date(date_str: str, field_name: str) -> str:
    """Validates if a date string is a valid date and not in the past."""
    valid_date_str = validate_date(date_str, field_name)
    input_date = datetime.strptime(valid_date_str, '%Y-%m-%d').date()
    
    # Get today's date without time component for accurate comparison
    today = date.today()

    if input_date < today:
        raise ValidationError(f"{field_name} cannot be in the past.")
    return valid_date_str

def validate_status(status: str) -> str:
    """Validates if the status is one of the allowed values."""
    if not isinstance(status, str):
        raise ValidationError("Status must be a string.")
    
    normalized_status = status.strip().lower()
    allowed_statuses = ['active', 'inactive'] # Updated allowed statuses
    
    if normalized_status not in allowed_statuses:
        raise ValidationError(f"Invalid status: '{status}'. Allowed values are {', '.join(allowed_statuses)}.")
    
    return normalized_status