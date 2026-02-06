from __future__ import annotations
import structlog
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("EmailService")

class MockEmailService:
    @staticmethod
    async def sendOtpEmail(email: str, otp: str):
        """
        Simulate sending an OTP email.
        In production, this would use an SMTP server or email provider.
        """
        logger.info(
            label="email_sent_mock",
            message=f"Sending OTP to {email}",
            recipient=email,
            otp_code=otp,  # Logged only for development/mock purposes
            environment="development"
        )
        # Simulate network delay if needed
        return True
