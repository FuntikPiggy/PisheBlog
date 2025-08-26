import json
import psycopg2
import sqlite3

from django.conf import settings
from django.core.management import BaseCommand


class GetDataFromFileBase(BaseCommand):
    """Базовый класс для команд загрузки данных из json в БД"""

    def handle(self, *args, **options):
        with open(str(settings.BASE_DIR / 'data' / f'{self.filename}.json'),
                'r', encoding='U8') as ofl:
            try:
                self.klass.objects.bulk_create(
                    self.klass(**i) for i in json.load(ofl)
                )
                print(f'Таблица "Ингредиенты" обновлена!\n')
            except sqlite3.IntegrityError or psycopg2.IntegrityError as e:
                print(f'В таблице "Ингредиенты" данные не обновлены\n'
                      f'в связи с возникшей ошибкой:\n*** {e}\n')
