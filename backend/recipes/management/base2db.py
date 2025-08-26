import json
import os
import sqlite3
from glob import glob

from django.conf import settings
import psycopg2

from backend.settings import BASE_DIR


def get_json(file_name, tbl_name):
    DBT = os.getenv('DB_PROD_TYPE', False) == 'True'
    if DBT:
        con = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'django'),
            user=os.getenv('POSTGRES_USER', 'django'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            host=os.getenv('DB_HOST', ''),
            port=os.getenv('DB_PORT', ''),
        )
        cur = con.cursor()
        cur.execute("""SELECT table_name
                       FROM information_schema.tables
                       WHERE table_schema = 'public'""")
    else:
        db_path = BASE_DIR / '*.sqlite3'
        db_file = glob('\\'.join(db_path.parts))[0]
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        cur.execute('SELECT name FROM sqlite_master WHERE type="table";')
    with open(
            str(settings.BASE_DIR / 'data' / f'{file_name}.json'),
            'r', encoding='U8'
    ) as ofl:
        dr = json.load(ofl)
        jsn_clmns = list(dr[0].keys())
        to_db = [tuple(i[j] for j in jsn_clmns) for i in dr]
        sql_command = (f'INSERT INTO {tbl_name} '
                       f'({", ".join(jsn_clmns)}) VALUES '
                       f'({", ".join(["?", "%s"][DBT] for _ in jsn_clmns)});')
        try:
            cur.executemany(f'{sql_command}', to_db)
            print(f'Таблица {tbl_name} обновлена!\n')
        except sqlite3.IntegrityError or psycopg2.IntegrityError as e:
            print(f'В таблице {tbl_name} данные не обновлены\n'
                  f'в связи с возникшей ошибкой:\n*** {e}\n')
        con.commit()
        con.close()
