from fastapi import FastAPI, HTTPException, Request

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.exceptions import (
    CityNotFoundError,
    WeatherServiceError,
)
from app.rate_limit import limiter
from app.redis import redis_client
from app.schemas.weather import WeatherResponse
from app.services import weather_service


app = FastAPI(
    title=settings.app_name,
)


# Store the limiter on the FastAPI application state
app.state.limiter = limiter

# Return HTTP 429 when the rate limit is exceeded
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


@app.get(
    "/weather/{city}",
    response_model=WeatherResponse,
)
@limiter.limit("5/minute")
async def weather(
    request: Request,
    city: str,
):
    # Request weather data from the application service
    try:
        return await weather_service.get_weather(city)

    # Return 404 when the requested city cannot be found
    except CityNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="City not found",
        )

    # Return 502 when the external weather service fails
    except WeatherServiceError:
        raise HTTPException(
            status_code=502,
            detail="Weather service is unavailable",
        )