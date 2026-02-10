from __future__ import annotations
from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from shared.backend.config.settings import settings
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KAuthentication")

class EmailService:
    """
    Domain service for sending emails.
    Uses aiosmtplib for async SMTP operations.
    """

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email

    async def sendVerificationEmail(
        self,
        to_email: str,
        username: str,
        verification_token: str
    ) -> None:
        """Send email verification link to user"""
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"

        subject = "Verify Your Email Address"
        html_body = f"""
        <html>
        <body>
            <h2>Welcome {username}!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <a href="{verification_url}">Verify Email</a>
            <p>This link expires in 24 hours.</p>
            <p>If you didn't create this account, please ignore this email.</p>
        </body>
        </html>
        """

        await self._sendEmail(to_email, subject, html_body)

    async def sendPasswordResetEmail(
        self,
        to_email: str,
        username: str,
        reset_token: str
    ) -> None:
        """Send password reset link to user"""
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

        subject = "Password Reset Request"
        html_body = f"""
        <html>
        <body>
            <h2>Hi {username},</h2>
            <p>We received a request to reset your password. Click the link below:</p>
            <a href="{reset_url}">Reset Password</a>
            <p>This link expires in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """

        await self._sendEmail(to_email, subject, html_body)

    async def _sendEmail(
        self,
        to_email: str,
        subject: str,
        html_body: str
    ) -> None:
        """Internal method to send email via SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

            async with SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)

            logger.info(
                "email_sent",
                to_email=to_email,
                subject=subject
            )
        except Exception as e:
            logger.error(
                "email_send_failed",
                exception=str(e),
                to_email=to_email
            )
            raise
