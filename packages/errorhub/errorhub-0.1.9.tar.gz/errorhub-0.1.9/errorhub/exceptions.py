"""
All Custom exception you will need in your life
"""

from datetime import datetime, UTC
import uuid
import logging

from errorhub.models import ErrorDetail, ErrorSeverity, EnvironmentEnum


LOGGER = logging.getLogger(__name__)


class ErrorHubException(Exception):
    """
    Super Exception for all ErrorHub related errors.
    """

    def __init__(
        self,
        service: str,
        error_type: str,
        message: str,
        code: int = 500,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        environment: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT,
        trace_id: str | None = None,
        context: dict | None = None,
    ):
        """
        Super Exception Inherited by every custom Excetion in error hub
        """
        self.error_detail = ErrorDetail(
            service=service,
            error_type=error_type,
            message=message,
            code=code,
            severity=severity,
            environment=environment,
            trace_id=trace_id or str(uuid.uuid4()),
            timestamp=datetime.now(UTC).isoformat(),
            context=context,
        )
        super().__init__(message)
        self._log_error()

    def _log_error(self):
        if self.error_detail.severity == ErrorSeverity.HIGH:
            LOGGER.error("High Error occurred: %s", self.to_dict())
        elif self.error_detail.severity == ErrorSeverity.MEDIUM:
            LOGGER.warning("Medium Error occurred: %s", self.to_dict())
        else:
            LOGGER.info("Low Error occurred: %s", self.to_dict())

    def to_dict(self):
        """Return the structured error as a dictionary."""
        return self.error_detail.model_dump()

    def __str__(self):
        """
        String format of error in single line
        """
        return (
            f"[{self.error_detail.service}] {self.error_detail.error_type}:"
            f" {self.error_detail.code} | {self.error_detail.message}"
        )


class NotFoundException(ErrorHubException):
    """
    Exception raised when a requested resource is not found. 404
    """

    def __init__(self, service: str, message: str = "Resource not found", **kwargs):
        super().__init__(service=service, error_type="NotFound", message=message, code=404, **kwargs)


class UnauthorizedException(ErrorHubException):
    """
    Exception raised when a request is unauthorized. 401
    """

    def __init__(self, service: str, message: str = "Unauthorized", **kwargs):
        super().__init__(service=service, error_type="Unauthorized", message=message, code=401, **kwargs)


class BadRequestException(ErrorHubException):
    """
    Exception raised when a request is invalid. 400
    """

    def __init__(self, service: str, message: str = "Bad request", **kwargs):
        super().__init__(service=service, error_type="BadRequest", message=message, code=400, **kwargs)


class InternalServerErrorException(ErrorHubException):
    """
    Exception raised when an internal server error occurs. 500
    """

    def __init__(self, service: str, message: str = "Internal server error", **kwargs):
        super().__init__(service=service, error_type="InternalServerError", message=message, code=500, **kwargs)


class ForbiddenException(ErrorHubException):
    """
    Exception raised when a request is forbidden. 403
    """

    def __init__(self, service: str, message: str = "Forbidden", **kwargs):
        super().__init__(service=service, error_type="Forbidden", message=message, code=403, **kwargs)


class ConflictException(ErrorHubException):
    """
    Exception raised when a request conflicts with the current state. 409
    """

    def __init__(self, service: str, message: str = "Conflict", **kwargs):
        super().__init__(service=service, error_type="Conflict", message=message, code=409, **kwargs)


class UnprocessableEntityException(ErrorHubException):
    """
    Exception raised when a request is unprocessable. 422
    """

    def __init__(self, service: str, message: str = "Unprocessable entity", **kwargs):
        super().__init__(service=service, error_type="UnprocessableEntity", message=message, code=422, **kwargs)


class ServiceUnavailableException(ErrorHubException):
    """
    Exception raised when a service is unavailable. 503
    """

    def __init__(self, service: str, message: str = "Service unavailable", **kwargs):
        super().__init__(service=service, error_type="ServiceUnavailable", message=message, code=503, **kwargs)


class GatewayTimeoutException(ErrorHubException):
    """
    Exception raised when a gateway timeout occurs. 504
    """

    def __init__(self, service: str, message: str = "Gateway timeout", **kwargs):
        super().__init__(service=service, error_type="GatewayTimeout", message=message, code=504, **kwargs)
