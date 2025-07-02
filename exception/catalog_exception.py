# exception/catalog_exception.py

class CatalogError(Exception):
    """Base exception for catalog-related errors."""
    pass

class ValidationError(CatalogError):
    """Exception raised for invalid input data."""
    pass

class DataNotFoundError(CatalogError):
    """Exception raised when requested data is not found."""
    pass

class DatabaseConnectionError(CatalogError):
    """Exception raised for database connection or operation errors."""
    pass

class AuthenticationError(CatalogError):
    """Exception raised for authentication failures."""
    pass