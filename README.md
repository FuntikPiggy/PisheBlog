[![Main PisheBlog workflow](https://github.com/FuntikPiggy/pisheblog/actions/workflows/main.yml/badge.svg)](https://github.com/FuntikPiggy/pisheblog/actions/workflows/main.yml)
<a name="Start-point"></a>
# ПищеБлог<img align="right" width="120" height="42" alt="logo_readme" src="https://github.com/user-attachments/assets/9bc7311a-2f3c-414b-8ed7-463b44a8d3b3" />



* #### [О проекте.](#anchor-about)
* #### [Как запустить проект в контейнерах Docker.](#How-to-run-Docker)
* #### [Как запустить проект локально, без Docker.](#How-to-run-w/o-Docker)
    * [Запуск фронтенда проекта.](#Run-front)
    * [Запуск базы данных проекта.](#Run-db)
    * [Запуск бэкэнда проекта.](#Run-back)
**********


<a name="anchor-about"></a>
## О проекте

### Описание проекта
Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на 
онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления 
блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

<img width="300" height="400" alt="PisheBlog_08" src="https://github.com/user-attachments/assets/2b446e59-5288-418a-b46c-e8405be4003b" />
<img width="300" height="403" alt="PisheBlog_04" src="https://github.com/user-attachments/assets/2c2e435f-d1f8-45a7-a5e7-b5a8a861c9f7" />
<img width="300" height="401" alt="PisheBlog_05" src="https://github.com/user-attachments/assets/6d0d47f1-a3a8-4654-a0a4-bdc3082a3b8d" />
<img width="300" height="403" alt="PisheBlog_06" src="https://github.com/user-attachments/assets/fa43c626-0b1f-4ec3-90c3-db74d825976d" />



Авторы проекта:

Гурин Валерий - ([GitHub](https://github.com/FuntikPiggy), [Telegram](https://t.me/CallSign_Yakuza))


### Технические подробности
Бэкэнд проекта написан на базе фреймворка [Django](https://docs.djangoproject.com/en/5.2/)
и библиотеки [djangoRESTframework](https://www.django-rest-framework.org/)
на языке программирования [Python](https://www.python.org/).
Фронтенд проекта написан на языке программирования [JavaScript](https://nodejs.org/en)
с помощью библиотеки [React](https://react.dev/).
WSGI-сервер - [Gunicorn](https://gunicorn.org/).
Веб-сервер - [Nginx](https://nginx.org/ru/).
Пример заполнения переменных среды - см. файл **.env.example** (в репозитории).

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>


<a name="How-to-run-Docker"></a>
## Как запустить проект в контейнерах Docker:

Клонировать репозиторий и перейти в него в командной строке:


```bash
git clone https://github.com/FuntikPiggy/pisheblog.git

cd pisheblog
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv .venv
```

* Если у вас Linux/macOS

```bash
source .venv/bin/activate
```

* Если у вас windows

```bash
source .venv/Scripts/activate
```

```bash
python3 -m pip install --upgrade pip
```

Перейти в папку "backend":

```bash
cd backend
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

<a name="env-file"></a>
Создать файл .evn для хранения ключей в корне проекта:

```bash
POSTGRES_USER=<имя пользователя БД>
POSTGRES_PASSWORD=<пароль БД>
POSTGRES_DB=<имя БД>
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=<секретный ключ Django>
DJANGO_ALLOWED_HOSTS=<имя или IP-адрес хоста>
DEBUG_MODE=  # Любая строка == True, не заполнено == False
DB_PROD_TYPE=True  # Любая строка == True (для Postgres), не заполнено == False(для SQLite)
CSRF_TRUSTED='<https://subdomain.example.com>'  # Ваш адрес
```

Из папки "pisheblog" запустить проект:

```bash
cd ..
docker compose up
```

Выполнить миграции, сбор статики:


```bash
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

Наполнить базу данных ингредиентами и тэгами:


```bash
sudo docker compose exec backend python manage.py ing2db
sudo docker compose exec backend python manage.py tag2db
```

При необходимости создать суперпользователя (далее следовать указаниям и ввести требуемые данные):


```bash
sudo docker compose exec backend python manage.py createsuperuser
```

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>

<a name="How-to-run-w/o-Docker"></a>
## Как запустить проект без Docker:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/FuntikPiggy/pisheblog.git

cd pisheblog
```

Создать файл .evn для хранения ключей в корне проекта (пример заполнения смотри [выше](#env-file)).


<a name="Run-front"></a>
### Запуск фронтенда проекта:
Установите [Node.js](https://nodejs.org/en/about/previous-releases#looking-for-latest-release-of-a-version-branch) версии v24.1.0.
```

Перейдите в директорию "frontend" проекта:

```bash
cd frontend
```

Установите зависимости:

```bash
npm i
```

Откройте в редакторе файл "package.json" из папки "frontend" и в конце файла замените
"web" на "localhost":

```bash
"proxy": "http://web:8000/"    -->    "proxy": "http://localhost:8000/"
```

Фронтенд готов к запуску. Запустите его:

```bash
npm run start
```

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>

<a name="Run-db"></a>
### Запуск базы данных проекта:

Создать БД [Postgres](https://www.postgresql.org/download/windows/):
Находясь в папке backend (где лежит файл manage.py), введите команду: 

```bash
python manage.py migrate
```

Создать пользователя и наделить его правами:


```bash
CREATE USER django_user WITH PASSWORD 'mysecretpassword';
GRANT ALL ON DATABASE django TO django_user;
ALTER DATABASE django OWNER TO django_user;
GRANT USAGE, CREATE ON SCHEMA PUBLIC TO django_user;
```

Перейти в папку "backend":

```bash
cd ../backend
```

Наполнить базу данных ингредиентами и тэгами:

```bash
python manage.py ing2db
python manage.py tag2db
```

При необходимости создать суперпользователя (далее следовать указаниям и ввести требуемые данные):

```bash
python manage.py createsuperuser
```

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>

<a name="Run-back"></a>
### Запуск бэкэнда проекта:

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv .venv
```

* Если у вас Linux/macOS

```bash
source .venv/bin/activate
```

* Если у вас windows

```bash
source .venv/Scripts/activate
```

```bash
python3 -m pip install --upgrade pip
```

Перейти в папку "backend":

```
cd backend
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

```
python manage.py runserver
```

Основные точки доступа развёрнутого локально проекта:

[Главная страница сайта](http://127.0.0.1:3000/)

[Админ-панель](http://127.0.0.1:8000/admin/)

[API-панель](http://127.0.0.1:8000/api/)

[Документация к API](http://127.0.0.1:8000/api/docs/)

<p align="right"><a href="#Start-point">Вернуться к началу</a></p>
