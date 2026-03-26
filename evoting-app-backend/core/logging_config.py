"""Centralized logging configuration for the e-voting backend.

This module exposes a helper to obtain namespaced loggers with a
consistent JSON-style format. The actual LOGGING dict is defined
in Django settings, but this helper keeps logger creation in one
place and allows us to attach structured context information.
"""

import logging
from typing import Any, Dict, Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger instance using a consistent naming convention.

    Args:
        name: Optional logger name. If omitted, uses ``evoting``.

    Returns:
        Configured ``logging.Logger`` instance.
    """

    logger_name = name or "evoting"
    return logging.getLogger(logger_name)


def build_log_extra(
    *,
    correlation_id: Optional[str] = None,
    user_identifier: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a structured ``extra`` dict for log records.

    The ``extra`` dictionary is attached to log records so formatters
    can include rich contextual information (for example correlation
    IDs and user identifiers) without leaking sensitive data.
    """

    safe_context = context.copy() if context else {}
    # Ensure we never log raw passwords or similar secrets.
    for sensitive_key in {"password", "old_password", "new_password"}:
        if sensitive_key in safe_context:
            safe_context[sensitive_key] = "***REDACTED***"

    return {
        "correlation_id": correlation_id,
        "user_identifier": user_identifier,
        "context": safe_context,
    }
