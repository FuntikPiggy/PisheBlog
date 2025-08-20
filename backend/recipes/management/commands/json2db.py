from glob import glob
import json
import os
import sqlite3

from django.core.management.base import BaseCommand
import psycopg2

from backend.settings import BASE_DIR


class Command(BaseCommand):

    help = 'Импорт данных из csv-файлов в БД'

    # Оформляем путь до файлов json (в формате специального объекта)
    json_path = BASE_DIR / 'data/*.json'
    # Создаём список путей к файлам csv (в виде строк)
    json_files = glob('\\'.join(json_path.parts))

    def handle(self, *args, **options):
        # DBT - DateBaseType, True - Postgres, False - SqLite
        DBT = os.getenv('DB_PROD_TYPE', False) == 'True'
        # Создаём объект БД (подключаемся к базе данных)
        if DBT:
            con = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB', 'django'),
                user=os.getenv('POSTGRES_USER', 'django'),
                password=os.getenv('POSTGRES_PASSWORD', ''),
                host=os.getenv('DB_HOST', ''),
                port=os.getenv('DB_PORT', ''),
            )
            # Создаём объект указателя
            cur = con.cursor()
            # Делаем запрос имён всех таблиц
            cur.execute("""SELECT table_name
                           FROM information_schema.tables
                           WHERE table_schema = 'public'""")
        else:
            # Оформляем путь до БД (в формате специального объекта)
            db_path = BASE_DIR / '*.sqlite3'
            # Создаём путь к файлу БД (в виде строки)
            db_file = glob('\\'.join(db_path.parts))[0]
            con = sqlite3.connect(db_file)
            # Создаём объект указателя
            cur = con.cursor()
            # Делаем запрос имён всех таблиц
            cur.execute('SELECT name FROM sqlite_master WHERE type="table";')
        # Оформляем список имён всех таблиц
        db_tables = list(map(lambda x: x[0], cur.fetchall()))
        for file in self.json_files:
            with (open(file, 'r', encoding='U8') as ofl):
                dr = json.load(ofl)
                for table in db_tables:
                    # Делаем запрос всех полей (вообще всей таблицы) таблицы
                    cur.execute(f'SELECT * FROM {table} LIMIT 0')
                    # Оформляем список имён всех столбцов таблицы
                    tbl_clmns = list(map(
                        lambda x: x[0],
                        [description for description in cur.description]
                    ))
                    # Оформляем список имён всех столбцов в текущем файле css
                    jsn_clmns = list(dr[0].keys())
                    # Если все имена столбцов в файле есть в таблице
                    filename = file.split('\\')[-1].split('.')[0]
                    tablename = '_'.join(table.split('_')[1:])
                    if (set(jsn_clmns) <= set(tbl_clmns)
                        and (filename[:-1] == tablename)
                            or filename == tablename):
                        # Оформляем список кортежей из значений
                        # (один кортеж - одна запись таблицы)
                        to_db = [tuple(i[j] for j in jsn_clmns) for i in dr]
                        # Оформляем команду запроса на вставку значений в БД
                        sql_command = (
                            f'INSERT INTO {table} ('
                            f'{", ".join(jsn_clmns)}'
                            f') VALUES ('
                            f'{", ".join(["?", "%s"][DBT] for _ in jsn_clmns)}'
                            f');'
                        )
                        try:
                            # Производим вставку значений,
                            # полученных из файла css в БД
                            cur.executemany(f'{sql_command}', to_db)
                            print(f'Таблица {table} обновлена!\n')
                        except sqlite3.IntegrityError as e:
                            print(f'В таблице {table} данные не обновлены\n'
                                  f'в связи с возникшей ошибкой:\n*** {e}\n')
                        break
        # Сохраняем изменения в БД
        con.commit()
        # Закрываем соединение с БД
        con.close()


if __name__ == '__main__':
    command1 = Command()
    command1.handle()
