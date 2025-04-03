class WeatherServiceError(Exception):
    pass


class GeocodingApiError(WeatherServiceError):
    pass
