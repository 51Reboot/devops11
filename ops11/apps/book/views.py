from django.views import View
from django.http.response import HttpResponse

from .models import Publisher


from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

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

    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            raise NotFound()

    def get(self, request, format=None, *args, **kwargs):
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
