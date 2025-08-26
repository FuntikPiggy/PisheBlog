[![Main Foodgram workflow](https://github.com/FuntikPiggy/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/FuntikPiggy/foodgram/actions/workflows/main.yml)

# FoodGram

## [О проекте.](#anchor-about)<br/>
## [Как запустить проект в контейнерах Docker.](#How-to-run-Docker)<br/>
## [Как запустить проект локально, без Docker.](#How-to-run w/o-Docker)<br/>
### [Запуск фронтенда проекта.](#Run-front)<br/>
### [Запуск базы данных проекта.](#Run-db)<br/>
### [Запуск бэкэнда проекта.](#Run-back)<br/>
<br/>

<a name="anchor-about"></a>
## О проекте

### Описание проекта
Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на 
онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления 
блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

Авторы проекта:

Гурин Валерий - (GitHub - [FuntikPiggy](https://github.com/FuntikPiggy))


### Технические подробности
Бэкэнд проекта написан на базе фреймворка [Django](https://docs.djangoproject.com/en/5.2/)
и библиотеки [djangoRESTframework](https://www.django-rest-framework.org/)
на языке программирования [Python](https://www.python.org/).
Фронтенд проекта написан на языке программирования [JavaScript](https://nodejs.org/en)
с помощью библиотеки [React](https://react.dev/).
WSGI-сервер - [Gunicorn](https://gunicorn.org/).
Веб-сервер - [Nginx](https://nginx.org/ru/).
Пример заполнения переменных среды - см. файл **.env.example** (в репозитории).


<a name="How-to-run-Docker"></a>
## Как запустить проект в контейнерах Docker:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/FuntikPiggy/foodgram.git

cd foodgram
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv .venv
```

* Если у вас Linux/macOS

```
source .venv/bin/activate
```

* Если у вас windows

```
source .venv/Scripts/activate
```

```
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

Создать файл .evn для хранения ключей в корне проекта:

```
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

Из папки "foodgram" запустить проект:

```
cd ..
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:


```
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

Наполнить базу данных ингредиентами и тэгами:


```
sudo docker compose exec backend python manage.py ing2db
sudo docker compose exec backend python manage.py tag2db
```

При необходимости создать суперпользователя (далее следовать указаниям и ввести требуемые данные):


```
sudo docker compose exec backend python manage.py createsuperuser
```

<a name="How-to-run-w/o-Docker"></a>
## Как запустить проект без Docker:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/FuntikPiggy/foodgram.git

cd foodgram
```

Создать файл .evn для хранения ключей в корне проекта:

```
POSTGRES_USER=<имя пользователя БД>
POSTGRES_PASSWORD=<пароль БД>
POSTGRES_DB=<имя БД>
DB_HOST=db
DB_PORT=5430
DJANGO_SECRET_KEY=<секретный ключ Django>
DJANGO_ALLOWED_HOSTS=<имя или IP-адрес хоста>
DEBUG_MODE=  # Любая строка == True, не заполнено == False
DB_PROD_TYPE=True  # Любая строка == True (для Postgres), не заполнено == False(для SQLite)
CSRF_TRUSTED='<https://subdomain.example.com>'  # Ваш адрес
```

<a name="Run-front"></a>
### Запуск фронтенда проекта:
Установите Node.js версии v24.1.0, используя дистрибутивы и инструкции с [официального сайта проекта](https://nodejs.org/en/about/previous-releases#looking-for-latest-release-of-a-version-branch).
После установки, проверьте, появился ли npm на вашем компьютере. Выполните в терминале команду:

```
npm -v
```

Перейдите в директорию "frontend" проекта:

```
cd frontend
```

Установите зависимости:

```
npm i
```

Откройте в редакторе файл "package.json" из папки "frontend" и в конце файла замените
"web" на "localhost":

```
"proxy": "http://web:8000/"  -->  "proxy": "http://localhost:8000/"
```

Фронтенд готов к запуску. Запустите его:

```
npm run start
```

<a name="Run-bd"></a>
### Запуск базы данных проекта:

Создать БД [Postgres](https://www.postgresql.org/download/windows/):
Войти в консоль postgres, введя пароль пользователя (указывали при установке): 

```
psql -U postgres
```

Создать БД: 

```
CREATE DATABASE django;
```

Создать пользователя и наделить его правами:


```
CREATE USER django_user WITH PASSWORD 'mysecretpassword';
GRANT ALL ON DATABASE django TO django_user;
ALTER DATABASE django OWNER TO django_user;
GRANT USAGE, CREATE ON SCHEMA PUBLIC TO django_user;
```

Перейти в папку "backend":

```
cd ../backend
```

Наполнить базу данных ингредиентами и тэгами:

```
python manage.py ing2db
python manage.py tag2db
```

При необходимости создать суперпользователя (далее следовать указаниям и ввести требуемые данные):

```
python manage.py createsuperuser
```

<a name="Run-back"></a>
### Запуск бэкэнда проекта:

Cоздать и активировать виртуальное окружение:

```
python3 -m venv .venv
```

* Если у вас Linux/macOS

```
source .venv/bin/activate
```

* Если у вас windows

```
source .venv/Scripts/activate
```

```
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

```
[Главная страница сайта](http://127.0.0.1:3000/)
[Админ-панель](http://127.0.0.1:8000/admin/)
[API-панель](http://127.0.0.1:8000/api/)
[Документация ReDoc](http://127.0.0.1:8000/redoc/)
[Документация Swagger](http://127.0.0.1:8000/swagger/)
```