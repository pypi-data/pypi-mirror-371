"""
Advanced Caching System for Rust Crate Pipeline

Provides intelligent caching with multiple strategies:
- Memory cache (fastest)
- Disk cache (persistent)
- Distributed cache (Redis/Memcached)
- Intelligent cache invalidation
- Cache warming and prefetching
"""

import hashlib
import json
import logging
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiofiles
from cachetools import TTLCache
import redis.asyncio as redis


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl: Optional[int] = None  # seconds
    tags: List[str] = field(default_factory=list)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)

    def touch(self) -> None:
        """Update access time and count."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Store value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries by tags."""
        pass


class MemoryCache(CacheStrategy):
    """In-memory cache using TTLCache."""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.logger = logging.getLogger(__name__)

    async def get(self, key: str) -> Optional[Any]:
        try:
            return self.cache.get(key)
        except Exception as e:
            self.logger.warning(f"Memory cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        try:
            self.cache[key] = value
            return True
        except Exception as e:
            self.logger.warning(f"Memory cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            return self.cache.pop(key, None) is not None
        except Exception as e:
            self.logger.warning(f"Memory cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        try:
            self.cache.clear()
            return True
        except Exception as e:
            self.logger.warning(f"Memory cache clear error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        # Memory cache doesn't support tag-based invalidation
        return 0


class DiskCache(CacheStrategy):
    """Persistent disk cache with intelligent file management."""

    def __init__(self, cache_dir: str = "./cache", max_size_mb: int = 1024):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(__name__)
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self.metadata = {k: CacheEntry(**v) for k, v in data.items()}
        except Exception as e:
            self.logger.warning(f"Failed to load cache metadata: {e}")
            self.metadata = {}

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(
                    {
                        k: {
                            "key": v.key,
                            "created_at": v.created_at.isoformat(),
                            "accessed_at": v.accessed_at.isoformat(),
                            "access_count": v.access_count,
                            "ttl": v.ttl,
                            "tags": v.tags,
                            "size_bytes": v.size_bytes,
                        }
                        for k, v in self.metadata.items()
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            self.logger.warning(f"Failed to save cache metadata: {e}")

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    async def get(self, key: str) -> Optional[Any]:
        try:
            if key not in self.metadata:
                return None

            entry = self.metadata[key]
            if entry.is_expired():
                await self.delete(key)
                return None

            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None

            async with aiofiles.open(cache_path, "rb") as f:
                data = await f.read()
                value = pickle.loads(data)

            # Update access metadata
            entry.touch()
            self._save_metadata()

            return value
        except Exception as e:
            self.logger.warning(f"Disk cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        try:
            # Serialize value
            data = pickle.dumps(value)
            size_bytes = len(data)

            # Check cache size limits
            await self._enforce_size_limit(size_bytes)

            # Save to disk
            cache_path = self._get_cache_path(key)
            async with aiofiles.open(cache_path, "wb") as f:
                await f.write(data)

            # Update metadata
            self.metadata[key] = CacheEntry(
                key=key,
                value=None,  # Don't store value in metadata
                ttl=ttl,
                tags=tags or [],
                size_bytes=size_bytes,
            )
            self._save_metadata()

            return True
        except Exception as e:
            self.logger.warning(f"Disk cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            if key in self.metadata:
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
                del self.metadata[key]
                self._save_metadata()
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Disk cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        try:
            # Remove all cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

            # Clear metadata
            self.metadata.clear()
            self._save_metadata()
            return True
        except Exception as e:
            self.logger.warning(f"Disk cache clear error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries that match any of the provided tags."""
        try:
            invalidated = 0
            keys_to_delete = []

            for key, entry in self.metadata.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                if await self.delete(key):
                    invalidated += 1

            return invalidated
        except Exception as e:
            self.logger.warning(f"Disk cache tag invalidation error: {e}")
            return 0

    async def _enforce_size_limit(self, new_entry_size: int) -> None:
        """Enforce cache size limits by removing least recently used entries."""
        current_size = sum(entry.size_bytes for entry in self.metadata.values())

        if current_size + new_entry_size <= self.max_size_bytes:
            return

        # Sort by access time (oldest first)
        sorted_entries = sorted(self.metadata.items(), key=lambda x: x[1].accessed_at)

        # Remove entries until we have enough space
        for key, entry in sorted_entries:
            if current_size + new_entry_size <= self.max_size_bytes:
                break

            await self.delete(key)
            current_size -= entry.size_bytes


class RedisCache(CacheStrategy):
    """Redis-based distributed cache."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)

    async def _get_client(self) -> redis.Redis:
        """Get Redis client, creating if necessary."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(self.redis_url)
        return self.redis_client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            data = await client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            self.logger.warning(f"Redis cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        try:
            client = await self._get_client()
            data = pickle.dumps(value)

            if ttl:
                await client.setex(key, ttl, data)
            else:
                await client.set(key, data)

            # Store tags if provided
            if tags:
                tag_key = f"{key}:tags"
                await client.sadd(tag_key, *tags)
                if ttl:
                    await client.expire(tag_key, ttl)

            return True
        except Exception as e:
            self.logger.warning(f"Redis cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            result = await client.delete(key)
            # Also delete associated tags
            await client.delete(f"{key}:tags")
            return result > 0
        except Exception as e:
            self.logger.warning(f"Redis cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        try:
            client = await self._get_client()
            await client.flushdb()
            return True
        except Exception as e:
            self.logger.warning(f"Redis cache clear error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        try:
            client = await self._get_client()
            invalidated = 0

            # Find keys with matching tags
            for tag in tags:
                pattern = f"*:tags"
                async for key in client.scan_iter(match=pattern):
                    tag_values = await client.smembers(key)
                    if any(tag.encode() in tag_values):
                        # Extract the main key from tag key
                        main_key = key.decode().replace(":tags", "")
                        if await self.delete(main_key):
                            invalidated += 1

            return invalidated
        except Exception as e:
            self.logger.warning(f"Redis cache tag invalidation error: {e}")
            return 0


class AdvancedCache:
    """Multi-level intelligent cache system."""

    def __init__(
        self,
        memory_cache_size: int = 1000,
        memory_cache_ttl: int = 3600,
        disk_cache_dir: str = "./cache",
        disk_cache_size_mb: int = 1024,
        redis_url: Optional[str] = None,
        enable_memory: bool = True,
        enable_disk: bool = True,
        enable_redis: bool = False,
    ):
        self.logger = logging.getLogger(__name__)
        self.strategies: List[CacheStrategy] = []

        # Initialize cache strategies
        if enable_memory:
            self.strategies.append(MemoryCache(memory_cache_size, memory_cache_ttl))

        if enable_disk:
            self.strategies.append(DiskCache(disk_cache_dir, disk_cache_size_mb))

        if enable_redis and redis_url:
            self.strategies.append(RedisCache(redis_url))

        self.logger.info(f"Initialized cache with {len(self.strategies)} strategies")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache, trying strategies in order."""
        for strategy in self.strategies:
            value = await strategy.get(key)
            if value is not None:
                # Cache warming: store in faster caches
                await self._warm_cache(key, value, strategy)
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Set value in all cache strategies."""
        success = False
        for strategy in self.strategies:
            if await strategy.set(key, value, ttl, tags):
                success = True
        return success

    async def delete(self, key: str) -> bool:
        """Delete value from all cache strategies."""
        success = False
        for strategy in self.strategies:
            if await strategy.delete(key):
                success = True
        return success

    async def clear(self) -> bool:
        """Clear all cache strategies."""
        success = True
        for strategy in self.strategies:
            if not await strategy.clear():
                success = False
        return success

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries by tags across all strategies."""
        total_invalidated = 0
        for strategy in self.strategies:
            total_invalidated += await strategy.invalidate_by_tags(tags)
        return total_invalidated

    async def _warm_cache(
        self, key: str, value: Any, source_strategy: CacheStrategy
    ) -> None:
        """Warm faster caches with value from slower cache."""
        for strategy in self.strategies:
            if strategy is source_strategy:
                continue
            # Only warm memory cache from disk/redis
            if isinstance(strategy, MemoryCache) and not isinstance(
                source_strategy, MemoryCache
            ):
                await strategy.set(key, value)


# Global cache instance
_global_cache: Optional[AdvancedCache] = None


def get_cache() -> AdvancedCache:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = AdvancedCache()
    return _global_cache


def set_cache(cache: AdvancedCache) -> None:
    """Set global cache instance."""
    global _global_cache
    _global_cache = cache
