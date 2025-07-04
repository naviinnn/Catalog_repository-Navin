from datetime import datetime, date
from exception.catalog_exception import ValidationError
from utils.logger import logger

def validate_alphanumeric_string(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
    """
    Validates an alphanumeric string with optional punctuation and length constraints.
    Logs and raises ValidationError on failure.
    """
    if not isinstance(value, str):
        logger.warning(f"{field_name} must be a string.")
        raise ValidationError(f"{field_name} must be a string.")
    
    value = value.strip()
    if not value:
        logger.warning(f"{field_name} cannot be empty.")
        raise ValidationError(f"{field_name} cannot be empty.")
    
    if not (min_length <= len(value) <= max_length):
        logger.warning(f"{field_name} length must be between {min_length} and {max_length}.")
        raise ValidationError(f"{field_name} must be between {min_length} and {max_length} characters.")

    allowed_chars = ".,!?'\"-"
    if not all(c.isalnum() or c.isspace() or c in allowed_chars for c in value):
        logger.warning(f"{field_name} contains invalid characters.")
        raise ValidationError(
            f"{field_name} contains invalid characters. Only alphanumeric, spaces, and basic punctuation (.,!?'\"-) are allowed."
        )

    return value

def validate_date(date_str: str, field_name: str) -> str:
    """
    Validates if the input string is a valid date in `YYYY-MM-DD` format.
    Logs and raises ValidationError on failure.
    """
    if not isinstance(date_str, str):
        logger.warning(f"{field_name} must be a string.")
        raise ValidationError(f"{field_name} must be a string.")

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        logger.warning(f"{field_name} is not in valid 'YYYY-MM-DD' format.")
        raise ValidationError(f"{field_name} must be in `YYYY-MM-DD` format.")

def validate_future_date(date_str: str, field_name: str) -> str:
    """
    Validates that the date is in `YYYY-MM-DD` format and not in the past.
    Logs and raises ValidationError if invalid or past date.
    """
    valid_date_str = validate_date(date_str, field_name)
    input_date = datetime.strptime(valid_date_str, '%Y-%m-%d').date()
    today = date.today()

    if input_date < today:
        logger.warning(f"{field_name} cannot be in the past.")
        raise ValidationError(f"{field_name} cannot be in the past.")

    return valid_date_str

def validate_status(status: str) -> str:
    """
    Validates if status is one of the allowed values: 'active', 'inactive'.
    Logs and raises ValidationError if not valid.
    """
    if not isinstance(status, str):
        logger.warning("Status must be a string.")
        raise ValidationError("Status must be a string.")

    normalized = status.strip().lower()
    allowed = ['active', 'inactive']

    if normalized not in allowed:
        logger.warning(f"Invalid status '{status}'. Allowed: {allowed}.")
        raise ValidationError(f"Invalid status: '{status}'. Allowed values are {', '.join(allowed)}.")

    return normalized
