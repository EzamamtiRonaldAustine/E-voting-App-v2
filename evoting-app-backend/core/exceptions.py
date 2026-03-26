"""Custom exception hierarchy for the e-voting backend.

This module defines domain-specific exceptions used across the
services, views, and serializers. All custom exceptions inherit
from EVotingException to support consistent catching and logging.
"""

from typing import Optional


class EVotingException(Exception):
    """Base exception for all custom e-voting errors.

    Attributes:
        message: Human-readable error message safe to return to API clients.
        code: Short machine-readable error code.
        details: Optional contextual information for logging and debugging.
    """

    def __init__(self, message: str = "", code: str = "EVOTING_ERROR", details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message or "An error occurred in the e-voting system."
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Serialize the exception to a simple dictionary for responses/logging."""

        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# Authentication-related exceptions


class AuthenticationException(EVotingException):
    """Base class for authentication failures."""


class InvalidCredentialsException(AuthenticationException):
    def __init__(self, message: str = "Username or password is incorrect", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="INVALID_CREDENTIALS", details=details)


class AccountDeactivatedException(AuthenticationException):
    def __init__(self, message: str = "Account has been deactivated", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="ACCOUNT_DEACTIVATED", details=details)


class AccountNotVerifiedException(AuthenticationException):
    def __init__(self, message: str = "Account has not been verified", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="ACCOUNT_NOT_VERIFIED", details=details)


# Validation-related exceptions


class ValidationException(EVotingException):
    """Base class for validation errors."""


class DuplicateRecordException(ValidationException):
    def __init__(self, message: str = "Duplicate record detected", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="DUPLICATE_RECORD", details=details)


class InvalidStateException(ValidationException):
    def __init__(self, message: str = "Invalid state for this operation", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="INVALID_STATE", details=details)


# Authorization-related exceptions


class AuthorizationException(EVotingException):
    """Base class for authorization/permission issues."""


class InsufficientPermissionsException(AuthorizationException):
    def __init__(self, message: str = "You do not have permission to perform this action", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="INSUFFICIENT_PERMISSIONS", details=details)


# Resource-related exceptions


class ResourceException(EVotingException):
    """Base class for resource-related problems (missing, conflict, etc.)."""


class ResourceNotFoundException(ResourceException):
    def __init__(self, message: str = "Requested resource was not found", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="RESOURCE_NOT_FOUND", details=details)


class ResourceConflictException(ResourceException):
    def __init__(self, message: str = "Conflict with existing resource", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="RESOURCE_CONFLICT", details=details)


# Business rule exceptions


class BusinessRuleException(EVotingException):
    """Base class for domain-specific business rule violations."""


class VoterAlreadyVotedException(BusinessRuleException):
    def __init__(self, message: str = "Voter has already cast a vote in this poll", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="VOTER_ALREADY_VOTED", details=details)


class PollNotOpenException(BusinessRuleException):
    def __init__(self, message: str = "This poll is not open", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="POLL_NOT_OPEN", details=details)


class InvalidElectionStateException(BusinessRuleException):
    def __init__(self, message: str = "Invalid election state for this action", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="INVALID_ELECTION_STATE", details=details)


# Database exceptions


class DatabaseException(EVotingException):
    """Base class for database or transaction failures."""


class DatabaseUnavailableException(DatabaseException):
    def __init__(self, message: str = "Database is currently unavailable", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="DATABASE_UNAVAILABLE", details=details)


class TransactionFailedException(DatabaseException):
    def __init__(self, message: str = "Database transaction failed", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="TRANSACTION_FAILED", details=details)


class SystemException(EVotingException):
    """Fallback exception for unexpected internal errors."""

    def __init__(self, message: str = "An internal server error occurred", details: Optional[dict] = None) -> None:
        super().__init__(message=message, code="INTERNAL_SERVER_ERROR", details=details)
