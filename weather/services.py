import logging
from json import JSONDecodeError

import requests
from requests import RequestException, Timeout

from WeatherApp.settings import WEATHER_API_KEY
from weather.config import GEOCODING_LIMIT, GEOCODING_API_URL, WEATHER_API_URL, API_TIMEOUT
from weather.dtos import LocationDTO, WeatherDTO
from weather.exceptions import GeocodingApiError

logger = logging.getLogger(__name__)


class WeatherAPI:
    @staticmethod
    def get_locations(query: str) -> list[LocationDTO]:
        if not query:
            return []
        params = {'q': query, 'limit': GEOCODING_LIMIT, 'appid': WEATHER_API_KEY}

        data = WeatherAPI.get_json_by_weather_api(params, GEOCODING_API_URL)

        locations_dto = []
        if isinstance(data, list):
            for location in data:
                location_dto = LocationDTO(
                    name=location.get('name', 'Unknown'),
                    latitude=location.get('lat'),
                    longitude=location.get('lon'),
                    country=location.get('country', 'Unknown'),
                )
                locations_dto.append(location_dto)

        return locations_dto

    @staticmethod
    def get_weather(latitude, longitude, name):
        weather_locations = []
        params = {'lat': latitude, 'lon': longitude, 'appid': WEATHER_API_KEY, 'units': 'metric', 'lang': 'ru'}

        data = WeatherAPI.get_json_by_weather_api(params, WEATHER_API_URL)
        try:
            return WeatherDTO(
                lat=latitude,
                lon=longitude,
                weather=data['weather'][0].get('description', 'неизвестно').capitalize(),
                temp=round(data['main']['temp']),
                feels_like=round(data['main']['feels_like']),
                pressure=round(data['main']['pressure'] * 0.75),
                humidity=data['main']['humidity'],
                wind_speed=round(data['wind']['speed']),
                country=data['sys']['country'],
                name=name,
                icon=data['weather'][0]['icon']
            )
        except (KeyError, IndexError):
            logger.error(f'Ошибка извлечения данных', exc_info=True)
            raise GeocodingApiError('Ошибка извлечения данных')

    @staticmethod
    def get_json_by_weather_api(params, url):
        try:
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            return response.json()

        except Timeout:
            logger.warning(f"Превышено время ожидания от OpenWeatherAPI {url}.")
            raise GeocodingApiError('Превышено время ожидания от OpenWeatherAPI.')
        except RequestException:
            logger.warning("Ошибка сети при поиске локаций.")
            raise GeocodingApiError(f'Ошибка сети при поиске локаций.')
        except (ValueError, JSONDecodeError):
            logger.warning(f'Не удалось обработать ответ от сервиса OpenWeatherAPI {url}.')
            raise GeocodingApiError('Не удалось обработать ответ от сервиса OpenWeatherAPI.')
