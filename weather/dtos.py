from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LocationDTO:
    name: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    country: str | None


@dataclass(frozen=True)
class WeatherDTO:
    lat: Decimal
    lon: Decimal
    weather: str
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    wind_speed: float
    country: str
    name: str
    icon: str
