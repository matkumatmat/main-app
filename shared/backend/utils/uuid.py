from __future__ import annotations
from uuid_utils import uuid7
import uuid

def generateId() -> uuid.UUID:
    """
    Generate time-sortable UUID7.

    Benefits over UUID4:
    - Time-ordered (better B-tree index performance)
    - Chronologically sortable
    - Still globally unique
    - Better for distributed systems
    """
    return uuid7()

def parseId(id_string: str) -> uuid.UUID:
    """Parse string to UUID object with validation"""
    try:
        return uuid.UUID(id_string)
    except ValueError as e:
        raise ValueError(f"Invalid UUID format: {id_string}") from e

def isValidId(id_string: str) -> bool:
    """Check if string is valid UUID format"""
    try:
        uuid.UUID(id_string)
        return True
    except (ValueError, AttributeError, TypeError):
        return False
