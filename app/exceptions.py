class CityNotFoundError(Exception):
    """Raised when the requested city cannot be found."""
    pass


class WeatherServiceError(Exception):
    """Raised when the external weather service fails."""
    pass