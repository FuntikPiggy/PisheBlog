from django.conf import settings

from django.core.exceptions import ValidationError


def not_me_username_validator(username):
    if username == settings.SERS_URL_SUFFIX:
        raise ValidationError(
            f'Укажите корректное имя. Нельзя использовать '
            f'"{settings.USERS_URL_SUFFIX}" в качестве имени,'
            f'это зарезервированное слово.'
        )
    return username