import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import ForeignKey

from . import constants
from .constants import USERNAME_VALID, USERNAME_REGEX


class FoodgramUser(AbstractUser):
    """Модель пользователя, таблица users_fguser."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    username = models.CharField(
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        validators=(RegexValidator(
            regex = USERNAME_REGEX,
            message=USERNAME_VALID,
            flags = re.ASCII
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
    """Модель тэга, таблица recipes_tag."""

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
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name[:32]=} '
                f'{self.slug=}')


class Ingredient(models.Model):
    """Модель ингредиента, таблица recipes_ingredient."""

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
        validators=(
            MinValueValidator(1),
        )
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,

        default=None,
        verbose_name='Изображение',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
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

    @property
    def in_shopping_cart(self, user):
        return user.purchases.filter(user_id=user.id, recipe_id=self.id).exists()


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента, таблица recipes_recipeingredient."""

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
            MinValueValidator(1),
        ),
        verbose_name='Количество',
    )

    class Meta:
        default_related_name = 'recipeingredients'
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)

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


class Purchase(UserFavoriteBase):
    """Модель связи пользователя и рецепта,
    таблица recipes_userpurchase."""


class Followings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following',),
                name='unique_following',
            ),
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'