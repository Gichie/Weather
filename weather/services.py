import requests
from requests import RequestException, Timeout

from WeatherApp.settings import WEATHER_API_KEY
from weather.dtos import LocationDTO, WeatherDTO
from weather.exceptions import GeocodingApiError

GEOCODING_API_URL = 'https://api.openweathermap.org/geo/1.0/direct'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
GEOCODING_LIMIT = 5
API_TIMEOUT = 10


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

    @staticmethod
    def get_json_by_weather_api(params, url):
        try:
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            return response.json()

        except Timeout:
            raise GeocodingApiError('Превышено время ожидания от GeocodingAPI.')
        except RequestException as e:
            # todo logging
            raise GeocodingApiError(f'Ошибка сети при поиске локаций: {e}')
        except ValueError:
            # todo logging
            raise GeocodingApiError('Не удалось обработать ответ от сервиса GeocodingAPI.')
