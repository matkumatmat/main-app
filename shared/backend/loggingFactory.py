from __future__ import annotations
import logging
import sys
import time
import traceback
from typing import Any
from contextlib import contextmanager
import structlog
from structlog.types import Processor
from shared.backend.config.settings import settings

def setupLogging() -> None:
    """
    Configure global structlog and standard logging.
    Call this once at application startup.
    """

    # 1. Define Shared Processors (for both JSON and Console)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars, # Bind request_id, etc.
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.processors.StackInfoRenderer(),
    ]

    # 2. Define Output Processors based on Environment
    if settings.log_format == "json":
        # Production / JSON Mode
        processors = shared_processors + [
            structlog.processors.dict_tracebacks, # Full stack trace in JSON
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development / Console Mode
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]

    # 3. Configure Structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 4. Configure Standard Library Logging (Interception)
    # Redirect standard logging (uvicorn, sqlalchemy) to structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.processors.dict_tracebacks if settings.log_format == "json" else structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level.upper())

    # Silencing noisy loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


class SystemLogger:
    """
    System logger with categorized subtypes:
    - Security: auth failures, brute force, violations
    - Application: business flow, info, debug
    - Performance: slow queries (>500ms), API response times
    - Error: exceptions with stack traces
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = structlog.get_logger().bind(
            category="system",
            service=service_name
        )

    def security(
        self,
        label: str,
        message: str,
        **context: Any
    ) -> None:
        """
        Log security events (auth failures, suspicious activity).

        Examples:
            - Failed login attempts
            - Brute force detection
            - Invalid token usage
            - Permission violations
        """
        self.logger.warning(
            message,
            type="security",
            label=label,
            **context
        )

    def application(
        self,
        label: str,
        message: str,
        level: str = "info",
        **context: Any
    ) -> None:
        """
        Log application business logic flow.

        Examples:
            - User registration flow
            - Payment processing steps
            - Feature flag changes
        """
        log_method = getattr(self.logger, level.lower())
        log_method(
            message,
            type="application",
            label=label,
            **context
        )

    def performance(
        self,
        label: str,
        duration_ms: float,
        threshold_ms: float = 500,
        **context: Any
    ) -> None:
        """
        Log slow operations exceeding threshold.

        Args:
            label: Operation identifier (e.g., "database_query", "api_call")
            duration_ms: Actual duration in milliseconds
            threshold_ms: Threshold for slow operation (default 500ms)
        """
        if duration_ms >= threshold_ms:
            self.logger.warning(
                f"Slow operation detected: {label}",
                type="performance",
                label=label,
                duration_ms=duration_ms,
                threshold_ms=threshold_ms,
                **context
            )

    def error(
        self,
        label: str,
        exception: Exception,
        message: str | None = None,
        **context: Any
    ) -> None:
        """
        Log exceptions with full context and stack trace.

        Args:
            label: Error identifier (e.g., "database_connection_failed")
            exception: The exception object
            message: Optional custom message (defaults to exception message)
            context: Additional context (user_id, request_id, etc.)
        """
        error_detail = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "stack_trace": traceback.format_exc(),
        }

        self.logger.error(
            message or str(exception),
            type="error",
            label=label,
            error_detail=error_detail,
            **context
        )

    @contextmanager
    def measurePerformance(self, label: str, threshold_ms: float = 500, **context: Any):
        """
        Context manager to measure operation duration.

        Usage:
            with logger.measurePerformance("database_query", user_id=123):
                result = await session.execute(query)
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.performance(label, duration_ms, threshold_ms, **context)


class UserLogger:
    """
    User audit logger for tracking user actions.
    IMMUTABLE logs for compliance and security.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = structlog.get_logger().bind(
            category="user",
            service=service_name,
            type="audit"
        )

    def audit(
        self,
        action: str,
        user_id: str,
        resource: str | None = None,
        **context: Any
    ) -> None:
        """
        Log user actions for audit trail.

        Args:
            action: Action performed (login, logout, create, update, delete)
            user_id: User identifier
            resource: Resource affected (e.g., "user:123", "payment:456")
            context: Additional data (ip_address, user_agent, changes, etc.)
        """
        self.logger.info(
            f"User {action}",
            action=action,
            user_id=user_id,
            resource=resource,
            **context
        )


class LoggerFactory:
    """
    Factory to create specific loggers with presets.
    """

    @staticmethod
    def getSystemLogger(service_name: str) -> SystemLogger:
        """
        Get system logger with categorized subtypes.

        Usage:
            logger = LoggerFactory.getSystemLogger("KAuthApp")
            logger.security("failed_login", "Invalid credentials", email="user@example.com")
            logger.error("db_error", exception, user_id="123")
        """
        return SystemLogger(service_name)

    @staticmethod
    def getUserLogger(service_name: str) -> UserLogger:
        """
        Get user audit logger.

        Usage:
            logger = LoggerFactory.getUserLogger("KAuthApp")
            logger.audit("login", user_id="123", ip_address="192.168.1.1")
        """
        return UserLogger(service_name)


def bindRequestContext(request_id: str, user_id: str | None = None, **context: Any) -> None:
    """
    Bind request context to all subsequent logs in this thread/task.

    Usage (in FastAPI middleware):
        bindRequestContext(
            request_id=request.state.request_id,
            user_id=current_user.id,
            ip_address=request.client.host
        )
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        user_id=user_id,
        **context
    )


def clearRequestContext() -> None:
    """
    Clear request context after request completes.
    Call this in middleware cleanup.
    """
    structlog.contextvars.clear_contextvars()


@contextmanager
def logRequestContext(request_id: str, user_id: str | None = None, **context: Any):
    """
    Context manager for request logging lifecycle.

    Usage:
        with logRequestContext(request_id="abc-123", user_id="user-456"):
            # All logs here will include request_id and user_id
            await process_request()
    """
    try:
        bindRequestContext(request_id, user_id, **context)
        yield
    finally:
        clearRequestContext()
