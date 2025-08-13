from django.db import models

from . import constants

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
        verbose_name='Слаг',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name[:32]=} '
                f'{self.slug[:32]=}')


class Ingredient(models.Model):
    """Модель ингредиента, таблица recipes_ingredient."""

    name = models.CharField(
        max_length=constants.INGREDIENT_NAME_LENGTH,
        unique=True,
        verbose_name='Наименование',
    )
    measurement_unit = models.SlugField(
        max_length=constants.INGREDIENT_MEASURE_LENGTH,
        unique=True,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name[:32]=} '
                f'{self.measurement_unit[:32]=}')