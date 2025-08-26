from django.shortcuts import redirect, get_object_or_404

from recipes.models import Recipe


def short_link(request, recipe_id):
    """Функция представления для декодирования коротких ссылок."""
    get_object_or_404(Recipe, id=recipe_id)
    return redirect(f'/recipes/{recipe_id}')
