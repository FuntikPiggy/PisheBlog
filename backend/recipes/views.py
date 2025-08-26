from django.shortcuts import redirect


def short_link(request, recipe_id):
    """Функция представления для декодирования коротких ссылок."""
    return redirect(f'/recipes/{recipe_id}')
