"""Custom exception classes for the OCR service."""


class BaseException(Exception):
    """Base exception class for the application."""

    def __init__(self, message: str = "An error occurred") -> None:
        """Initialize base exception.

        Args:
            message: Error message.
        """
        self.message = message
        super().__init__(self.message)


class ValidationException(BaseException):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation error") -> None:
        """Initialize validation exception.

        Args:
            message: Validation error message.
        """
        super().__init__(message)


class RepositoryException(BaseException):
    """Exception raised for repository errors."""

    def __init__(self, message: str = "Repository error") -> None:
        """Initialize repository exception.

        Args:
            message: Repository error message.
        """
        super().__init__(message)


class ServiceException(BaseException):
    """Exception raised for service-level errors."""

    def __init__(self, message: str = "Service error") -> None:
        """Initialize service exception.

        Args:
            message: Service error message.
        """
        super().__init__(message)


class UseCaseException(BaseException):
    """Exception raised for use case errors."""

    def __init__(self, message: str = "Use case error") -> None:
        """Initialize use case exception.

        Args:
            message: Use case error message.
        """
        super().__init__(message)


class OCRException(BaseException):
    """Exception raised for OCR processing errors."""

    def __init__(self, message: str = "OCR processing error") -> None:
        """Initialize OCR exception.

        Args:
            message: OCR error message.
        """
        super().__init__(message)


class VLMError(Exception):
    """Base class for VLM errors."""


class VLMProcessingError(VLMError):
    """Error during VLM processing."""


class VLMValidationError(VLMError):
    """Error validating VLM response."""


class VLMConfigError(VLMError):
    """Error in VLM configuration."""
