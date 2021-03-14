from django.views import View
from django.http.response import HttpResponse

from .models import Publisher
from .serializers import PublisherModelSerializer


from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.viewsets import ModelViewSet


from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, AdminRenderer
from rest_framework_yaml.renderers import YAMLRenderer
from rest_framework_csv.renderers import CSVRenderer

from base.response import JSONAPIResponse
# Create your views here.


# Django FBV function base view
def PrintHello(request, *args, **kwargs):
    print("path_info", request.path_info)
    print("META", request.META)
    print("method", request.method)
    return HttpResponse("hello world.")


# Django CBV class base view
class PublisherView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse("View get")

    def post(self, request, *args, **kwargs):
        return HttpResponse("View post")

    def put(self, request, *args, **kwargs):
        return HttpResponse("View put")

    def delete(self, request, *args, **kwargs):
        return HttpResponse("View delete")


# DRF CBV
# APIView
class PublisherApiView(APIView):
    # parser_classes = [JSONParser, FormParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, AdminRenderer, YAMLRenderer, CSVRenderer]

    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            raise NotFound()

    def get(self, request, format=None, *args, **kwargs):
        print("django get param", request.GET)
        print("drf get param", request.query_params)
        # /api/v1/book/publisher
        if kwargs.get("pk"):
            # 查看单条数据
            p = self.get_object(kwargs['pk'])
            data = p.serializer()
        else:
            # 查询全部数据
            ps = Publisher.objects.all() # queryset []
            data = [p.serializer() for p in ps]
        return JSONAPIResponse(code=0, data=data, message=None)

    def post(self, request):
        data = request.data
        # content-type: application/json
        # print(f"drf data--> {data}", request.content_type)
        #
        # print("django data->", request.POST, request.content_type)
        # return JSONAPIResponse(code=-2, data=None, message=None)

        p = Publisher.objects.create(**data)
        return JSONAPIResponse(code=0, data=p.serializer(), message=None)

    def put(self, request, *args, **kwargs):
        data = request.data

        count = Publisher.objects.filter(pk=kwargs['pk']).update(**data)
        # 受影响的行数
        if count == 0:
            return JSONAPIResponse(code=-1, data=None, message="Update fail, please check.")
        else:
            return JSONAPIResponse(code=0, data=None, message=f"{count} record is updated.")

    def delete(self, request, *args, **kwargs):
        p = self.get_object(kwargs['pk'])
        p.delete()
        return JSONAPIResponse(code=0, data=None, message="Delete ok.")


class PublisherListAPIView(ListAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherModelSerializer


class PublisherCreateAPIView(CreateAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherModelSerializer


class PublisherListCreateAPIView(ListCreateAPIView): # update or delete
    queryset = Publisher.objects.all()
    serializer_class = PublisherModelSerializer


class PublisherModelViewSet(ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherModelSerializer

    @action(methods=['get'], detail=False, url_path="set_url")
    def print_url(self, request):
        """
        update password
        """
        print("update password")
        return JSONAPIResponse(code=0, data=None, message=None)


