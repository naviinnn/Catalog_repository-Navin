# dto/user.py

from datetime import datetime

class User:
    """
    Data Transfer Object (DTO) for a User entry.
    Encapsulates user properties for consistent data structure.
    """
    def __init__(self, username: str, password_hash: str, email: str, user_id: int = None, created_at: datetime = None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Converts the User object to a dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }