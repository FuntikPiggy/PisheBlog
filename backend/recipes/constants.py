# models.py

# Регулярные выражения
USERNAME_REGEX = r"^[\w.@+-]+\Z"
# Максимально-допустимые длины строк
USERNAME_LENGTH = 150
EMAIL_LENGTH = 254
FIRSTNAME_LENGTH = USERNAME_LENGTH
LASTNAME_LENGTH = USERNAME_LENGTH
TAG_NAME_LENGTH = 32
TAG_SLUG_LENGTH = TAG_NAME_LENGTH
INGREDIENT_NAME_LENGTH = 128
INGREDIENT_MEASURE_LENGTH = 64
RECIPE_NAME_LENGTH = 256
# Имена таблиц БД
INGREDIENTS_DB_NAME = 'recipes_ingredient'
TAGS_DB_NAME = 'recipes_tag'
# Имена файлов с данными
INGREDIENTS_FILE_NAME = 'ingredients'
TAGS_FILE_NAME = 'tags'

# Сообщения
USERNAME_VALID = 'Используются только буквы, цифры и символы @/./+/-/_ .'