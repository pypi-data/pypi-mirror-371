"""
Cache helper utilities for clean, consistent cache operations with automatic logging.
Abstracts away cache complexity and provides clean interfaces for routers.
"""

import time
from typing import Any, Tuple, Callable
from ..core.logger import get_logger

logger = get_logger(__name__)


class CacheHelper:
    """
    Helper class for cache operations with automatic logging and error handling.

    Usage:
        cache = CacheHelper("quote_cache", "redis")

        # Get with automatic logging
        data = await cache.get("quote:AAPL", fallback=default_quote)

        # Set with automatic logging
        await cache.set("quote:AAPL", quote_data, ttl_seconds=300)

        # Check if exists
        if await cache.exists("quote:AAPL"):
            # Do something
    """

    def __init__(self, cache_name: str, cache_type: str = "redis"):
        self.cache_name = cache_name
        self.cache_type = cache_type
        self._cache_service = None

    def _get_cache_service(self):
        """Get cache service - override in subclasses for actual implementation."""
        if self._cache_service is None:
            # This is a placeholder - subclasses should implement actual cache service
            raise NotImplementedError(
                "Cache service not implemented - override _get_cache_service"
            )
        return self._cache_service

    async def get(
        self, key: str, fallback: Any = None, log_operation: bool = True
    ) -> Tuple[Any, bool]:
        """
        Get data from cache with automatic logging.

        Returns:
            Tuple of (data, cache_hit)
        """
        start_time = time.time()

        try:
            cache_service = self._get_cache_service()
            data = await cache_service.get(key)
            duration_ms = (time.time() - start_time) * 1000

            if data is not None:
                # Cache hit
                if log_operation:
                    await logger.log_cache_operation(
                        step="Cache_Hit",
                        cache_hit=True,
                        cache_key=key,
                        duration_ms=duration_ms,
                    )
                return data, True
            else:
                # Cache miss
                if log_operation:
                    await logger.log_cache_operation(
                        step="Cache_Miss",
                        cache_hit=False,
                        cache_key=key,
                        duration_ms=duration_ms,
                    )
                return fallback, False

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            if log_operation:
                await logger.log_cache_operation(
                    step="Cache_Error",
                    cache_hit=False,
                    cache_key=key,
                    duration_ms=duration_ms,
                    error=str(e),
                )
            return fallback, False

    async def set(
        self, key: str, data: Any, ttl_seconds: int = 300, log_operation: bool = True
    ) -> bool:
        """Set data in cache with automatic logging."""
        start_time = time.time()

        try:
            cache_service = self._get_cache_service()
            success = await cache_service.set(key, data, ttl_seconds)
            duration_ms = (time.time() - start_time) * 1000

            if log_operation:
                await logger.log_cache_operation(
                    step="Cache_Set",
                    cache_hit=False,
                    cache_key=key,
                    duration_ms=duration_ms,
                )

            # Ensure we return a boolean
            return bool(success)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            if log_operation:
                await logger.log_cache_operation(
                    step="Cache_Error",
                    cache_hit=False,
                    cache_key=key,
                    duration_ms=duration_ms,
                    error=str(e),
                )
            return False

    async def delete(self, key: str, log_operation: bool = True) -> bool:
        """Delete data from cache with automatic logging."""
        start_time = time.time()

        try:
            cache_service = self._get_cache_service()
            success = await cache_service.delete(key)
            duration_ms = (time.time() - start_time) * 1000

            if log_operation:
                await logger.log_cache_operation(
                    step="Cache_Delete",
                    cache_hit=False,
                    cache_key=key,
                    duration_ms=duration_ms,
                )

            # Ensure we return a boolean
            return bool(success)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            if log_operation:
                await logger.log_cache_operation(
                    step="Cache_Error",
                    cache_hit=False,
                    cache_key=key,
                    duration_ms=duration_ms,
                    error=str(e),
                )
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            cache_service = self._get_cache_service()
            data = await cache_service.get(key)
            return data is not None
        except Exception:
            return False

    def build_key(self, *parts: str, separator: str = ":") -> str:
        """Build a cache key from parts."""
        return separator.join(str(part) for part in parts if part is not None)


async def get_cached_or_fetch(
    cache_name: str,
    cache_key: str,
    fetch_func: Callable,
    ttl_seconds: int = 300,
    cache_type: str = "redis",
    **fetch_kwargs,
) -> Tuple[Any, bool]:
    """
    High-level function to get from cache or fetch if not available.

    Usage:
        data, cache_hit = await get_cached_or_fetch(
            cache_name="quote_cache",
            cache_key=f"quote:{symbol}",
            fetch_func=quote_service.get_quote,
            symbol=symbol,
            ttl_seconds=300
        )
    """
    cache = CacheHelper(cache_name, cache_type)

    # Try to get from cache first
    cached_data, cache_hit = await cache.get(cache_key)

    if cache_hit:
        return cached_data, True

    # Cache miss - fetch fresh data
    try:
        fresh_data = await fetch_func(**fetch_kwargs)

        # Cache the fresh data
        if fresh_data is not None:
            await cache.set(cache_key, fresh_data, ttl_seconds)

        return fresh_data, False

    except Exception as e:
        # Log the fetch error
        await logger.log_cache_operation(
            step="Cache_Fetch_Error", cache_hit=False, cache_key=cache_key, error=str(e)
        )
        raise


def cache_key_builder(prefix: str, *parts: str, separator: str = ":") -> str:
    """
    Simple function to build cache keys.

    Usage:
        key = cache_key_builder("quote", symbol, timeframe, method)
        # Result: "quote:AAPL:daily:standard"
    """
    return separator.join([prefix] + [str(part) for part in parts if part is not None])
