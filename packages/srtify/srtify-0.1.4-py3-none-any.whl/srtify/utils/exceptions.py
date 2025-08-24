"""Exception classes for the application."""


class SrtifyException(Exception):
    """Base exception class for the application."""



class APIKeyError(SrtifyException):
    """Exception raised when the API key is invalid."""
