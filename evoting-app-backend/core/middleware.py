"""Middleware for request/response logging and correlation IDs."""

import logging
import time
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

from .logging_config import build_log_extra, get_logger


class RequestLoggingMiddleware:
    """Log basic request/response data with a correlation ID.

    This middleware is deliberately conservative to avoid logging
    sensitive payloads while still providing useful diagnostics.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self.logger = get_logger("evoting.request")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        correlation_id = request.headers.get("X-Correlation-ID") or uuid.uuid4().hex
        request.correlation_id = correlation_id  # type: ignore[attr-defined]

        user_identifier = getattr(request.user, "username", None) or "anonymous"
        start_time = time.monotonic()

        self.logger.info(
            "Incoming request %s %s",
            request.method,
            request.path,
            extra=build_log_extra(
                correlation_id=correlation_id,
                user_identifier=user_identifier,
                context={"remote_addr": request.META.get("REMOTE_ADDR")},
            ),
        )

        response = self.get_response(request)

        elapsed_ms = (time.monotonic() - start_time) * 1000
        self.logger.info(
            "Response %s %s (%s) in %.2f ms",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            extra=build_log_extra(
                correlation_id=correlation_id,
                user_identifier=user_identifier,
                context={"elapsed_ms": elapsed_ms},
            ),
        )

        response["X-Correlation-ID"] = correlation_id
        return response
