from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination


class CustomPageNumberPagination(PageNumberPagination):
    # 设置
    page_size_query_param = "page_size"

    # 一页显示多少条数据
    # 默认值
    page_size = 5

    # 最大值
    max_page_size = 10


class CustomLimitOffsetPagination(LimitOffsetPagination):
    # 默认显示多少条数据
    default_limit = 5

