from datetime import datetime

from django.http import HttpResponse


def save_shopping_file(ingredients, recipes):
    [i.update({'length': 40 - len(str(i["amount"])) - len(i["m_unit"])})
     for i in ingredients]
    [r.update({'length': 41 - len(r["author"])}) for r in recipes]
    shopping = '\n'.join([
        f'Список покупок (от {datetime.now().strftime("%d.%m.%Y")}):',

        '\nПродукты:',

        *[f' {n:02}.{i["name"].capitalize():.<{i["length"]}}'
          f'{i["amount"]}{i["m_unit"]}'
          for n, i in enumerate(ingredients)],

        '\nРецепты:',
        *[f' {r['name'][:30]:.<{r["length"]}}({r['author']})'
          for r in recipes],

    ])
    return HttpResponse(shopping, content_type='text/plain')
