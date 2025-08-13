from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
# from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

# from .validators import not_me_username_validator
from . import constants


# class CustomUserManager(UserManager):
#
#     def get_by_natural_key(self, username):
#         return self.get(
#             models.Q(**{self.model.USERNAME_FIELD: username}) |
#             models.Q(**{self.model.EMAIL_FIELD: username})
#         )


class FgUser(AbstractUser):
    """Модель пользователя, таблица users_fguser."""

    # objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    username = models.CharField(
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        # validators=(
        #     UnicodeUsernameValidator(),
        #     not_me_username_validator,
        # ),
        verbose_name='Псевдоним',
        help_text=f'Используются только буквы, цифры и символы @/./+/-/_ .'
                  # f'Нельзя использовать "{settings.USERS_URL_SUFFIX}" в '
                  # f'качестве имени пользователя, это зарезервированное слово',
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
        # through='Subscriptions',
        symmetrical=False,
        related_name='follower',
    )

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


User = get_user_model()


# class Subscriptions(models.Model):
#     follower = models.ForeignKey(
#         User,
#         on_delete=models.DO_NOTHING,
#         related_name='following'
#     )
#     following = models.ForeignKey(
#         User,
#         on_delete=models.DO_NOTHING,
#         related_name='followers'
#     )
#     following_since = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return (f'{self.follower} подписан на '
#                 f'{self.following} с {self.following_since}')
