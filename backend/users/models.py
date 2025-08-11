from django.conf import settings
from django.db import models

from . import constants

class YaUser(AbstractUser):
    """Модель пользователя, таблица reviews_yauser."""

    username = models.CharField(
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        validators=(
            UnicodeUsernameValidator(),
            not_me_username_validator,
        ),
        verbose_name='Псевдоним',
        help_text=f'Используются только буквы, цифры и символы @/./+/-/_ .'
                  f'Нельзя использовать "{settings.USERS_URL_SUFFIX}" в '
                  f'качестве имени пользователя, это зарезервированное слово',
    )
    email = models.EmailField(
        max_length=constants.EMAIL_LENGTH,
        unique=True,
        verbose_name='E-mail адрес',
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'users'
        ordering = ('username',)

    def __str__(self):
        return (f'{self.username[:64]=} '
                f'{self.email[:64]=} '
                f'{self.role[:16]=} '
                f'{self.bio[:64]=} ')
