from recipes.management.base2db import GetDataFromFileBase
from recipes.models import Ingredient


class Command(GetDataFromFileBase):
    """Класс команды на вставку данных ингредиентов из json в БД"""

    help = 'Импорт ингредиентов из json-файла в БД'
    filename = 'recipes_ingredient'
    klass = Ingredient


if __name__ == '__main__':
    command1 = Command()
    command1.handle()
