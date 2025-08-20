[![Main Foodgram workflow](https://github.com/FuntikPiggy/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/FuntikPiggy/foodgram/actions/workflows/main.yml)

# FoodGram

[О проекте.](#anchor-about)<br/>
[Как запустить проект.](#How-to-run)<br/>
<br/>

<a name="anchor-about"></a>
## О проекте

### Описание проекта
Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на 
онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления 
блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

Авторы проекта:

Гурин Валерий - (GitHub - [FuntikPiggy](https://github.com/FuntikPiggy))
А так же неизвестные авторы фронтенда, но тоже молодцы...


### Технические подробности
Бэкэнд проекта написан на базе фреймворка [Django](https://docs.djangoproject.com/en/5.2/)
и библиотеки [djangoRESTframework](https://www.django-rest-framework.org/)
на языке программирования [Python](https://www.python.org/).
Фронтенд проекта написан на языке программирования [JavaScript](https://nodejs.org/en)
с помощью библиотеки [React](https://react.dev/).
WSGI-сервер - [Gunicorn](https://gunicorn.org/).
Веб-сервер - [Nginx](https://nginx.org/ru/).
Пример заполнения переменных среды - см. файл **.env.example** (в репозитории).


<a name="How-to-run"></a>
## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/FuntikPiggy/kittygram_final.git

cd kittygram_final
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
```

Запустить проект:

```
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:


```
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

Если в базе данных нужны будут тестовые исходные данные, то скопировать медиа-файлы:


```
sudo docker compose exec backend cp -r /app/data/images/. /app/media/
```

Наполнить базу данных тестовыми данными и ингредиентами (файл с ингредиентами - ingredients.json,
если тестовые данные не нужны, можно убрать остальные файлы из папки data):


```
sudo docker compose exec backend python manage.py loaddata ./data/indented_db.json
```

При необходимости создать суперпользователя (далее следовать указаниям и ввести требуемые данные):


```
sudo docker compose exec backend python manage.py createsuperuser
```

Тестовые данные пользователей:
1. Admin: email - vg@mail.ru, password - 1234
2. User: email - ii@mail.ru, password - 1234
3. User: email - ap@mail.ru, password - 1234
4. User: email - os@mail.ru, password - 1234