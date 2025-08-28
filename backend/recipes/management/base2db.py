import json

from django.conf import settings
from django.core.management import BaseCommand


class GetDataFromFileBase(BaseCommand):
    """Базовый класс для команд загрузки данных из json в БД"""

    def handle(self, *args, **options):
        try:
            with open(
                    settings.BASE_DIR / 'data' / f'{self.filename}.json',
                    'r', encoding='U8',
            ) as ofl:
                rows = [self.klass(**i) for i in json.load(ofl)]
                self.klass.objects.bulk_create(
                    rows, ignore_conflicts=True,
                )
                print(f'В таблицу {self.klass._meta.verbose_name_plural} '
                      f'добавлено {len(rows)} записей!\n')
        except Exception as e:
            print(f'В таблице "{self.klass._meta.verbose_name_plural}" данные '
                  f'не обновлены\n в связи с возникшей ошибкой:\n*** {e}\n')
