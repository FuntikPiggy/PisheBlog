from rest_framework.pagination import PageNumberPagination


class QueryPageNumberPagination(PageNumberPagination):
    """Класс пагинации с размером страницы из параметра запроса."""

    page_size_query_param = 'limit'