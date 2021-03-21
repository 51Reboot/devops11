from rest_framework.viewsets import ModelViewSet

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters

from base.response import JSONAPIResponse
from base.pagination import CustomPageNumberPagination

from rest_framework.views import exception_handler


class BaseModelViewSet(ModelViewSet):
    # 过滤器
    # parser_classes = []
    pagination_class = CustomPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    search_fields = []
    filterset_fields = []
    filterset_class = None
    throttle_classes = []

    def list(self, request, *args, **kwargs):
        response = super(BaseModelViewSet, self).list(request, *args, **kwargs)
        return JSONAPIResponse(code=0, data=response.data, message=None)

    def retrieve(self, request, *args, **kwargs):
        response = super(BaseModelViewSet, self).retrieve(request, *args, **kwargs)
        return JSONAPIResponse(code=0, data=response.data, message=None)
