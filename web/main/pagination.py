from rest_framework.pagination import CursorPagination, PageNumberPagination


class BasePageNumberPagination(PageNumberPagination):
    page_size = 9
    page_query_param = 'page'
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data.update(self.get_html_context())
        return response


class BaseCursorPagination(CursorPagination):
    ordering = 'id'
    page_size = 10
