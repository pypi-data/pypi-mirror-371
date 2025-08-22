"""
Retry configuration and exception handling for dotevals.

This module provides robust retry mechanisms that automatically discover
and handle connection errors from popular API clients and HTTP libraries.
It centralizes all retry logic to ensure consistent behavior across the
evaluation framework.
"""

from functools import lru_cache

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

# Default retry configuration constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # Initial delay in seconds
DEFAULT_MAX_DELAY = 30.0  # Maximum delay between retries


@lru_cache(maxsize=1)
def discover_connection_errors() -> tuple[type[Exception], ...]:
    """
    Dynamically discover connection exceptions from available libraries.

    This function attempts to import popular API client libraries and HTTP
    libraries to collect their connection-related exception classes. This
    allows the retry mechanism to handle these exceptions without requiring
    hard dependencies on the libraries.

    Returns:
        Tuple of exception classes that should be retried for connection issues

    Note:
        The discovered exceptions are cached using @lru_cache for performance.
    """

    # Base connection errors from Python standard library
    base_exceptions = [
        ConnectionError,
        ConnectionResetError,
        ConnectionAbortedError,
        ConnectionRefusedError,
        TimeoutError,
        OSError,
    ]

    api_exceptions = []

    try:
        import openai

        api_exceptions.extend(
            [
                openai.APIConnectionError,
                openai.APITimeoutError,
            ]
        )
    except ImportError:
        pass

    try:
        import anthropic

        api_exceptions.extend(
            [
                anthropic.APIConnectionError,
                anthropic.APITimeoutError,
            ]
        )
    except ImportError:
        pass

    try:
        import httpx

        api_exceptions.extend(
            [
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.ProxyError,
            ]
        )
    except ImportError:
        pass

    try:
        import requests  # type: ignore[import-untyped]

        api_exceptions.extend(
            [
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ProxyError,
                requests.exceptions.ChunkedEncodingError,
            ]
        )
    except ImportError:
        pass

    try:
        import urllib3

        api_exceptions.extend(
            [
                urllib3.exceptions.NewConnectionError,
                urllib3.exceptions.ConnectTimeoutError,
                urllib3.exceptions.ProxyError,
                urllib3.exceptions.MaxRetryError,
            ]
        )
    except ImportError:
        pass

    all_exceptions = tuple(base_exceptions + api_exceptions)

    return all_exceptions


def create_default_sync_retrying(
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = DEFAULT_RETRY_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    additional_exceptions: tuple[type[Exception], ...] | None = None,
) -> Retrying:
    """
    Create a default synchronous retry configuration for doteval.

    This creates a Retrying instance configured with sensible defaults for
    handling connection errors during evaluations.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 30.0)
        additional_exceptions: Additional exception types to retry beyond
                             the automatically discovered connection errors

    Returns:
        Configured Retrying instance for synchronous operations
    """
    connection_errors = discover_connection_errors()

    if additional_exceptions:
        connection_errors = connection_errors + additional_exceptions

    return Retrying(
        retry=retry_if_exception_type(connection_errors),
        stop=stop_after_attempt(
            max_retries + 1
        ),  # +1 because tenacity counts initial attempt
        wait=wait_exponential_jitter(initial=initial_delay, max=max_delay),
        reraise=True,
    )


def create_default_async_retrying(
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = DEFAULT_RETRY_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    additional_exceptions: tuple[type[Exception], ...] | None = None,
) -> AsyncRetrying:
    """
    Create a default asynchronous retry configuration for doteval.

    This creates an AsyncRetrying instance configured with sensible defaults for
    handling connection errors during async evaluations.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 30.0)
        additional_exceptions: Additional exception types to retry beyond
                             the automatically discovered connection errors

    Returns:
        Configured AsyncRetrying instance for asynchronous operations
    """
    connection_errors = discover_connection_errors()

    if additional_exceptions:
        connection_errors = connection_errors + additional_exceptions

    return AsyncRetrying(
        retry=retry_if_exception_type(connection_errors),
        stop=stop_after_attempt(
            max_retries + 1
        ),  # +1 because tenacity counts initial attempt
        wait=wait_exponential_jitter(initial=initial_delay, max=max_delay),
    )
