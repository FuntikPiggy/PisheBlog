from django.contrib import admin
from django.db.models import Sum, Count


class SubsFilterBase(admin.SimpleListFilter):
    """Базовый класс для фильтров."""

    LOOK_UPS = [(1, 'Да'), (0, 'Нет')]

    def lookups(self, request, model_admin):
        return self.LOOK_UPS

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(
                **{f'{self.parameter_name}__isnull': False}).distinct()
        elif self.value() == '0':
            return queryset.filter(**{f'{self.parameter_name}__isnull': True})


class HasRecipes(SubsFilterBase):
    """Фильтр по наличию рецептов, связанных с объектом."""

    title = 'Есть рецепты'
    parameter_name = 'recipes'


class HasSubscriptions(SubsFilterBase):
    """Фильтр по наличию подписок на других пользователей."""

    title = 'Есть подписки'
    parameter_name = 'subscriptions_added'


class HasFollowers(SubsFilterBase):
    """Фильтр по наличию подписок других пользователей на текущего."""

    title = 'Есть подписчики'
    parameter_name = 'subscriptions_recieved'


class IsInRecipe(SubsFilterBase):
    """Фильтр по наличию продукта в рецептах."""

    title = 'Есть в рецептах'
    parameter_name = 'recipes'


class IsInFavorites(SubsFilterBase):
    """Фильтр по наличию рецепта в списках избранного."""

    title = 'Добавлен в избранное'
    parameter_name = 'favorites'


class CookTimeFilter(admin.SimpleListFilter):
    """Фильтр по времени приготовления."""

    title = 'Время приготовления'
    parameter_name = 'time'

    def lookups(self, request, model_admin):
        queryset = model_admin.model.objects.all()
        self.lower_limit = max(20, (queryset.aggregate(
            time=Sum('cooking_time') / Count('cooking_time')
        )['time'] // 3 * 2 // 5 + 1) * 5)
        self.upper_limit = self.lower_limit * 2
        return [
            (0, f'<{self.lower_limit}мин.'),
            (1, f'{self.lower_limit}-{self.upper_limit}мин.'),
            (2, f'>{self.upper_limit}мин.'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(cooking_time__lt=self.lower_limit)
        elif self.value() == '1':
            return queryset.filter(cooking_time__range=(self.lower_limit, self.upper_limit))
        elif self.value() == '2':
            return queryset.filter(cooking_time__gt=self.upper_limit)
        return queryset
