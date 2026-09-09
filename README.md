

# Weather API

A weather API built with FastAPI that fetches weather data from the Visual Crossing Weather API, caches responses using Redis, handles external service errors, and protects the API with rate limiting.

This project was built as a practical backend project to learn how to work with:

- Third-party APIs
- Redis caching
- Environment variables
- Pydantic models
- Error handling
- Rate limiting
- Automated testing
- Docker and Docker Compose



## Features

- Fetch current weather data for a city
- Integrate with the Visual Crossing Weather API
- Cache weather responses in Redis
- Cache expiration using a 12-hour TTL
- Handle invalid cities and external API failures
- Rate limit requests to prevent abuse
- Validate external API responses using Pydantic
- Return a clean and controlled API response
- Automated tests with pytest
- Run the complete application with Docker Compose



## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- httpx
- Pydantic
- Pydantic Settings
- Redis
- SlowAPI
- pytest
- pytest-asyncio
- Docker
- Docker Compose
- Visual Crossing Weather API



## Architecture

The application follows a simple layered architecture:

```text
Client
   │
   ▼
FastAPI
   │
   ├── Rate Limiter
   │
   ▼
Weather Service
   │
   ├── Redis Cache
   │      │
   │      ├── Cache HIT
   │      │      └── Return cached data
   │      │
   │      └── Cache MISS
   │
   ▼
Visual Crossing API
   │
   ▼
Pydantic Validation
   │
   ▼
Map external response to internal response
   │
   ▼
Redis Cache
   │
   ▼
Client
````

Redis is used only as a cache. Visual Crossing remains the source of weather data.

---



## Project Structure

```text
weather-api/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── redis.py
│   ├── rate_limit.py
│   ├── exceptions.py
│   │
│   ├── schemas/
│   │   └── weather.py
│   │
│   └── services/
│       ├── weather_service.py
│       └── cache_service.py
│
├── tests/
│   └── test_weather.py
│
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Main components

`main.py`

Contains the FastAPI application and API routes.

`config.py`

Loads application configuration and environment variables.

`weather_service.py`

Contains the main weather logic and communicates with the external weather API.

`cache_service.py`

Contains Redis cache operations.

`weather.py`

Contains Pydantic models for validating external and internal weather data.

`exceptions.py`

Contains application-level exceptions such as city-not-found and weather-service errors.

`rate_limit.py`

Configures the API rate limiter.

`tests/test_weather.py`

Contains automated tests for the API and weather service.

---

## Environment Variables

Create a `.env` file in the root of the project.

```env
APP_NAME=Weather API
WEATHER_API_KEY=YOUR_VISUAL_CROSSING_API_KEY
REDIS_URL=redis://localhost:6379
```

### Variables

| Variable          | Description                            |
| ----------------- | -------------------------------------- |
| `APP_NAME`        | Name of the FastAPI application        |
| `WEATHER_API_KEY` | API key used to access Visual Crossing |
| `REDIS_URL`       | Redis connection URL                   |

Never commit `.env` to GitHub.

The repository contains `.env.example` as a template:

```env
APP_NAME=Weather API
WEATHER_API_KEY=
REDIS_URL=
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/ItsMikaeil/Weather-api
cd weather-api
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Redis

Make sure Redis is running on:

```text
localhost:6379
```

You can verify it with:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

### 5. Configure environment variables

Create `.env`:

```env
APP_NAME=Weather API
WEATHER_API_KEY=YOUR_VISUAL_CROSSING_API_KEY
REDIS_URL=redis://localhost:6379
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Docker

The project can also be run with Docker Compose.

Make sure your `.env` uses the Redis service name:

```env
APP_NAME=Weather API
WEATHER_API_KEY=YOUR_VISUAL_CROSSING_API_KEY
REDIS_URL=redis://redis:6379
```

Build and start the application:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

To stop the containers:

```bash
docker compose down
```

---

## API Endpoint

### Get weather for a city

```http
GET /weather/{city}
```

Example:

```http
GET /weather/London
```

Example response:

```json
{
  "city": "London",
  "temperature": 22.5,
  "feels_like": 22.5,
  "humidity": 41.9,
  "conditions": "Partially cloudy",
  "wind_speed": 3.6
}
```

The API exposes a simplified response instead of returning the complete Visual Crossing response.

---

## API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Caching

Weather responses are cached using Redis.

The cache key follows this format:

```text
weather:{city}
```

Example:

```text
weather:london
```

### Cache HIT

If the requested city already exists in Redis:

```text
Client
   ↓
FastAPI
   ↓
Redis
   ↓
Cache HIT
   ↓
Return cached response
```

The external weather API is not called.

### Cache MISS

If the city is not cached:

```text
Client
   ↓
FastAPI
   ↓
Redis
   ↓
Cache MISS
   ↓
Visual Crossing
   ↓
Redis SET
   ↓
Return response
```

Cached weather data expires after 12 hours.

```text
12 hours = 43200 seconds
```

---

## Rate Limiting

The weather endpoint is protected with rate limiting.

Current configuration:

```text
5 requests per minute
```

The limit is applied per client IP.

When the limit is exceeded, the API returns:

```text
429 Too Many Requests
```

The current limit is intentionally small to make the feature easy to test during development.

---

## Error Handling

The API translates external service errors into application-level responses.

### Invalid city

```text
404 Not Found
```

Example:

```json
{
  "detail": "City not found"
}
```

### External weather service failure

```text
502 Bad Gateway
```

Example:

```json
{
  "detail": "Weather service is unavailable"
}
```

### Rate limit exceeded

```text
429 Too Many Requests
```

---

## Testing

Tests are written using:

* pytest
* pytest-asyncio
* FastAPI TestClient
* monkeypatch

Run all tests with:

```bash
pytest
```

The test suite covers:

* Successful weather requests
* Invalid cities
* External API failures
* Cache HIT
* Cache MISS
* Rate limiting

The tests mock external dependencies instead of relying on the real Visual Crossing API wherever appropriate.

---

## Example Test Flow

A typical cached request behaves like this:

```text
First request
     ↓
CACHE MISS
     ↓
Visual Crossing API
     ↓
Save response to Redis
     ↓
Return weather


Second request
     ↓
CACHE HIT
     ↓
Return weather directly
```

---

## Development Notes

The application separates responsibilities into different layers:

```text
API Layer
    ↓
Service Layer
    ↓
Cache / External API
```

The external Visual Crossing response is validated separately from the response exposed by this API.

This prevents the application's public response format from being tightly coupled to the structure of the third-party API.

Redis is treated as a non-critical dependency because it is only used for caching. If Redis is unavailable, the application can still request fresh weather data from Visual Crossing.

---

## Future Improvements

Possible improvements for a production deployment include:

* Use Redis as the backend for rate limiting
* Add structured logging
* Add a dedicated health check endpoint
* Add more granular error handling
* Add integration tests
* Add CI/CD with GitHub Actions
* Deploy the API to a cloud platform
* Add monitoring and metrics

````
## URL

https://roadmap.sh/projects/weather-api-wrapper-service