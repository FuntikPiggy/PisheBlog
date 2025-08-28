from recipes.management.base2db import GetDataFromFileBase
from recipes.models import Ingredient


class Command(GetDataFromFileBase):
    """Класс команды на вставку данных о продуктах из json в БД"""

    help = 'Импорт продуктов из json-файла в БД'
    filename = 'ingredients'
    klass = Ingredient
