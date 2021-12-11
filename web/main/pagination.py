from rest_framework.pagination import PageNumberPagination, CursorPagination


class BasePageNumberPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 100
    page_size_query_param = 'page_size'


class BaseCursorPagination(CursorPagination):
    ordering = 'id'
    page_size = 10
