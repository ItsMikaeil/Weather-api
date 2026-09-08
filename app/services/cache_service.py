import json

import redis.asyncio as redis

from app.redis import redis_client


async def get_cached_weather(key: str):
    try:
        # Try to read the cached weather data from Redis
        cached = await redis_client.get(key)

        if cached is None:
            return None

        # Convert the JSON string stored in Redis back into a Python dictionary
        return json.loads(cached)

    except redis.RedisError as exc:
        # Redis is only a cache, so a Redis failure should not break the request
        print(f"Redis GET failed: {exc}")
        return None


async def set_cached_weather(
    key: str,
    weather: dict,
    ttl: int,
):
    try:
        # Convert the Python dictionary into a JSON string
        value = json.dumps(weather)

        # Store the weather data in Redis with an expiration time
        await redis_client.set(
            key,
            value,
            ex=ttl,
        )

    except redis.RedisError as exc:
        # Cache failures should not prevent a successful weather response
        print(f"Redis SET failed: {exc}")