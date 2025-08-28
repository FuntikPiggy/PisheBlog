from datetime import datetime

from django.http import FileResponse


PRODUCTS = ' {:02}.{} - {}{}'
RECIPES = ' {} ({})'


def save_shopping_file(ingredients, recipes):
    shopping = '\n'.join([
        f'Список покупок (от {datetime.now().strftime("%d.%m.%Y")}):',
        '',
        'Продукты:',
        *[PRODUCTS.format(
            n,
            i["name"].capitalize(),
            i["amount"],
            i["m_unit"]
        ) for n, i in enumerate(ingredients, 1)],
        '',
        'Рецепты:',
        *[RECIPES.format(
            r.recipe.name,
            r.recipe.author.username,
        ) for r in recipes],
    ])
    return FileResponse(shopping, 'shopping.txt')
