"""
Basic unit of errorhub life...everything depends on this model
"""

from enum import Enum
from pydantic import BaseModel


class ErrorSeverity(str, Enum):
    """
    Represents the severity levels of errors.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EnvironmentEnum(str, Enum):
    """
    Represents the different environments in which the application can run.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ErrorDetail(BaseModel):
    """
    Represents the details of an error. Life of errohub library depends on this model.
    """

    service: str
    error_type: str
    code: int
    message: str
    timestamp: str
    trace_id: str | None = None
    severity: ErrorSeverity
    environment: EnvironmentEnum
    context: dict | None = None
