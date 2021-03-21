from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    :param exc: 异常
    :param context: 上下文
    :return: Response object
    """
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data.pop('detail')
        response.data['code'] = -1
        response.data['data'] = None
        response.data['message'] = detail
        response.data['request_id'] = ""

    return response