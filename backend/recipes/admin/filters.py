from django.contrib import admin
from django.db.models import Sum, Count


class SubsFilterBase(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        return [(1, 'Да'), (0, 'Нет'),]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(
                **{f'{self.parameter_name}__isnull':False}).distinct()
        elif self.value() == '0':
            return queryset.filter(**{f'{self.parameter_name}__isnull':True})


class HasRecipes(SubsFilterBase):
    title = 'Есть рецепты'
    parameter_name = 'recipes'


class HasSubscriptions(SubsFilterBase):
    title = 'Есть подписки'
    parameter_name = 'subscriptions'


class HasFollowers(SubsFilterBase):
    title = 'Есть подписчики'
    parameter_name = 'followers'


class IsInRecipe(SubsFilterBase):
    title = 'Есть в рецептах'
    parameter_name = 'recipes'


class IsInFavorites(SubsFilterBase):
    title = 'Добавлен в избранное'
    parameter_name = 'favorites'


class CookTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'time'

    def __init__(self, *args, **kwargs):
        queryset = args[2].objects.all()
        self.n = max(20, int(queryset.aggregate(
            time=Sum('cooking_time')/Count('cooking_time')
        )['time'] / 3 * 2 / 5 + 0.5) * 5)
        self.m = self.n * 2
        super().__init__(*args, **kwargs)


    def lookups(self, request, model_admin):
        return [
            (0, f'<{self.n}мин.'),
            (1, f'{self.n}-{self.m}мин.'),
            (2, f'>{self.m}мин.'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(cooking_time__lt=self.n)
        elif self.value() == '1':
            return queryset.filter(cooking_time__range=(self.n,self.m))
        elif self.value() == '2':
            return queryset.filter(cooking_time__gt=self.m)