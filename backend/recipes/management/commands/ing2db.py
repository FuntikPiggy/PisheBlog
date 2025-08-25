from django.core.management import BaseCommand

from recipes.constants import INGREDIENTS_DB_NAME, INGREDIENTS_FILE_NAME
from recipes.management.base2db import get_json


class Command(BaseCommand):
    """Класс команды на вставку данных из json в БД"""

    help = 'Импорт ингредиентов из json-файла в БД'

    def handle(self, *args, **options):
        get_json(INGREDIENTS_FILE_NAME, INGREDIENTS_DB_NAME)

if __name__ == '__main__':
    command1 = Command()
    command1.handle()
