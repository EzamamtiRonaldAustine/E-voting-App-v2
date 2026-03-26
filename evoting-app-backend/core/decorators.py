"""Reusable decorators for logging and exception handling.

These decorators are intentionally lightweight so that they can be
applied to service and view methods without changing their public
interfaces. They delegate to the logging and exceptions modules
for the actual behaviour.
"""

import functools
import logging
import time
from typing import Any, Callable, TypeVar, cast

from .exceptions import EVotingException, SystemException
from .logging_config import build_log_extra, get_logger


_F = TypeVar("_F", bound=Callable[..., Any])


def log_method_execution(logger_name: str) -> Callable[[_F], _F]:
    """Decorator that logs method entry, exit, and execution time.

    Args:
        logger_name: Name of the logger to use.
    """

    def decorator(func: _F) -> _F:
        logger = get_logger(logger_name)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.monotonic()
            logger.debug(
                "Entering %s", func.__qualname__, extra=build_log_extra(context={"args": str(args[1:]), "kwargs": kwargs})
            )
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                logger.debug(
                    "Exiting %s (%.2f ms)",
                    func.__qualname__,
                    elapsed_ms,
                    extra=build_log_extra(context={"elapsed_ms": elapsed_ms}),
                )
                return result
            except Exception:
                # Allow exception handlers or the caller to decide how to handle.
                logger.exception("Unhandled exception in %s", func.__qualname__)
                raise

        return cast(_F, wrapper)

    return decorator


def handle_exceptions(logger_name: str) -> Callable[[_F], _F]:
    """Decorator that converts unexpected exceptions to ``SystemException``.

    Known ``EVotingException`` instances are simply re-raised so that
    views can map them to HTTP responses. All other exceptions are
    logged with a stack trace and wrapped.
    """

    def decorator(func: _F) -> _F:
        logger = get_logger(logger_name)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except EVotingException:
                # Domain exceptions are already meaningful and logged at source.
                raise
            except Exception as exc:  # pragma: no cover - defensive
                logger.error(
                    "Unexpected error in %s: %s",
                    func.__qualname__,
                    exc,
                    exc_info=True,
                )
                raise SystemException() from exc

        return cast(_F, wrapper)

    return decorator
