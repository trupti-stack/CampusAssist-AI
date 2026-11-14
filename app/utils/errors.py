from typing import Optional


class AppError(Exception):
    def __init__(self, status_code: int, error_type: str, message: str, headers: Optional[dict[str, str]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.headers = headers or {}


class LLMTimeoutError(Exception):
    pass


class LLMProviderError(Exception):
    pass


class ExternalAPITimeoutError(Exception):
    pass


class ExternalAPIError(Exception):
    pass
