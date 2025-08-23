from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from threading import Lock
import asyncio
from loguru import logger


@dataclass
class CacheEntry:
    """A single cache entry with TTL support."""
    value: Any
    expires_at: float
    
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at


class ResponseCache:
    """Thread-safe response cache with TTL support for sync clients."""
    
    def __init__(self, ttl: float = 300.0, max_size: int = 1000):
        """Initialize the cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 300s / 5 minutes)
            max_size: Maximum number of entries to cache
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        logger.debug(f"ResponseCache initialized with ttl={ttl}s, max_size={max_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            self._hits += 1
            logger.debug(f"Cache hit for key: {key}")
            return entry.value
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Clean up if we're at max size
            if len(self._cache) >= self.max_size:
                self._evict_expired()
                # If still at max size, remove oldest entry
                if len(self._cache) >= self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    logger.debug(f"Evicted oldest cache entry: {oldest_key}")
            
            expires_at = time.time() + self.ttl
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            logger.debug(f"Cached key: {key}, expires at: {expires_at}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            size = len(self._cache)
            self._cache.clear()
            logger.debug(f"Cleared {size} cache entries")
    
    def _evict_expired(self) -> None:
        """Remove all expired entries."""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.expires_at <= now
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"Evicted {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
            }


class AsyncResponseCache:
    """Async-safe response cache with TTL support for async clients."""
    
    def __init__(self, ttl: float = 300.0, max_size: int = 1000):
        """Initialize the async cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 300s / 5 minutes)
            max_size: Maximum number of entries to cache
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0
        logger.debug(f"AsyncResponseCache initialized with ttl={ttl}s, max_size={max_size}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            self._hits += 1
            logger.debug(f"Cache hit for key: {key}")
            return entry.value
    
    async def set(self, key: str, value: Any) -> None:
        """Set a value in the cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        async with self._lock:
            # Clean up if we're at max size
            if len(self._cache) >= self.max_size:
                self._evict_expired()
                # If still at max size, remove oldest entry
                if len(self._cache) >= self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    logger.debug(f"Evicted oldest cache entry: {oldest_key}")
            
            expires_at = time.time() + self.ttl
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            logger.debug(f"Cached key: {key}, expires at: {expires_at}")
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            size = len(self._cache)
            self._cache.clear()
            logger.debug(f"Cleared {size} cache entries")
    
    def _evict_expired(self) -> None:
        """Remove all expired entries (internal, not async)."""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.expires_at <= now
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"Evicted {len(expired_keys)} expired entries")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
            }