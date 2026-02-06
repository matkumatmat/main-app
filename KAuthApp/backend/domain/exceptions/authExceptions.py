from shared.backend.exceptions.baseException import BaseServiceException

class AuthException(BaseServiceException):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message=message, status_code=status_code)

class UserAlreadyExistsException(AuthException):
    def __init__(self, email: str):
        super().__init__(f"User with email {email} already exists", 400)

class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__("Invalid email or password", 401)

class UserNotVerifiedException(AuthException):
    def __init__(self):
        super().__init__("Please verify your email before signing in", 403)

class InvalidOtpException(AuthException):
    def __init__(self):
        super().__init__("Invalid or expired OTP", 400)

class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__("Invalid token", 401)

class RateLimitException(AuthException):
    def __init__(self):
        super().__init__("Please wait 60 seconds before requesting another OTP", 429)
