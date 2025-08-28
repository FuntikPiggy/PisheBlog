import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import ForeignKey

from . import constants
from .constants import (USERNAME_VALID, USERNAME_REGEX,
                        MIN_COOK_TIME, MIN_AMOUNT)


class FoodgramUser(AbstractUser):
    """Модель пользователя, таблица users_fguser."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    username = models.CharField(
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        validators=(RegexValidator(
            regex=USERNAME_REGEX,
            message=USERNAME_VALID,
            flags=re.ASCII
        ),),
        verbose_name='Псевдоним',
        help_text=USERNAME_VALID,
    )
    first_name = models.CharField(
        max_length=constants.FIRSTNAME_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=constants.LASTNAME_LENGTH,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=constants.EMAIL_LENGTH,
        unique=True,
        verbose_name='E-mail адрес',
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        default=None,
        verbose_name='Аватар',
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
                f'{self.email[:64]=}')


User = get_user_model()


class Tag(models.Model):
    """Модель тега, таблица recipes_tag."""

    name = models.CharField(
        max_length=constants.TAG_NAME_LENGTH,
        unique=True,
        verbose_name='Наименование',
    )
    slug = models.SlugField(
        max_length=constants.TAG_SLUG_LENGTH,
        unique=True,
        null=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name=} '
                f'{self.slug=}')


class Ingredient(models.Model):
    """Модель продукта, таблица recipes_ingredient."""

    name = models.CharField(
        max_length=constants.INGREDIENT_NAME_LENGTH,
        verbose_name='Наименование',
    )
    measurement_unit = models.SlugField(
        max_length=constants.INGREDIENT_MEASURE_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return (f'{self.name[:32]=} '
                f'{self.measurement_unit[:32]=}')


class Recipe(models.Model):
    """Модель рецепта, таблица recipes_recipe."""

    name = models.CharField(
        max_length=constants.RECIPE_NAME_LENGTH,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        null=False,
        blank=False,
        validators=(
            MinValueValidator(MIN_COOK_TIME),
        )
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        blank=False,
        default=None,
        verbose_name='Изображение',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return (f'{self.name[:32]=}'
                f'{self.author=}'
                f'{self.pub_date=}'
                f'{self.tags=} ')


class RecipeIngredient(models.Model):
    """Модель связи рецепта и продукта, таблица recipes_recipeingredient."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(MIN_AMOUNT),
        ),
        verbose_name='Количество',
    )

    class Meta:
        default_related_name = 'recipeingredients'
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return (f'{self.recipe.name[:32]=} '
                f'{self.ingredient.name[:32]=} '
                f'{self.amount=}')


class UserFavoriteBase(models.Model):
    """Базовый класс для моделей связи пользователей и
    рецептов для логики избранного и корзины покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_%(class)s',
            ),
        )

    def __str__(self):
        return (f'{self.user.username[:32]=} '
                f'{self.recipe.name[:32]=}')


class Favorite(UserFavoriteBase):
    """Модель связи пользователя и рецепта, таблица recipes_userfavorite."""

    class Meta(UserFavoriteBase.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class Purchase(UserFavoriteBase):
    """Модель связи пользователя и рецепта,
    таблица recipes_userpurchase."""

    class Meta(UserFavoriteBase.Meta):
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'Корзины покупок'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_added',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_recieved',
        verbose_name='Автор',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscription',
            ),
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
