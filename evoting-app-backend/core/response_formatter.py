"""Helpers for building consistent API responses.

The views will use these helpers so that both success and error
responses follow a predictable structure, which is useful for
front-end consumers and for documentation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .exceptions import EVotingException


def success_response(data: Any, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Wrap successful payloads in a common structure."""

    return {
        "success": True,
        "data": data,
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def error_response_from_exception(
    exc: EVotingException,
    *,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a standardized error response from a custom exception."""

    error_dict = exc.to_dict()
    return {
        "success": False,
        "error": {
            "code": error_dict["code"],
            "message": error_dict["message"],
            "details": error_dict.get("details") or {},
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
