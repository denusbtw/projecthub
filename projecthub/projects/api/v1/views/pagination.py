from rest_framework import pagination


class ProjectPagination(pagination.PageNumberPagination):
    page_size = 30
    max_page_size = 200
    page_size_query_param = "page_size"


class ProjectMembershipPagination(pagination.PageNumberPagination):
    page_size = 30
    max_page_size = 200
    page_size_query_param = "page_size"