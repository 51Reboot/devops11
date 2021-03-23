

### wsgi 简述

> 是web服务器和web请求处理程序之间传输数据的一种标准协议   发展史为：CGI -> FCGI -> WSGI

* CGI：通用网关接口（Common Gateway Interface/CGI），最早的web协议

* FCGI：Fast CGI，在CGI基础上，提高了服务性能

* WSGI：Web Server Gateway Interface，**专用于python程序**，在CGI的基础上改进的协议

* uwsgi：uWSGI服务程序自有的协议（不是一个web协议），常用于在uWSGI服务器与其他网络服务器程序的数据通信，与WSGI没有关系。

  uWSGI是一个Web服务器程序，它实现了WSGI、uwsgi、http等协议。uWSGI起何作用，取决于架构方式

  - 如果架构是Nginx+uWSGI+Django， 那么uWSGI是一个中间件

  - 如果架构是uWSGI+Django，那么uWSGI是一个web服务器



### 源码分析

一般在项目目录同名目录下有个wsgi.py文件，应用启动后，主要由此来接收HTTP请求数据得解析和响应数据的封装。

```python
ops11
  -- apps
  -- ops11
    -- __init__.py
    -- asgi.py
    -- setting.py
    -- urls.py
  -- static
```

#### wsgi.py

该文件主要作为入口文件，加载django setting中配置信息，返回 `WSGIHandler()` 处理函数

> ops11/ops11/wsgi.py

```python

import os
from django.core.wsgi import get_wsgi_application
# 设置环境变量，加载setting.py中变量配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops11.settings')
application = get_wsgi_application()  
```

> django/core/wsgi.py

实际调用入口

```python
import django
from django.core.handlers.wsgi import WSGIHandler


def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Return a WSGI callable.
    Avoids making django.core.handlers.WSGIHandler a public API, in case the
    internal WSGI implementation changes or moves in the future.
    """
    #Django WSGI支持的公共接口。返回一个可调用的WSGI。避免将django.core.handlers.WSGIHandler设为公共API
    django.setup(set_prefix=False)
    return WSGIHandler()
```



==WSGIHandler 和 BaseHandler 体现了一个完成的请求和响应经过的函数和方法 除了实际业务逻辑外的过程==

#### WSGIHandler

WSGIHandler主要用来处理django的请求与响应逻辑，由于类内部实现了__call__方法 直接调用返回

WSGIRequest：Django在接收到http请求之后，会根据http请求携带的参数以及报文信息创建一个WSGIRequest对象，返回stream格式数据等待处理

> django/core/handles/wsgi.py

```python
class WSGIHandler(base.BaseHandler):
    request_class = WSGIRequest
    # 将HttpRequest请求封装成WSGIRequest对象，包含请求PATH_INFO/REQUEST_METHOD/SCRIPT_NAME等信息

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.load_middleware()
        # 当调用wsgihandler时，继承父类方法，加载后台异步处理的中间件

    def __call__(self, environ, start_response):
        set_script_prefix(get_script_name(environ))
        # 在处理请求之前先发送request_started信号，信号接收为类本身，参数为请求变量
        signals.request_started.send(sender=self.__class__, environ=environ)
        # request_class = WSGIRequest， 初始化request请求对象即WSGIRequest，该请求包含请求中变量信息
        request = self.request_class(environ)        
        response = self.get_response(request)
        response._handler_class = self.__class__
        status = '%d %s' % (response.status_code, response.reason_phrase)
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        # 获取请求响应后，将状态status和响应头reponse_headers作为参数传入start_response,
        # server提供的回调方法，将响应的header和status返回给server
        start_response(status, response_headers)
        if getattr(response, 'file_to_stream', None) is not None and environ.get('wsgi.file_wrapper'):
            # If `wsgi.file_wrapper` is used the WSGI server does not call
            # .close on the response, but on the file wrapper. Patch it to use
            # response.close instead which takes care of closing all files.
            response.file_to_stream.close = response.close
            # 如果有response有file_to_stream属性或变量里有file_wrapper属性，关闭响应文件流
            response = environ['wsgi.file_wrapper'](response.file_to_stream, response.block_size)
        return response
```

#### BaseHandler

l主要用来处理django请求和响应与django中间件调用逻辑

> django/core/handles/base.py 

```python
    def load_middleware(self, is_async=False):
        """
        Populate middleware lists from settings.MIDDLEWARE.

        Must be called after the environment is fixed (see __call__ in subclasses).
        """
        # # 中间件的process_view()方法都添加到这
        self._view_middleware = []
        # # 中间件的process_template_response()方法都添加到这
        self._template_response_middleware = []
        # 中间件的process_exception()方法都添加到这
        self._exception_middleware = []
        
        get_response = self._get_response_async if is_async else self._get_response
        # 遍历所有中间件之前，handler赋值给调用实体的_get_response成员函数，而_get_response()中包含了view函数的调用。
        handler = convert_exception_to_response(get_response)
        handler_is_async = is_async
        # 从配置文件中获得MIDDLEWARE变量中的所有中间件,开始遍历中间件
        for middleware_path in reversed(settings.MIDDLEWARE):
            # 根据middleware字符串导入middleware(中间件的类
            middleware = import_string(middleware_path)
            middleware_can_sync = getattr(middleware, 'sync_capable', True)
            middleware_can_async = getattr(middleware, 'async_capable', False)
            if not middleware_can_sync and not middleware_can_async:
                raise RuntimeError(
                    'Middleware %s must have at least one of '
                    'sync_capable/async_capable set to True.' % middleware_path
                )
            elif not handler_is_async and middleware_can_sync:
                middleware_is_async = False
            else:
                middleware_is_async = middleware_can_async
            try:
                # Adapt handler, if needed.
                handler = self.adapt_method_mode(
                    middleware_is_async, handler, handler_is_async,
                    debug=settings.DEBUG, name='middleware %s' % middleware_path,
                )
                # # 创建中间件类的实例
                mw_instance = middleware(handler)
            except MiddlewareNotUsed as exc:
                if settings.DEBUG:
                    if str(exc):
                        logger.debug('MiddlewareNotUsed(%r): %s', middleware_path, exc)
                    else:
                        logger.debug('MiddlewareNotUsed: %r', middleware_path)
                continue

            if mw_instance is None:
                raise ImproperlyConfigured(
                    'Middleware factory %s returned None.' % middleware_path
                )
            # 如果 执行中间件类后返回有包含process_view、process_template_response、process_exception属性，将其放在各自对应的列表中
            if hasattr(mw_instance, 'process_view'):
                self._view_middleware.insert(
                    0,
                    self.adapt_method_mode(is_async, mw_instance.process_view),
                )
            if hasattr(mw_instance, 'process_template_response'):
                self._template_response_middleware.append(
                    self.adapt_method_mode(is_async, mw_instance.process_template_response),
                )
            if hasattr(mw_instance, 'process_exception'):
                # The exception-handling stack is still always synchronous for
                # now, so adapt that way.
                self._exception_middleware.append(
                    self.adapt_method_mode(False, mw_instance.process_exception),
                )

            handler = convert_exception_to_response(mw_instance)
            handler_is_async = middleware_is_async

        # Adapt the top of the stack, if needed.
        handler = self.adapt_method_mode(is_async, handler, handler_is_async)
        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._middleware_chain = handler
```

##### get_response 处理请求

> django/handler/base.py/BaseHandler

```python

def get_response(self, request):
    """Return an HttpResponse object for the given HttpRequest."""
    # Setup default url resolver for this thread
    # ROOT_URLCONF = 'ops11.urls' ,将路由的总路径作为参数传递，为当前线程设置URLconf
    set_urlconf(settings.ROOT_URLCONF)
    # 将 request = self.request_class(environ)请求压入中间件处理，会依次调用中间件中处理方法，即上述load_middware方法，并返回response
    response = self._middleware_chain(request)
    response._closable_objects.append(request)
    # 如果响应的状态码大雨400，则记录错误日志
    if response.status_code >= 400:
        log_response(
            '%s: %s', response.reason_phrase, request.path,
            response=response,
            request=request,
        )
    return response
```



