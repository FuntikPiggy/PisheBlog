from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe
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
        related_name='followers',
    )
    favorites = models.ManyToManyField(
        Recipe,
        through='Favorites',
    )
    shopping_cart = models.ManyToManyField(
        Recipe,
        through='ShoppingCart',
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


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return (f'{self.user.username[:32]=} '
                f'{self.recipe.name[:32]=}')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return (f'{self.user.username[:32]=} '
                f'{self.recipe.name[:32]=}')
