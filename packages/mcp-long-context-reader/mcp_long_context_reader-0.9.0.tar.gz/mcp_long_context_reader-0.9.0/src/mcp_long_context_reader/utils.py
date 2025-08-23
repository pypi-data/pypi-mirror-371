import signal
import functools
from typing import Any, Callable


class TimeoutError(Exception):
    """Custom timeout error"""

    pass


def timeout(seconds: int):
    """
    Timeout decorator that raises TimeoutError if function execution exceeds the specified time.

    Args:
        seconds: Maximum execution time in seconds

    Raises:
        TimeoutError: If function execution exceeds the timeout limit
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            def timeout_handler(signum, frame):
                raise TimeoutError(
                    f"Function '{func.__name__}' timed out after {seconds} seconds"
                )

            # Set the signal handler and alarm
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # Reset the alarm and handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        return wrapper

    return decorator
