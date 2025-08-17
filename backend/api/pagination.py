from functools import wraps

from rest_framework.pagination import PageNumberPagination


class QueryPageNumberPagination(PageNumberPagination):
    """Класс пагинации с размером страницы из параметра запроса."""

    page_size_query_param = 'limit'


def paginated(func):
    """Декоратор для пагинации actions."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        queryset = func(self, *args, **kwargs)
        page = self.paginate_queryset(queryset)
        # if page is not None:
            # serializer = self.get_serializer(page, many=True)
            # return self.get_paginated_response(serializer.data)
        return self.get_paginated_response(page)
        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)
        # return Response(page)
    return wrapper