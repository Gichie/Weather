import requests
from requests import HTTPError

from WeatherApp.settings import WEATHER_API_KEY
from weather.dtos import LocationDTO
from weather.exceptions import GeocodingApiError

GEOCODING_API_URL = 'https://api.openweathermap.org/geo/1.0/direct'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
GEOCODING_LIMIT = 5
API_TIMEOUT = 10


class WeatherAPI:
    @staticmethod
    def find_locations(query: str) -> list[LocationDTO]:
        if not query:
            return []

        params = {'q': query, 'limit': GEOCODING_LIMIT, 'appid': WEATHER_API_KEY}

        try:
            response = requests.get(GEOCODING_API_URL, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.Timeout:
            raise GeocodingApiError('Превышено время ожидания от GeocodingAPI.')
        except requests.exceptions.RequestException as e:
            # todo logging
            raise GeocodingApiError(f'Ошибка сети при поиске локаций: {e}')
        except ValueError:
            # todo logging
            raise GeocodingApiError('Не удалось обработать ответ от сервиса геокодинга.')

        locations_dto = []
        if isinstance(data, list):
            for location in data:
                try:
                    location_dto = LocationDTO(
                        name=location.get('name'),
                        latitude=location.get('lat'),
                        longitude=location.get('lon'),
                        country=location.get('country'),
                    )
                    locations_dto.append(location_dto)
                except (ValueError, TypeError) as e:
                    # todo logging
                    print(f"Ошибка парсинга данных локации: {location}. Ошибка: {e}")
                    continue

        return locations_dto


