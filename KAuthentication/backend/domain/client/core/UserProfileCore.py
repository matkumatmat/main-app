from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING
import re

if TYPE_CHECKING:
    from uuid import UUID

@dataclass
class UserProfileDomain:
    sid : UUID
    username: str
    email: str
    password : str
    phone : str | None = None
    first_name : str | None = None
    last_name : str | None = None
    address : str | None = None
    region : str | None = None
    metadata_info : str | None = None
    devices : str | None = None
    status : str | None = None
    active: bool = False
    actived_at: datetime | None = None
    deleted: bool = False
    deleted_at: datetime | None = None

    def __post_init__(self):
        self.username = self.username.strip()
        self.validate_username()
        self.validate_password()

    def __bool__(self):
        return self.status == "active"
    
    def validate_username(self):
        if len(self.username) < 4:
            raise ValueError("Username too short (min 4 chars)")

    def validate_password(self):
        """
        Validate password meets strong security requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character (@$!%*?&)
        """
        if len(self.password) < 8:
            raise ValueError("Password too short (min 8 chars)")

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pattern, self.password):
            raise ValueError(
                "Password must contain at least: 1 uppercase, 1 lowercase, "
                "1 number, and 1 special character (@$!%*?&)"
            )
        
    def has_firstname(self) -> bool:
        return self.first_name is not None
    
    def has_lastname(self) -> bool:
        return self.last_name is not None
    
    def full_name(self) -> str:
        parts = [name for name in (self.first_name, self.last_name) if name]
        return " ".join(parts) if parts else self.username

    def has_email(self) -> bool:
        return bool(self.email)

    def has_phone(self) -> bool:
        return self.phone is not None

    def has_region(self) -> bool:
        return self.region is not None

    def mark_active(self, activate_time: datetime):
        self.active = True
        self.actived_at = activate_time

    def mark_deleted(self, deleted_time: datetime):
        self.deleted = True
        self.deleted_at = deleted_time
        self.active = False
