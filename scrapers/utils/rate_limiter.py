"""Rate limiter for HTTP requests to prevent IP blocking."""

import time
from functools import wraps
from typing import Any, Callable, TypeVar
from loguru import logger

F = TypeVar("F", bound=Callable[..., Any])


class RateLimiter:
    """Simple rate limiter for HTTP requests."""

    def __init__(self, calls_per_second: float = 5.0) -> None:
        """
        Initialize rate limiter.

        Args:
            calls_per_second: Maximum number of calls allowed per second
        """
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_call = time.time()


def rate_limit(calls_per_second: float = 1.0) -> Callable[[F], F]:
    """
    Decorator to rate limit function calls.

    Args:
        calls_per_second: Maximum number of calls allowed per second

    Returns:
        Decorated function with rate limiting

    Example:
        >>> @rate_limit(calls_per_second=2.0)
        ... def fetch_data(url):
        ...     return requests.get(url)
    """
    limiter = RateLimiter(calls_per_second)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter.wait()
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
