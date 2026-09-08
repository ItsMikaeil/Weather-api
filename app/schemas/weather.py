from typing import Optional

from pydantic import BaseModel, ConfigDict


class CurrentConditions(BaseModel):
    model_config = ConfigDict(extra="ignore")

    datetime: Optional[str] = None
    temp: float
    feelslike: Optional[float] = None
    humidity: float
    windspeed: Optional[float] = None
    conditions: str


class VisualCrossingResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    address: str
    resolvedAddress: str
    timezone: str
    description: Optional[str] = None
    currentConditions: CurrentConditions


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    feels_like: Optional[float] = None
    humidity: float
    conditions: str
    wind_speed: Optional[float] = None