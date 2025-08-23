"""
Custom exceptions for Polaris CLI
"""


class PolarisError(Exception):
    """Base exception for all Polaris CLI errors."""
    pass


class AuthenticationError(PolarisError):
    """Raised when authentication fails."""
    pass


class ConfigurationError(PolarisError):
    """Raised when there's a configuration issue."""
    pass


class APIError(PolarisError):
    """Raised when API calls fail."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ResourceNotFoundError(PolarisError):
    """Raised when a resource is not found."""
    pass


class ValidationError(PolarisError):
    """Raised when input validation fails."""
    pass
