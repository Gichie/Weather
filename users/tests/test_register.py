import logging

from django.contrib.auth import get_user_model, SESSION_KEY
from django.test import TestCase
from django.urls import reverse

from users.forms import RegisterUserForm

User = get_user_model()
logging.disable()


class UserRegistrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.signup_url = reverse('users:register')
        cls.login_url = reverse('users:login')
        cls.valid_username = 'testuser'
        cls.valid_password = 'testpassword123'
        cls.valid_email = 'test@sobaka.kal'

    def test_registration_view_get(self):
        """Тест: Доступность страницы регистрации (GET)."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'Регистрация')
        self.assertIsInstance(response.context['form'], RegisterUserForm)

    def test_successful_registration_creates_user(self):
        """Тест: Успешная регистрация создает новую запись User."""
        initial_user_count = User.objects.count()
        sign_up_data = {
            'username': self.valid_username, 'email': self.valid_email,
            'password': self.valid_password, 'password2': self.valid_password,
        }

        response = self.client.post(self.signup_url, sign_up_data)

        # 1. Проверка редиректа
        self.assertRedirects(response, self.login_url, 302)

        # 2. Проверка создания пользователя в БД
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        new_user = User.objects.get(username=self.valid_username)
        self.assertEqual(new_user.email, self.valid_email)
        self.assertTrue(new_user.check_password(self.valid_password))
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)
        self.assertTrue(new_user.is_active)
        self.assertNotIn(SESSION_KEY, self.client.session)
