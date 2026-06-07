import functools
import logging
import signal
from collections.abc import Callable
from typing import TypeVar

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# before_sleep_log from tenacity requires a stdlib logger and an integer log level.
# structlog is used everywhere else; this logger is only for tenacity's callback.
_stdlib_logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)

# Exceptions that indicate a transient failure worth retrying.
# ConnectionError, TimeoutError are transient; ValueError, TypeError are not.
_TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def with_retry(
    max_attempts: int = 3,
    wait_min_seconds: float = 1.0,
    wait_max_seconds: float = 30.0,
    transient_exceptions: tuple = _TRANSIENT_EXCEPTIONS,
) -> Callable[[F], F]:
    """
    Decorator that retries on transient failures with exponential backoff.
    Logs each retry attempt as a warning including the exception and attempt number.
    Raises the original exception after all attempts are exhausted.

    Usage:
        @with_retry(max_attempts=3)
        def run(self, target_value, api_key):
            ...
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=1, min=wait_min_seconds, max=wait_max_seconds
        ),
        retry=retry_if_exception_type(transient_exceptions),
        before_sleep=before_sleep_log(_stdlib_logger, logging.WARNING),
        reraise=True,
    )


class ModuleTimeoutError(Exception):
    """Raised when a module exceeds its allotted execution time."""


def with_timeout(seconds: int) -> Callable[[F], F]:
    """
    Decorator that raises ModuleTimeoutError if the function takes longer
    than `seconds` to complete. Uses SIGALRM — Linux/macOS only.
    Only safe to use in the main thread; Celery workers run tasks in
    their own processes so this is always the main thread there.
    """
    def decorator(function: F) -> F:
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            def _handle_alarm(signum, frame):
                raise ModuleTimeoutError(
                    f"Module exceeded timeout of {seconds}s"
                )

            old_handler = signal.signal(signal.SIGALRM, _handle_alarm)
            signal.alarm(seconds)
            try:
                return function(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        return wrapper  # type: ignore[return-value]

    return decorator


def is_retryable_error(exception: BaseException) -> bool:
    """Returns True if the exception represents a transient failure."""
    return isinstance(exception, _TRANSIENT_EXCEPTIONS)
