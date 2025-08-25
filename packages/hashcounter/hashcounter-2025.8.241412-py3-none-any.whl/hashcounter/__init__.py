from __future__ import annotations

import hashlib
from typing import Optional

import redis.asyncio as redis


async def bump_string_counter(
    value: str,
    *,
    redis_url: str,
    key_prefix: str,
    ttl_seconds: int = 600,
    client: Optional[redis.Redis] = None,
) -> int:
    """
    Increment a counter for a given string value in Redis with a specified TTL.
    Args:
        value (str): The string value to count.
        redis_url (str): The Redis connection URL.
        key_prefix (str): Prefix for the Redis key.
        ttl_seconds (int, optional): Time-to-live for the key in seconds. Defaults to 600.
        client (Optional[redis.Redis], optional): An existing Redis client. If None, a new client will be created. Defaults to None.
    Returns:
        int: The current count after incrementing.
    Raises:
        ValueError: If ttl_seconds is not greater than 0.
    Example:
        count = await bump_string_counter(
            "example_value",
            redis_url="redis://localhost",
            key_prefix="myapp:counter",
            ttl_seconds=300,
        )
        print(count)  # Outputs the current count for "example_value"
    """
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be > 0")

    key_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
    key = f"{key_prefix}:{key_hash}"

    close_client = False
    if client is None:
        client = redis.from_url(redis_url, decode_responses=False)
        close_client = True

    try:
        async with client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, ttl_seconds)
            res = await pipe.execute()

        current = int(res[0])
        return current
    finally:
        if close_client:
            await client.aclose()
