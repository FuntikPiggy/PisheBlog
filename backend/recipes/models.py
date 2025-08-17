from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ForeignKey

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
        default=None,
        verbose_name='Аватар',
    )
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        verbose_name='Подписки',
    )
    favorites = models.ManyToManyField(
        'Recipe',
        through='UserFavorites',
        related_name='fans',
        verbose_name='В избранном',
    )
    shopping_cart = models.ManyToManyField(
        'Recipe',
        through='UserShoppingCart',
        related_name='buyers',
        verbose_name='В списке покупок',
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
                f'{self.slug[:32]=}')


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
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name[:32]=} '
                f'{self.measurement_unit[:32]=}')


class CookingTimeField(models.PositiveSmallIntegerField):
    """Формат поля для времени приготовления >=1."""

    def formfield(self, **kwargs):
        return super(
            models.PositiveSmallIntegerField,
            self
        ).formfield(**{"min_value": 1, **kwargs,})


class Recipe(models.Model):
    """Модель рецепта, таблица recipes_recipe."""

    name = models.CharField(
        max_length=constants.RECIPE_NAME_LENGTH,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    cooking_time = CookingTimeField(
        verbose_name='Время приготовления',
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name = 'Автор',
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
        through='RecipeTag',
        verbose_name='Тэги',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)
        default_related_name = 'recipes'

    def __str__(self):
        return (f'{self.name[:32]=} '
                f'{self.ingredients.__str__()=}'
                f'{self.tags.__str__()=}')


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return (f'{self.recipe.name[:32]=} '
                f'{self.tag.name[:32]=}')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,)
    amount = models.PositiveSmallIntegerField()

    class Meta:
        default_related_name = 'recipeingredients'

    def __str__(self):
        return (f'{self.recipe.name[:32]=} '
                f'{self.ingredient.name[:32]=}')


class UserFavorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)# related_name='favorited_by')

    def __str__(self):
        return (f'{self.user.username[:32]=} '
                f'{self.recipe.name[:32]=}')


class UserShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)# related_name='carted_by')

    def __str__(self):
        return (f'{self.user.username[:32]=} '
                f'{self.recipe.name[:32]=}')
