import logging
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from weather.dtos import LocationDTO
from weather.exceptions import GeocodingApiError
from weather.forms import SearchLocationForm

logging.disable(logging.CRITICAL)

User = get_user_model()


class TestLocationSearchView(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создаем пользователя один раз для всех тестов класса."""
        cls.test_user = User.objects.create_user(username='testuser', password='password123')
        cls.search_url = reverse('weather:search')
        cls.login_url = reverse('users:login')

    def setUp(self):
        """Выполняется перед каждым тестом. Логиним пользователя."""
        self.client.login(username='testuser', password='password123')

    def test_search_view_get_no_query(self):
        """Тест GET-запроса без параметра 'location'."""
        response = self.client.get(self.search_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/search.html')
        self.assertIsInstance(response.context['search_form'], SearchLocationForm)
        self.assertQuerySetEqual(response.context['locations_dto'], [])
        self.assertIsNone(response.context['error_message'], None)
        self.assertEqual(response.context['query'], '')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Вы ничего не ввели. Введите название локации")
        self.assertContains(response, "Вы ничего не ввели. Введите название локации")

    @patch('weather.services.WeatherAPI.get_locations')
    def test_search_view_get_with_query_success(self, mock_get_locations):
        """Тест GET-запроса с параметром 'location', API возвращает результаты."""
        query = 'London'

        expected_locations = [
            LocationDTO(name='London', latitude=Decimal(51.5074), longitude=Decimal(-0.1278), country='GB'),
            LocationDTO(name='London', latitude=Decimal(42.9834), longitude=Decimal(-81.2330), country='CA')
        ]

        mock_get_locations.return_value = expected_locations

        response = self.client.get(self.search_url, {'location': query})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/search.html')
        mock_get_locations.assert_called_once_with(query)
        self.assertEqual(response.context['query'], query)
        self.assertListEqual(response.context['locations_dto'], expected_locations)
        self.assertIsNone(response.context['error_message'], None)
        self.assertContains(response, 'London')
        self.assertContains(response, 'GB')
        self.assertContains(response, 'CA')

    @patch('weather.services.WeatherAPI.get_locations')
    def test_search_view_get_with_query_not_found(self, mock_get_locations):
        """Тест GET-запроса с 'location', API ничего не находит и возвращает пустой список."""
        query = 'НесуществующаяЛокация'
        mock_get_locations.return_value = []

        response = self.client.get(self.search_url, {'location': query})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/search.html')
        mock_get_locations.assert_called_once_with(query)
        self.assertEqual(response.context['query'], query)
        self.assertListEqual(response.context['locations_dto'], [])
        self.assertIsNone(response.context['error_message'], None)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Локация {query} не найдена')
        self.assertContains(response, f'Локация {query} не найдена')

    @patch('weather.services.WeatherAPI.get_locations')
    def test_search_view_get_with_query_api_error(self, mock_get_locations):
        """Тест GET-запроса с параметром 'location', API возвращает ошибку."""
        query = 'Error Island'
        error_message = 'Тестовая ошибка API'
        mock_get_locations.side_effect = GeocodingApiError(error_message)

        response = self.client.get(self.search_url, {'location': query})
        self.assertEqual(response.status_code, 503)
        self.assertTemplateUsed(response, 'weather/API_error.html')
        mock_get_locations.assert_called_once_with(query)

        self.assertIn('error_message', response.context)
        self.assertEqual(response.context['error_message'], 'Ошибка сервиса при поиске локаций.')

    def test_search_view_requires_login(self):
        """Тест: Анонимный пользователь перенаправляется на страницу входа."""
        self.client.logout()
        response = self.client.get(self.search_url)

        expected_redirect_url = f'{self.login_url}?next={self.search_url}'
        self.assertRedirects(response, expected_redirect_url, status_code=302)
