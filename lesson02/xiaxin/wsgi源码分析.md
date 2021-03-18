# wsgi源码分析

## wsgi.py
```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops11.settings')

application = get_wsgi_application()
```

```python
def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Return a WSGI callable.

    Avoids making django.core.handlers.WSGIHandler a public API, in case the
    internal WSGI implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    return WSGIHandler()
```

- django项目运行的时候，会加载项目目录下面的settings模块文件，然后application对象会做一次初始化操作, 调用WSGIHandler对象；


## WSGIHandler Class

```python
# 继承BaseHandler类
class WSGIHandler(base.BaseHandler):
    # 类属性，给request_class赋值WSGIRequest的属性方法等；
    request_class = WSGIRequest

    # 实例初始化
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 加载settings模块中的中间件
        self.load_middleware()
    
    # 当请求进来的时候，才会执行application(environ,start_response),回调__call__方法
    def __call__(self, environ, start_response):
        # 在url后面加/
        set_script_prefix(get_script_name(environ))
        
        # 当执行某一次请求之前，发送信号
        signals.request_started.send(sender=self.__class__, environ=environ)

        # 实例化WSGIRequest类
        request = self.request_class(environ)

        # 为request相应的返回结果，如url模块中的定义的名称
        # 是否同步返回数据还是异步返回数据
        response = self.get_response(request)

        response._handler_class = self.__class__
        
        # 设置返回结果的状态码
        status = '%d %s' % (response.status_code, response.reason_phrase)
        # 响应结果的头部信息，如cookie等
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        
        # 返回状态码头部信息等数据
        start_response(status, response_headers)

        # 如果response该方法没有file_to_stream属性或者environ对象能获取wsgi.file_wrapper属性，那么就关闭此类连接等
        if getattr(response, 'file_to_stream', None) is not None and environ.get('wsgi.file_wrapper'):
            # If `wsgi.file_wrapper` is used the WSGI server does not call
            # .close on the response, but on the file wrapper. Patch it to use
            # response.close instead which takes care of closing all files.
            response.file_to_stream.close = response.close
            response = environ['wsgi.file_wrapper'](response.file_to_stream, response.block_size)
        return response

```