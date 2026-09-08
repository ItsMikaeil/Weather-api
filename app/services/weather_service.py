import httpx

from app.config import settings
from app.exceptions import (
    CityNotFoundError,
    WeatherServiceError,
)
from app.schemas.weather import VisualCrossingResponse
from app.services import cache_service
from pydantic import ValidationError


BASE_URL = (
    "https://weather.visualcrossing.com/"
    "VisualCrossingWebServices/rest/services/timeline"
)

# Keep cached weather data for 12 hours
CACHE_TTL = 43200


async def fetch_weather_from_api(city: str):
    # Build the request URL for the external weather API
    url = f"{BASE_URL}/{city}"

    params = {
        "unitGroup": "metric",
        "include": "current",
        "key": settings.weather_api_key,
        "contentType": "json",
    }

    try:
        # Create an asynchronous HTTP client with a 10-second timeout
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                params=params,
            )

        # Raise an exception for HTTP error responses
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        # A 400 response means the requested city could not be found
        if exc.response.status_code == 400:
            raise CityNotFoundError(
                f"City not found: {city}"
            ) from exc

        # Convert other upstream HTTP errors into an application-level error
        raise WeatherServiceError(
            "Weather service returned an HTTP error"
        ) from exc

    except httpx.RequestError as exc:
        # Convert network and timeout errors into an application-level error
        raise WeatherServiceError(
            "Weather service is unavailable"
        ) from exc

    try:
        # Validate the response using the Pydantic model
        return VisualCrossingResponse.model_validate(
            response.json()
        )

    except ValidationError as exc:
        # Treat an unexpected response structure as an external service failure
        raise WeatherServiceError(
            "Invalid response from weather service"
        ) from exc



async def get_weather(city: str):

    # Remove unnecessary whitespace from the city name
    normalized_city = city.strip()

    # Use lowercase cache keys to avoid duplicate entries
    cache_key = f"weather:{normalized_city.lower()}"

    # Try to get the weather data from Redis first
    cached = await cache_service.get_cached_weather(cache_key)

    if cached is not None:
        print("CACHE HIT")
        return cached

    print("CACHE MISS")

    # Fetch fresh weather data from the external API
    data = await fetch_weather_from_api(normalized_city)

    # Convert the external API response into our internal response format
    weather = {
        "city": data.resolvedAddress,
        "temperature": data.currentConditions.temp,
        "feels_like": data.currentConditions.feelslike,
        "humidity": data.currentConditions.humidity,
        "conditions": data.currentConditions.conditions,
        "wind_speed": data.currentConditions.windspeed,
    }

    # Store the fresh data in Redis for future requests
    await cache_service.set_cached_weather(
        cache_key,
        weather,
        CACHE_TTL,
    )

    return weather