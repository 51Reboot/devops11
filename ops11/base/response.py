from django.http.response import JsonResponse as JsonResponseX
from rest_framework.response import Response


def JSONAPIResponse(code, data=None, message=None, request_id=None):
    return Response({
        "code": code,
        "data": data,
        "message": message,
        "request_id": request_id,
        }
    )


# def JSONAPIResponse(code, data=None, message=None, request_id=None):
#     return JsonResponseX(data={
#         "code": code,
#         "data": data,
#         "message": message,
#         "request_id": request_id,
#     })