import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f"Успешный вход: Пользователь '{user.username}' (ID: {user.pk}) вошел с IP: {ip}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = ip = request.META.get('REMOTE_ADDR')
    username = credentials.get('username', None)
    logger.warning(f"Неудачная попытка входа: Для пользователя '{username}' с IP: {ip}")


@receiver(post_save, sender=User)
def log_user_registered(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Успешная регистрация: Новый пользователь '{instance.username}' (ID: {instance.pk}) зарегистрирован.")
