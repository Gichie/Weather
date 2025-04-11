from django.contrib.auth import get_user_model, SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
from django.test import TestCase, override_settings
from django.urls import reverse
from freezegun import freeze_time

from WeatherApp import settings
from users.forms import LoginUserForm

User = get_user_model()


class LoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.signup_url = reverse('users:register')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.home_url = reverse('weather:home')
        cls.valid_username = 'testuser'
        cls.valid_password = 'password123'
        cls.valid_email = 'test@sobaka.gav'
        cls.valid_login_data = {'username': cls.valid_username, 'password': cls.valid_password}

    def test_login_view_get(self):
        """Тест: Доступность страницы входа (GET)."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertContains(response, 'Авторизация')
        self.assertIsInstance(response.context['form'], LoginUserForm)

    def test_successful_login_creates_session(self):
        """Тест: Успешный вход создает сессию для пользователя."""
        user = User.objects.create_user(username=self.valid_username, password=self.valid_password)

        self.assertNotIn(SESSION_KEY, self.client.session)

        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL), 302)

        self.assertIn(SESSION_KEY, self.client.session)
        self.assertIn(BACKEND_SESSION_KEY, self.client.session)
        self.assertIn(HASH_SESSION_KEY, self.client.session)
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

    def test_unsuccessful_login_invalid_password(self):
        """Тест: Неудачный вход (неправильный пароль)."""
        User.objects.create(username=self.valid_username, password=self.valid_password)

        login_data = {'username': self.valid_username, 'password': 'invalid_password'}

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertNotIn(SESSION_KEY, self.client.session)
        expected_error = 'Пожалуйста, введите правильные имя пользователя и пароль. Оба поля могут быть чувствительны к регистру.'
        self.assertContains(response, expected_error)
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertTrue(response.context['form'].non_field_errors()[0], expected_error)

    def test_unsuccessful_login_invalid_password(self):
        """Тест: Неудачный вход (пользователя не существует)."""
        login_data = {'username': 'non_exist_username', 'password': 'non_exist_password'}

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertNotIn(SESSION_KEY, self.client.session)
        expected_error = 'Пожалуйста, введите правильные имя пользователя и пароль. Оба поля могут быть чувствительны к регистру.'
        self.assertContains(response, expected_error)
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertTrue(response.context['form'].non_field_errors()[0], expected_error)

    def test_logout_destroys_session(self):
        """Тест: Выход из системы удаляет сессию."""
        User.objects.create_user(username=self.valid_username, password=self.valid_password)

        self.client.post(self.login_url, self.valid_login_data)

        self.assertIn(SESSION_KEY, self.client.session)

        response = self.client.post(self.logout_url)

        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            fetch_redirect_response=True,
        )

        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(SESSION_COOKIE_AGE=60, SESSION_EXPIRE_AT_BROWSER_CLOSE=False)
    @freeze_time("2022-02-24 10:00:00")
    def test_session_expiry(self):
        """
        Тест: Проверка, что сессия истекает согласно настройкам.
        """

        User.objects.create_user(username=self.valid_username, password=self.valid_password)
        # Логинимся (в "10:00:00")
        self.client.post(self.login_url, self.valid_login_data)
        self.assertIn(SESSION_KEY, self.client.session)

        # "Перематываем" время на 61 секунду вперед
        with freeze_time('2022-02-24 10:01:01'):
            response = self.client.get(self.home_url)

            expected_url = f'{self.login_url}?next={self.home_url}'
            self.assertRedirects(response, expected_url, 302)
            self.assertNotIn(SESSION_KEY, self.client.session)
