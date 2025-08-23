"""
PayPal SDK Exceptions

Custom exception classes for handling PayPal API errors.
"""

from typing import Optional, Dict, Any


class PayPalError(Exception):
    """Base exception for PayPal SDK errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        error_details: Optional[Dict[str, Any]] = None,
        debug_id: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_details = error_details or {}
        self.debug_id = debug_id
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.debug_id:
            return f"{self.message} (Debug ID: {self.debug_id})"
        return self.message


class PayPalAuthenticationError(PayPalError):
    """Raised when authentication fails."""
    pass


class PayPalValidationError(PayPalError):
    """Raised when request validation fails (400 errors)."""
    pass


class PayPalNotFoundError(PayPalError):
    """Raised when a resource is not found (404 errors)."""
    pass


class PayPalConflictError(PayPalError):
    """Raised when there's a conflict with the resource (409 errors)."""
    pass


class PayPalUnprocessableEntityError(PayPalError):
    """Raised when the request is semantically incorrect (422 errors)."""
    pass


class PayPalServerError(PayPalError):
    """Raised when PayPal server encounters an error (5xx errors)."""
    pass


class PayPalRateLimitError(PayPalError):
    """Raised when rate limits are exceeded."""
    pass


def create_paypal_error(
    status_code: int, 
    error_data: Dict[str, Any]
) -> PayPalError:
    """
    Create the appropriate PayPal error based on status code.
    
    Args:
        status_code: HTTP status code
        error_data: Error response data from PayPal
        
    Returns:
        Appropriate PayPalError subclass
    """
    message = error_data.get("message", "Unknown error")
    debug_id = error_data.get("debug_id")
    details = error_data.get("details", [])
    
    if status_code == 401:
        return PayPalAuthenticationError(message, status_code, {"details": details}, debug_id)
    elif status_code == 400:
        return PayPalValidationError(message, status_code, {"details": details}, debug_id)
    elif status_code == 404:
        return PayPalNotFoundError(message, status_code, {"details": details}, debug_id)
    elif status_code == 409:
        return PayPalConflictError(message, status_code, {"details": details}, debug_id)
    elif status_code == 422:
        return PayPalUnprocessableEntityError(message, status_code, {"details": details}, debug_id)
    elif status_code >= 500:
        return PayPalServerError(message, status_code, {"details": details}, debug_id)
    elif status_code == 429:
        return PayPalRateLimitError(message, status_code, {"details": details}, debug_id)
    else:
        return PayPalError(message, status_code, {"details": details}, debug_id)
