from __future__ import annotations

import hashlib
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import WatchError


async def bump_string_counter(
    value: str,
    *,
    redis_url: str,
    key_prefix: str,
    ttl_seconds: int = 600,
    client: Optional[redis.Redis] = None,
    val: Optional[int] = None,
) -> int:
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be > 0")

    key_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
    key = f"{key_prefix}:{key_hash}"

    close_client = False
    if client is None:
        client = redis.from_url(redis_url, decode_responses=False)
        close_client = True

    try:
        if val is None:
            async with client.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, ttl_seconds)
                incr_res, _ = await pipe.execute()
            return int(incr_res)

        while True:
            pipe = client.pipeline()
            try:
                await pipe.watch(key)
                cur = await pipe.get(key)  # immediate under WATCH
                cur_i = int(cur.decode() if isinstance(cur, (bytes, bytearray)) else (cur or 0)) if cur else 0

                if cur_i >= val:
                    await pipe.unwatch()
                    try:
                        await client.getex(key, ex=ttl_seconds)  # type: ignore[attr-defined]
                    except Exception:
                        await client.expire(key, ttl_seconds)
                    return cur_i

                pipe.multi()
                pipe.incr(key)
                pipe.expire(key, ttl_seconds)
                new_i, _ = await pipe.execute()
                return int(new_i)
            except WatchError:
                continue
            finally:
                await pipe.reset()
    finally:
        if close_client:
            await client.aclose()
