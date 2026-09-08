import httpx

from fastapi.testclient import TestClient

from app.exceptions import (
    CityNotFoundError,
    WeatherServiceError,
)
from app.main import app
import pytest
from app.services import weather_service, cache_service
from app.schemas.weather import VisualCrossingResponse



client = TestClient(app)


FAKE_WEATHER = {
    "city": "London",
    "temperature": 22.5,
    "feels_like": 22.5,
    "humidity": 41.9,
    "conditions": "Partially cloudy",
    "wind_speed": 3.6,
}


def test_weather_endpoint(monkeypatch):
    # Replace the real weather service with a fake implementation
    async def fake_get_weather(city: str):
        return {
            **FAKE_WEATHER,
            "city": city,
        }

    monkeypatch.setattr(
        weather_service,
        "get_weather",
        fake_get_weather,
    )

    response = client.get("/weather/London")

    # The endpoint should return HTTP 200
    assert response.status_code == 200

    data = response.json()

    assert data["city"] == "London"
    assert data["temperature"] == 22.5
    assert data["conditions"] == "Partially cloudy"


def test_invalid_city(monkeypatch):
    # Simulate the application-level error for an unknown city
    async def fake_get_weather(city: str):
        raise CityNotFoundError(
            f"City not found: {city}"
        )

    monkeypatch.setattr(
        weather_service,
        "get_weather",
        fake_get_weather,
    )

    response = client.get("/weather/InvalidCity")

    # The API should translate the application error into HTTP 404
    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "City not found"


def test_weather_service_unavailable(monkeypatch):
    # Simulate a failure in the external weather service
    async def fake_get_weather(city: str):
        raise WeatherServiceError(
            "Weather service is unavailable"
        )

    monkeypatch.setattr(
        weather_service,
        "get_weather",
        fake_get_weather,
    )

    response = client.get("/weather/London")

    # The API should return HTTP 502 when the external service fails
    assert response.status_code == 502

    data = response.json()

    assert data["detail"] == "Weather service is unavailable"





@pytest.mark.asyncio
async def test_cache_hit(monkeypatch):
    # Prepare weather data that simulates an existing cache entry
    cached_weather = {
        **FAKE_WEATHER,
        "city": "London",
    }

    # Return the fake data whenever Redis is queried
    async def fake_get_cached_weather(key: str):
        return cached_weather

    # Fail the test if the external API is called
    async def fake_fetch_weather_from_api(city: str):
        raise AssertionError(
            "External API should not be called on cache HIT"
        )

    # Replace the real Redis lookup with our fake implementation
    monkeypatch.setattr(
        cache_service,
        "get_cached_weather",
        fake_get_cached_weather,
    )

    # Replace the external API call with a function that must never run
    monkeypatch.setattr(
        weather_service,
        "fetch_weather_from_api",
        fake_fetch_weather_from_api,
    )

    result = await weather_service.get_weather("London")

    # The cached data should be returned directly
    assert result == cached_weather




@pytest.mark.asyncio
async def test_cache_miss(monkeypatch):
    # Track whether the external API was called
    api_call_count = 0

    # Store data written to the fake cache
    saved_cache = {}

    # Simulate a cache miss
    async def fake_get_cached_weather(key: str):
        return None

    # Simulate a successful external API response
    async def fake_fetch_weather_from_api(city: str):
        nonlocal api_call_count

        api_call_count += 1

        return VisualCrossingResponse(
            address="London",
            resolvedAddress="London",
            timezone="Europe/London",
            currentConditions={
                "datetime": "18:36:00",
                "temp": 22.5,
                "feelslike": 22.5,
                "humidity": 41.9,
                "windspeed": 3.6,
                "conditions": "Partially cloudy",
            },
        )

    # Capture whatever the application tries to save to Redis
    async def fake_set_cached_weather(
        key: str,
        weather: dict,
        ttl: int,
    ):
        saved_cache["key"] = key
        saved_cache["weather"] = weather
        saved_cache["ttl"] = ttl

  
    monkeypatch.setattr(
        cache_service,
        "get_cached_weather",
        fake_get_cached_weather,
    )

  
    monkeypatch.setattr(
        weather_service,
        "fetch_weather_from_api",
        fake_fetch_weather_from_api,
    )

   
    monkeypatch.setattr(
        cache_service,
        "set_cached_weather",
        fake_set_cached_weather,
    )

    result = await weather_service.get_weather("London")

    # The external API should be called exactly once
    assert api_call_count == 1

    # The service should return fresh weather data
    assert result["city"] == "London"
    assert result["temperature"] == 22.5

    # The service should save the result in the cache
    assert saved_cache["key"] == "weather:london"

    # The cached data should match the returned data
    assert saved_cache["weather"] == result

    # The configured cache TTL should be used
    assert saved_cache["ttl"] == weather_service.CACHE_TTL



# Inside tests/test_weather.py

# ... other imports ...
from app.main import app, limiter # Make sure you import limiter correctly

# ... other tests ...

def test_rate_limit(monkeypatch):
    # Replace the weather service so the test only focuses on rate limiting
    async def fake_get_weather(city: str):
        return FAKE_WEATHER

    monkeypatch.setattr(
        weather_service,
        "get_weather",
        fake_get_weather,
    )

    # --- Add this line here ---
    # Clear the rate limiter's storage before making requests
    if hasattr(limiter, "_storage") and limiter._storage is not None:
        limiter._storage.reset()
    # --- End of added line ---

    # The first five requests should be allowed
    for _ in range(5):
        response = client.get("/weather/London")
        assert response.status_code == 200

    # The sixth request should be rejected by the rate limiter
    response = client.get("/weather/London")
    assert response.status_code == 429

# ... rest of your tests ...
