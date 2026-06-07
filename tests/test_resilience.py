import time
from unittest.mock import patch

import pytest

from api.resilience import ModuleTimeoutError, is_retryable_error, with_retry, with_timeout


def test_retry_succeeds_on_eventual_success():
    call_count = 0

    @with_retry(max_attempts=3, wait_min_seconds=1, wait_max_seconds=10)
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("transient")
        return "ok"

    with patch("time.sleep"):
        assert flaky() == "ok"
    assert call_count == 3


def test_retry_does_not_retry_non_transient_errors():
    call_count = 0

    @with_retry(max_attempts=3, wait_min_seconds=1, wait_max_seconds=10)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("permanent")

    with patch("time.sleep"):
        with pytest.raises(ValueError):
            always_fails()

    assert call_count == 1  # no retry on ValueError


def test_retry_raises_after_max_attempts():
    @with_retry(max_attempts=2, wait_min_seconds=1, wait_max_seconds=10)
    def always_transient():
        raise ConnectionError("always fails")

    with patch("time.sleep"):
        with pytest.raises(ConnectionError):
            always_transient()


def test_timeout_fires_when_exceeded():
    @with_timeout(seconds=1)
    def slow():
        time.sleep(2)

    with pytest.raises(ModuleTimeoutError):
        slow()


def test_timeout_does_not_fire_when_within_limit():
    @with_timeout(seconds=5)
    def fast():
        return "done"

    assert fast() == "done"


def test_is_retryable_error():
    assert is_retryable_error(ConnectionError())
    assert is_retryable_error(TimeoutError())
    assert not is_retryable_error(ValueError())
    assert not is_retryable_error(TypeError())
