from __future__ import annotations

from typing import Optional

import redis.asyncio as redis

__all__ = ["get_hash_value", "set_hash_value"]


async def get_hash_value(
    hash_hex: str,
    *,
    redis_url: str,
    key_prefix: str,
    client: Optional[redis.Redis] = None,
) -> str:
    """
    Get string value of <key_prefix>:<hash_hex>. Returns "" if absent.
    Does not change TTL.
    """
    key = f"{key_prefix}:{hash_hex.lower()}"

    close_client = False
    if client is None:
        client = redis.from_url(redis_url, decode_responses=False)
        close_client = True

    try:
        raw = await client.get(key)
        if raw is None:
            return ""
        if isinstance(raw, (bytes, bytearray)):
            return raw.decode()
        return str(raw)
    finally:
        if close_client:
            await client.aclose()


async def set_hash_value(
    hash_hex: str,
    *,
    value: str,
    ttl_seconds: int,
    redis_url: str,
    key_prefix: str,
    client: Optional[redis.Redis] = None,
) -> str:
    """
    Set <key_prefix>:<hash_hex> to the given string with TTL. Returns the value.
    """
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be > 0")

    key = f"{key_prefix}:{hash_hex.lower()}"

    close_client = False
    if client is None:
        client = redis.from_url(redis_url, decode_responses=False)
        close_client = True

    try:
        # store exactly as given
        await client.set(key, value.encode("utf-8"), ex=ttl_seconds)
        return value
    finally:
        if close_client:
            await client.aclose()
