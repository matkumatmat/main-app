from __future__ import annotations
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import re
from domain.exceptions.authenticationException import WeakPasswordException

class PasswordService:
    """
    Domain service for password operations.
    Uses Argon2id for secure password hashing.
    """

    PASSWORD_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )

    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=2,       # Number of iterations
            memory_cost=65536, # Memory usage in KiB (64MB)
            parallelism=1,     # Number of parallel threads
            hash_len=32,       # Hash output length in bytes
            salt_len=16        # Salt length in bytes
        )

    def validatePassword(self, password: str) -> None:
        """
        Validate password meets complexity requirements.
        Raises WeakPasswordException if validation fails.
        """
        if not self.PASSWORD_PATTERN.match(password):
            raise WeakPasswordException()

    def hashPassword(self, password: str) -> str:
        """
        Hash password using Argon2id after validation.
        Returns hashed password string.
        """
        self.validatePassword(password)
        return self.hasher.hash(password)

    def verifyPassword(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash.
        Returns True if password matches, False otherwise.
        """
        try:
            self.hasher.verify(hashed, password)

            # Check if rehashing needed (params changed)
            if self.hasher.check_needs_rehash(hashed):
                # Signal caller to rehash (return still True, but hash should be updated)
                pass

            return True
        except (VerifyMismatchError, InvalidHashError):
            return False
