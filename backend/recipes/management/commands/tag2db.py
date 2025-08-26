from recipes.management.base2db import GetDataFromFileBase
from recipes.models import Tag


class Command(GetDataFromFileBase):
    """Класс команды на вставку данных тэгов из json в БД"""

    help = 'Импорт ингредиентов из json-файла в БД'
    filename = 'recipes_tag'
    klass = Tag


if __name__ == '__main__':
    command1 = Command()
    command1.handle()
