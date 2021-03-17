## 一.关于WSGI
![image](https://note.youdao.com/yws/public/resource/9cd6ee440f29c478ea913e6a7aad9a34/xmlnote/WEBRESOURCE96bc49db25f85351d9031e1a03877aba/56875)

### 1.WSGI
WSGI(Web Server Gateway Interface)描述了WSGI server如何与WSGI App进行通信的规范。
### 2.WSGI的实现
server先收到用户的http请求，然后调用application提供的可调用对象，调用的结果会被封装成HTTP响应后发送给客户端。
### 3.对WSGI App的3个要求
1)实现一个可调用对象 ：
- Python中应该是函数、类、实现了__call__ 方法的类实例；
- 这个可调用对象应该接收两个参数(environ,start_response)
- 返回一个可迭代对象，比如:列表，yieled等；

==django、Flask==相当于就是这个可调用对象，本质就是实现了如上3个要求。

可调用对象的3种实现方式：

```python
res_str = b'baidu.com\n'

# 函数实现
def application1(environ, start_response):
    return [res_str]

# 类实现
class Application2:
    def __init__(self, environ, start_response):
        pass

    def __iter__(self):  # 实现此方法，对象即可迭代
        yield res_str

# 类实现 
class Application3:
    def __call__(self, environ, start_response):
        return [res_str]
```
2)关于environ:  
environ是一个包含http请求信息的dict对象  
![image](https://note.youdao.com/yws/public/resource/9cd6ee440f29c478ea913e6a7aad9a34/xmlnote/AB22F12A3300493F87AA57DA9494D574/57173)  
3)关于start_response：  
- start_response接受两个必须的参数，status(HTTP状态)和response_headers(响应消息的头)；
- response_headers 是一个  元素为二元组的列表，例如[('Content-Type', 'text/plain;charset=utf-8')]
- start_response应该在返回可迭代对象之前调用，因为它返回的是Response Header。返回的可迭代对象是 Response Body。  
### 4.对WSGI Server的要求
- 监听HTTP服务端口（TCPServer，默认端口80）
- 接收浏览器端的HTTP请求并解析封装成environ环境数据
- 负责调用应用程序，将environ和start_response方法传入
- 将应用程序响应的正文封装成HTTP响应报文返回浏览器端

### 5.自定义实现WSGI App 和WSGI Server

```python
# SWGI App
def application(environ, start_response):
    status = '200 OK'
    # headers是一个 2元祖的列表；
    headers = [('Content-Type', 'text/html;charset=utf-8')]
    start_response(status, headers)  # 返回可迭代对象
    html = '<h1>test wsgi App</h1>'.encode("utf-8")
    return [html]

# WSGI Server
from wsgiref.simple_server import make_server
ip = '127.0.0.1'
port = 9999
server = make_server(ip, port, application)
server.serve_forever()
```
## 二、django中如何实现WSGI App
### 1.wsgi.py文件源码解析：
django项目第一次运行的时候，application这个对象会做一次初始化操作，看下边的代码分析；  
当有请求进来的时候，才会执行application(environ, start_response), 即调用WSGIHandler()的__call__方法；
```python
# ./ops11/ops11/wsgi.py
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops11.settings')

# application变成了函数的返回结果；
# 根据后边代码的分析等价于 application =  WSGIHandler()
# 项目第一次运行之后，会先执行WSGIHandler()的__init__初始化。
application = get_wsgi_application()
```
### 2.get_wsgi_application()   
```python
# .venv/lib/python3.9/site-packages/django/core/wsgi.py
import django
from django.core.handlers.wsgi import WSGIHandler


def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Return a WSGI callable.

    Avoids making django.core.handlers.WSGIHandler a public API, in case the
    internal WSGI implementation changes or moves in the future.
    """
    # django.setup()函数，主要有set_prefix设置url的前缀、设置django默认配置、\
    # populate方法:导入INSTALLED_APPS中的模块、配置(反射思想)，以及model,最终将app设置为ready状态.
    django.setup(set_prefix=False)
    # 返回一个实例化的对象WSGIHandler()；
    return WSGIHandler()
```
### 3.WSGIHandler()
```python
# .venv/lib/python3.9/site-packages/django/core/handlers/wsgi.py
class WSGIHandler(base.BaseHandler):
    request_class = WSGIRequest
    
    # django项目第一次运行的时候，会执行初始化操作，实例化对象application；
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # load_moddleware方法 见下边代码分析，主要是为了载入setting中的middleware
        self.load_middleware()
        
    # 有请求进来的时候，才会执行application(environ,start_response),调用__call__方法
    def __call__(self, environ, start_response):
                
        # 跟url前缀有关， 对此不是很了解，先埋坑*******
        # WSGI协议中 path = SCRIPT_NAME + PATH_INFO
        # get_script_name代码中看到是获取environ中请求的SCRIPT_NAME；
        # set_script_name作用是给 前缀prefix后边加/；
        set_script_prefix(get_script_name(environ))
        
        # 触发信号，开始处理请求，未深入看******
        # 跟踪之后代码框中源码分析signals.request_started.send
        signals.request_started.send(sender=self.__class__, environ=environ)
        
        # request相当于是实例化WSGIRequest()的对象，因此通过request.xxx就能看到很多自己的很多属性；
        # 关于django中request有很多属性及方法就是这里获取到的，具体看WSGIRequest()这个类，比较简单，不深入了.
        request = self.request_class(environ)
        
        #查看下文中get_response(request)的代码注释分析
        response = self.get_response(request)
        response._handler_class = self.__class__
        # status 状态设置
        status = '%d %s' % (response.status_code, response.reason_phrase)
        # 符合start_response函数对response_headers参数的数据格式要求，一个二元组列表
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        # 先执行start_response(),设定好response的头信息；
        start_response(status, response_headers)
        if getattr(response, 'file_to_stream', None) is not None and environ.get('wsgi.file_wrapper'):
            response = environ['wsgi.file_wrapper'](response.file_to_stream)
        # 返回response的body部分    
        return response
```
### 4.load_middleware()  
主要是通过反射的形式将settings.py中的middle的配置载入到项目中，对于is_async相关的参数没看懂****  
看到代码中是一个response的一个过程，对配置中的middle列表做了倒叙，然后import到项目中，还是不太清晰**** 
```python
# .venv/lib/python3.9/site-packages/django/core/handlers/base.py
class BaseHandler:
    ...
    def load_middleware(self, is_async=False):
        self._view_middleware = []
        self._template_response_middleware = []
        self._exception_middleware = []
        get_response = self._get_response_async if is_async else self._get_response
        handler = convert_exception_to_response(get_response)
        handler_is_async = is_async
        for middleware_path in reversed(settings.MIDDLEWARE):
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
        ...
```
### 5.get_response(request) ：  
```
# .venv/lib/python3.9/site-packages/django/core/handlers/base.py
class BaseHandler:
    ...
    def get_response(self, request):
    """Return an HttpResponse object for the given HttpRequest."""
    #set_urlconf 过程没看懂，到了Local()实例化的时候******
    set_urlconf(settings.ROOT_URLCONF)
    # 已经实在看不进去了**************************
    response = self._middleware_chain(request)
    response._resource_closers.append(request.close)
    if response.status_code >= 400:
        log_response(
            '%s: %s', response.reason_phrase, request.path,
            response=response,
            request=request,
        )
    return response
    ...
```
