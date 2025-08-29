from recipes.management.base2db import GetDataFromFileBase
from recipes.models import Tag


class Command(GetDataFromFileBase):
    """Класс команды на вставку данных тегов из json в БД"""

    help = 'Импорт тегов из json-файла в БД'
    filename = 'recipes_tag'
    model = Tag
