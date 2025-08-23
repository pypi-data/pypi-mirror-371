import time
import pytest

from mcp_long_context_reader.utils import timeout, TimeoutError


class TestTimeoutDecorator:
    def test_timeout_decorator_normal_execution(self):
        """Test that timeout decorator doesn't interfere with normal execution."""

        @timeout(5)
        def fast_function():
            return "completed"

        result = fast_function()
        assert result == "completed"

    def test_timeout_decorator_with_args(self):
        """Test that timeout decorator works with functions that have arguments."""

        @timeout(5)
        def add_numbers(a, b):
            return a + b

        result = add_numbers(2, 3)
        assert result == 5

    def test_timeout_decorator_raises_timeout_error(self):
        """Test that timeout decorator raises TimeoutError for slow functions."""

        @timeout(1)  # 1 second timeout
        def slow_function():
            time.sleep(2)  # Sleep for 2 seconds
            return "should not reach this"

        with pytest.raises(TimeoutError) as exc_info:
            slow_function()

        assert "timed out after 1 seconds" in str(exc_info.value)
        assert "slow_function" in str(exc_info.value)
        assert "should not reach this" not in str(exc_info.value)

    def test_timeout_decorator_preserves_function_metadata(self):
        """Test that timeout decorator preserves the original function's metadata."""

        @timeout(5)
        def documented_function():
            """This function has documentation."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This function has documentation."

    def test_timeout_custom_error_message(self):
        """Test that TimeoutError contains the correct function name and timeout value."""

        @timeout(2)
        def my_slow_function():
            time.sleep(3)
            return "done"

        with pytest.raises(TimeoutError) as exc_info:
            my_slow_function()

        error_message = str(exc_info.value)
        assert "my_slow_function" in error_message
        assert "2 seconds" in error_message

    def test_timeout_with_different_timeout_values(self):
        """Test timeout decorator with different timeout values."""

        @timeout(1)
        def short_timeout_function():
            time.sleep(1.5)
            return "done"

        @timeout(3)
        def long_timeout_function():
            time.sleep(1.5)
            return "done"

        # Short timeout should fail
        with pytest.raises(TimeoutError):
            short_timeout_function()

        # Long timeout should succeed
        result = long_timeout_function()
        assert result == "done"

    def test_timeout_with_exception_in_function(self):
        """Test that timeout decorator properly handles exceptions from the wrapped function."""

        @timeout(5)
        def function_with_error():
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError) as exc_info:
            function_with_error()

        assert str(exc_info.value) == "Something went wrong"
