from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LocationDTO:
    name: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    country: str | None
