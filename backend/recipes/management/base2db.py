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
                old_len = self.model.objects.all().count()
                self.model.objects.bulk_create(
                    [self.model(**i) for i in json.load(ofl)],
                    ignore_conflicts=True,
                )
                print(f'В таблицу {self.model._meta.verbose_name_plural} '
                      f'добавлено {self.model.objects.all().count() - old_len}'
                      f' записей!\n')
        except Exception as e:
            print(f'В таблице "{self.model._meta.verbose_name_plural}" данные '
                  f'не обновлены\n в связи с возникшей ошибкой:\n*** {e}\n')
