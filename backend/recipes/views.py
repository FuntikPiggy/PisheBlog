from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe


def short_link(request, recipe_id):
    """Функция представления для декодирования коротких ссылок."""
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise Http404(f'Рецепта с id {recipe_id} в базе нет')
    return redirect(f'/recipes/{recipe_id}')
