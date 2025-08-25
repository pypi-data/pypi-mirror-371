"""
Custom exceptions for the Proof-of-Intent SDK.
"""

from typing import Optional


class PoIError(Exception):
    """Base exception for all PoI-related errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PoIValidationError(PoIError):
    """Raised when PoI receipt validation fails."""
    
    def __init__(self, message: str, receipt_id: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.receipt_id = receipt_id


class PoIGenerationError(PoIError):
    """Raised when PoI receipt generation fails."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, details)


class PoICryptographicError(PoIError):
    """Raised when cryptographic operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.operation = operation


class PoIConfigurationError(PoIError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.config_key = config_key


class PoIExpirationError(PoIError):
    """Raised when a PoI receipt has expired."""
    
    def __init__(self, message: str, receipt_id: str, expiration_time: str, details: Optional[dict] = None):
        super().__init__(message, details)
        self.receipt_id = receipt_id
        self.expiration_time = expiration_time


class PoISignatureError(PoIError):
    """Raised when signature verification fails."""
    
    def __init__(self, message: str, receipt_id: str, signature: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.receipt_id = receipt_id
        self.signature = signature
