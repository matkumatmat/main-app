from __future__ import annotations
import hashlib
from fastapi import Header, HTTPException
from shared.backend.config.settings import settings
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")

async def verifyAdminHashKey(
    x_admin_key: str = Header(..., alias="X-Admin-Key")
) -> None:
    provided_hash = hashlib.sha256(x_admin_key.encode('utf-8')).hexdigest()

    if provided_hash != settings.admin_hash_key:
        logger.security(
            "admin_auth_failed",
            "Invalid admin authentication key provided",
            provided_hash_prefix=provided_hash[:16]
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid admin authentication key"
        )

    logger.application(
        "admin_auth_success",
        "Admin authenticated successfully",
        level="debug"
    )
