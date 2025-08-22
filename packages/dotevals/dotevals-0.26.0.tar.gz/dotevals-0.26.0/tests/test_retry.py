"""
Tests for the retry module.

This test suite covers all aspects of the retry functionality including:
- Exception discovery from various libraries
- Retry configuration creation
- Integration with tenacity
- Caching behavior
- Error handling scenarios
"""

import asyncio
from unittest.mock import Mock, patch

import pytest
from tenacity import AsyncRetrying, Retrying

from dotevals.retry import (
    DEFAULT_MAX_DELAY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    create_default_async_retrying,
    create_default_sync_retrying,
    discover_connection_errors,
)


class TestExceptionDiscovery:
    """Test the dynamic exception discovery functionality."""

    def setup_method(self):
        """Clear the exception cache before each test."""
        discover_connection_errors.cache_clear()

    def test_discover_base_exceptions(self):
        """Test that base Python connection exceptions are always included."""
        exceptions = discover_connection_errors()

        # Should always include standard library exceptions
        assert ConnectionError in exceptions
        assert ConnectionResetError in exceptions
        assert ConnectionAbortedError in exceptions
        assert ConnectionRefusedError in exceptions
        assert TimeoutError in exceptions
        assert OSError in exceptions

    def test_exception_caching(self):
        """Test that discovered exceptions are cached for performance."""
        # First call should discover and cache
        exceptions1 = discover_connection_errors()

        # Second call should return cached result
        exceptions2 = discover_connection_errors()

        # Should be the exact same tuple object (cached)
        assert exceptions1 is exceptions2

    def test_clear_exception_cache(self):
        """Test that clearing the cache forces rediscovery."""
        # Discover exceptions
        exceptions1 = discover_connection_errors()

        # Clear cache
        discover_connection_errors.cache_clear()

        # Rediscover - should be different object but same content
        exceptions2 = discover_connection_errors()

        assert exceptions1 is not exceptions2  # Different objects
        assert set(exceptions1) == set(exceptions2)  # Same content

    @patch.dict("sys.modules", {"openai": Mock()})
    def test_openai_exception_discovery(self):
        """Test discovery of OpenAI exceptions when library is available."""
        # Mock OpenAI exceptions
        mock_openai = Mock()
        mock_openai.APIConnectionError = type("APIConnectionError", (Exception,), {})
        mock_openai.APITimeoutError = type("APITimeoutError", (Exception,), {})

        with patch.dict("sys.modules", {"openai": mock_openai}):
            discover_connection_errors.cache_clear()
            exceptions = discover_connection_errors()

            assert mock_openai.APIConnectionError in exceptions
            assert mock_openai.APITimeoutError in exceptions

    @patch.dict("sys.modules", {"anthropic": Mock()})
    def test_anthropic_exception_discovery(self):
        """Test discovery of Anthropic exceptions when library is available."""
        # Mock Anthropic exceptions
        mock_anthropic = Mock()
        mock_anthropic.APIConnectionError = type("APIConnectionError", (Exception,), {})
        mock_anthropic.APITimeoutError = type("APITimeoutError", (Exception,), {})

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            discover_connection_errors.cache_clear()
            exceptions = discover_connection_errors()

            assert mock_anthropic.APIConnectionError in exceptions
            assert mock_anthropic.APITimeoutError in exceptions

    @patch.dict("sys.modules", {"httpx": Mock()})
    def test_httpx_exception_discovery(self):
        """Test discovery of httpx exceptions when library is available."""
        # Mock httpx exceptions
        mock_httpx = Mock()
        mock_httpx.ConnectError = type("ConnectError", (Exception,), {})
        mock_httpx.TimeoutException = type("TimeoutException", (Exception,), {})
        mock_httpx.NetworkError = type("NetworkError", (Exception,), {})
        mock_httpx.ProxyError = type("ProxyError", (Exception,), {})

        with patch.dict("sys.modules", {"httpx": mock_httpx}):
            discover_connection_errors.cache_clear()
            exceptions = discover_connection_errors()

            assert mock_httpx.ConnectError in exceptions
            assert mock_httpx.TimeoutException in exceptions
            assert mock_httpx.NetworkError in exceptions
            assert mock_httpx.ProxyError in exceptions

    @patch.dict("sys.modules", {"requests": Mock()})
    def test_requests_exception_discovery(self):
        """Test discovery of requests exceptions when library is available."""
        # Mock requests exceptions
        mock_requests = Mock()
        mock_requests.exceptions = Mock()
        mock_requests.exceptions.ConnectionError = type(
            "ConnectionError", (Exception,), {}
        )
        mock_requests.exceptions.Timeout = type("Timeout", (Exception,), {})
        mock_requests.exceptions.ProxyError = type("ProxyError", (Exception,), {})
        mock_requests.exceptions.ChunkedEncodingError = type(
            "ChunkedEncodingError", (Exception,), {}
        )

        with patch.dict("sys.modules", {"requests": mock_requests}):
            discover_connection_errors.cache_clear()
            exceptions = discover_connection_errors()

            assert mock_requests.exceptions.ConnectionError in exceptions
            assert mock_requests.exceptions.Timeout in exceptions
            assert mock_requests.exceptions.ProxyError in exceptions
            assert mock_requests.exceptions.ChunkedEncodingError in exceptions

    def test_connection_errors_module_constant(self):
        """Test that discovered connection errors are properly initialized."""
        # Should be a tuple of exception types
        connection_errors = discover_connection_errors()
        assert isinstance(connection_errors, tuple)
        assert all(issubclass(exc, Exception) for exc in connection_errors)

        # Should include base exceptions
        assert ConnectionError in connection_errors


class TestRetryConfiguration:
    """Test the retry configuration creation functions."""

    def test_create_default_sync_retrying(self):
        """Test creation of default synchronous retry configuration."""
        retrying = create_default_sync_retrying()

        assert isinstance(retrying, Retrying)
        # Should have reraise=True for sync retrying
        assert retrying.reraise is True

    def test_create_default_async_retrying(self):
        """Test creation of default asynchronous retry configuration."""
        retrying = create_default_async_retrying()

        assert isinstance(retrying, AsyncRetrying)

    def test_sync_retrying_custom_parameters(self):
        """Test sync retry creation with custom parameters."""
        retrying = create_default_sync_retrying(
            max_retries=5, initial_delay=2.0, max_delay=60.0
        )

        assert isinstance(retrying, Retrying)

        # Test that parameters are applied by checking stop condition
        # This is a bit tricky to test directly, so we'll test behavior
        assert retrying.stop.max_attempt_number == 6  # 5 retries + 1 initial attempt

    def test_async_retrying_custom_parameters(self):
        """Test async retry creation with custom parameters."""
        retrying = create_default_async_retrying(
            max_retries=5, initial_delay=2.0, max_delay=60.0
        )

        assert isinstance(retrying, AsyncRetrying)
        assert retrying.stop.max_attempt_number == 6  # 5 retries + 1 initial attempt

    def test_additional_exceptions_sync(self):
        """Test that additional exceptions can be added to sync retrying."""

        class CustomError(Exception):
            pass

        retrying = create_default_sync_retrying(additional_exceptions=(CustomError,))

        # Test that the custom exception is retried
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise CustomError("Test error")
            return "success"

        wrapped_function = retrying.wraps(failing_function)
        result = wrapped_function()

        assert result == "success"
        assert call_count == 3  # Initial call + 2 retries

    def test_additional_exceptions_async(self):
        """Test that additional exceptions can be added to async retrying."""

        class CustomError(Exception):
            pass

        retrying = create_default_async_retrying(additional_exceptions=(CustomError,))

        # Test that the custom exception is retried
        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise CustomError("Test error")
            return "success"

        async def test_async():
            wrapped_function = retrying.wraps(failing_function)
            result = await wrapped_function()
            assert result == "success"
            assert call_count == 3  # Initial call + 2 retries

        asyncio.run(test_async())


class TestRetryBehavior:
    """Test actual retry behavior with different exception types."""

    def test_sync_retry_on_connection_error(self):
        """Test that sync retrying handles ConnectionError."""
        retrying = create_default_sync_retrying(max_retries=2)

        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 1:  # Fail once, then succeed
                raise ConnectionError("Network error")
            return "success"

        wrapped_function = retrying.wraps(failing_function)
        result = wrapped_function()

        assert result == "success"
        assert call_count == 2  # Initial call + 1 retry

    def test_async_retry_on_timeout_error(self):
        """Test that async retrying handles TimeoutError."""
        retrying = create_default_async_retrying(max_retries=2)

        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 1:  # Fail once, then succeed
                raise TimeoutError("Request timeout")
            return "success"

        async def test_async():
            wrapped_function = retrying.wraps(failing_function)
            result = await wrapped_function()
            assert result == "success"
            assert call_count == 2  # Initial call + 1 retry

        asyncio.run(test_async())

    def test_sync_retry_exhaustion(self):
        """Test that sync retrying eventually gives up and raises the exception."""
        retrying = create_default_sync_retrying(max_retries=2)

        call_count = 0

        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent network error")

        wrapped_function = retrying.wraps(always_failing_function)

        with pytest.raises(ConnectionError, match="Persistent network error"):
            wrapped_function()

        assert call_count == 3  # Initial call + 2 retries

    def test_async_retry_exhaustion(self):
        """Test that async retrying eventually gives up and raises the exception."""
        retrying = create_default_async_retrying(max_retries=2)

        call_count = 0

        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise TimeoutError("Persistent timeout")

        async def test_async():
            wrapped_function = retrying.wraps(always_failing_function)

            with pytest.raises(Exception) as exc_info:
                await wrapped_function()

            # AsyncRetrying wraps the final exception in RetryError
            from tenacity import RetryError

            assert isinstance(exc_info.value, RetryError)
            assert call_count == 3  # Initial call + 2 retries

        asyncio.run(test_async())

    def test_non_retryable_exception_not_retried(self):
        """Test that non-connection exceptions are not retried."""
        retrying = create_default_sync_retrying(max_retries=2)

        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("This should not be retried")

        wrapped_function = retrying.wraps(failing_function)

        with pytest.raises(ValueError, match="This should not be retried"):
            wrapped_function()

        assert call_count == 1  # No retries for ValueError


class TestIntegration:
    """Integration tests to ensure the retry module works with real scenarios."""

    def test_module_constants_accessible(self):
        """Test that module constants are properly accessible."""
        assert DEFAULT_MAX_RETRIES == 3
        assert DEFAULT_RETRY_DELAY == 1.0
        assert DEFAULT_MAX_DELAY == 30.0

    def test_backward_compatibility(self):
        """Test that discover_connection_errors provides consistent exception discovery."""
        connection_errors = discover_connection_errors()

        assert isinstance(connection_errors, tuple)
        assert len(connection_errors) > 0
        assert all(issubclass(exc, Exception) for exc in connection_errors)
