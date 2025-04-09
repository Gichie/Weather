from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from weather.exceptions import GeocodingApiError
from weather.forms import SearchLocationForm
from weather.models import Location

User = get_user_model()


class TestIndexView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.location1 = Location.objects.create(
            name='City A',
            country='CA',
            user=self.user,
            latitude=Decimal('10.0'),
            longitude=Decimal('20.0'),
        )
        self.location2 = Location.objects.create(
            name='City B',
            country='CB',
            user=self.user,
            latitude=Decimal('30.0'),
            longitude=Decimal('-40.0'),
        )
        self.index_url = reverse('weather:home')

    def test_index_view_redirects_anonymous(self):
        """Тест: анонимный пользователь перенаправляется на страницу входа."""
        response = self.client.get(self.index_url)
        self.assertRedirects(response, f'{reverse("users:login")}?next={self.index_url}')

    @patch('weather.services.WeatherAPI.get_weather')
    def test_index_view_succes_logged_in(self, mock_get_weather):
        """Тест: успешный доступ и базовый контекст для залогиненного пользователя."""
        mock_get_weather.side_effect = [
            {'name': 'City A', 'country': 'CA', 'temp': 15, 'weather': 'Облачно', 'icon': '04d', 'lat': 10.0,
             'lon': 20.0, 'feels_like': 14, 'pressure': 760, 'humidity': 50, 'wind_speed': 3},
            {'name': 'City B', 'country': 'CB', 'temp': 25, 'weather': 'Ясно', 'icon': '01d', 'lat': 30.0, 'lon': 40.0,
             'feels_like': 24, 'pressure': 755, 'humidity': 40, 'wind_speed': 1},
        ]

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

        self.assertIn('locations_weather', response.context)
        self.assertIn('search_form', response.context)
        self.assertIsInstance(response.context['search_form'], SearchLocationForm)

        self.assertEqual(mock_get_weather.call_count, 2)
        mock_get_weather.assert_any_call(Decimal('10.0'), Decimal('20.0'), 'City A')
        mock_get_weather.assert_any_call(Decimal('30.0'), Decimal('-40.0'), 'City B')

        locations_weather_context = response.context['locations_weather']
        self.assertEqual(len(locations_weather_context), 2)
        self.assertEqual(locations_weather_context[0]['temp'], 15)
        self.assertEqual(locations_weather_context[1]['temp'], 25)

    @patch('weather.services.WeatherAPI.get_weather')
    def test_index_view_handles_api_error(self, mock_get_weather):
        """Тест: обработка ошибки API."""
        mock_get_weather.side_effect = GeocodingApiError('Тестовая ошибка API')

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 503)
        self.assertTemplateUsed(response, 'weather/API_error.html')

        self.assertIn('error_title', response.context)
        self.assertIn('error_message', response.context)
        self.assertEqual(response.context['error_title'], 'Ошибка сервиса геолокации')

        mock_get_weather.assert_called()

    @patch('weather.services.WeatherAPI.get_weather')
    def test_index_view_pagination(self, mock_get_weather):
        """Тест: проверка пагинации."""
        for i in range(7):
            Location.objects.create(
                user=self.user,
                name=f'City {i + 3}',
                country='CX',
                latitude=Decimal(f'5{i}.0'),
                longitude=Decimal(f'6{i}.0')
            )

        def mock_weather_data(lat, lon, name):
            return {'name': name, 'temp': 10 + lat, 'weather': 'Пасмурно', 'icon': '03d', 'lat': lat, 'lon': lon,
                    'country': 'CX', 'feels_like': 10 + lat - 1, 'pressure': 750, 'humidity': 60, 'wind_speed': 2}

        mock_get_weather.side_effect = mock_weather_data

        self.client.login(username='testuser', password='password123')

        # Запрашиваем первую страницу
        response_page1 = self.client.get(self.index_url)
        self.assertEqual(response_page1.status_code, 200)
        self.assertTrue(response_page1.context['is_paginated'])  # Пагинация должна быть активна
        self.assertEqual(len(response_page1.context['locations_weather']), 6)  # На первой странице 6 элементов
        self.assertEqual(response_page1.context['page_obj'].number, 1)

        # Запрашиваем вторую страницу
        response_page2 = self.client.get(self.index_url + '?page=2')
        self.assertEqual(response_page2.status_code, 200)
        self.assertTrue(response_page2.context['is_paginated'])
        # На второй странице должно быть оставшееся количество (2 исходные + 7 новых = 9 всего; 9-6 = 3)
        self.assertEqual(len(response_page2.context['locations_weather']), 3)
        self.assertEqual(response_page2.context['page_obj'].number, 2)
