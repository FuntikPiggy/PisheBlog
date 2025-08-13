from django.contrib.auth.models import AbstractUser
from django.db import models

from . import constants


class FgUser(AbstractUser):
    """Модель пользователя, таблица users_fguser."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    username = models.CharField(
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        verbose_name='Псевдоним',
        help_text=f'Используются только буквы, цифры и символы @/./+/-/_ .',
    )
    email = models.EmailField(
        max_length=constants.EMAIL_LENGTH,
        unique=True,
        verbose_name='E-mail адрес',
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        default=None
    )
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='follower',
    )
    # subscriptions = models.ManyToManyField(
    #     'self',
    #     symmetrical=False,
    #     related_name='follower',
    # )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'users'
        ordering = ('username',)

    def __str__(self):
        return (f'{self.username[:64]=} '
                f'{self.first_name[:64]=} '
                f'{self.last_name[:64]=} '
                f'{self.email[:64]=} ')
