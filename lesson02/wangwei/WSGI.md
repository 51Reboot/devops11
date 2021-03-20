### wsgi 简述

**WSGI，**全称Python Web Server Gateway Interface，是在PEP333中(PEP3333进行了补充)定义的一种协议，目的是将http底层和框架层解耦，WSGI协议分为两部分，分别为WSGI Server和WSGI Application，WSGI Server负责接受客户端请求、解析请求、并按照协议规范将请求转发给WSGI Application，同时负责接受WSGI Application的响应并发送给客户端；WSGI Application负责接受由WSGI Server发送过来的请求，实现业务处理逻辑，并将标准的响应发回给WSGI Server：

![image](https://cdn.nlark.com/yuque/0/2021/png/370651/1616213464369-b0359934-76cb-4ca1-aa60-d264b50543bb.png)

具体来说，WSGI Server解析客户端由socket发送过来的http数据包，将请求的http version、method、host、path等包装成environ参数，并提供start_response回调函数，并将environ和

start_response函数作为参数传递给由WSGI Application提供的callable对象，获取callable对象的返回结果，处理后依照http协议传递给客户端，完成一次请求。



### 区分wsgi / uwsgi / asgi

 首先需要介绍的是CGI， CGI全称(Common Gateway Interface, 通用网关接口),定义的是客户端与Web服务器交流方式的一个程序.例如正常情况下客户端发送来一个请求,CGI根据HTTP协议的将请求内容进行解析, 经过计算以后会将计算出来的内容封装好,比如服务器返回一个html页面,并且根据http协议构建返回的内容格式,涉及到的tcp连接、http原始请求和相应的格式这些， 都是由一个软件来完成，完成以上的工作需要一个程序来完成， 便是CGI。

- **WSGI, 全称Web服务器网关接口(**Python Web Server Gateway Interface, WSGI),是为Python语言定义的Web服务器和Web应用程序或框架之间的一种简单而通用的接口..简单来说就是用来处理Web服务端与客户端的通信问题的.
- **UWSG**I是一个Web服务器, 实现了WSGI协议,uwsgi,http等协议，uwsgi是一个二进制协议, 能够携带任何类型的信息,uwsgi数据包的前4个字节用于面描述信息的类型,该协议主要工作在tcp方式下,**uwsgi是一种线路协议而不是通信协议,**因此常用于在uWSGI服务器与其他网络服务器的数据通信.
- **ASGI** 是异步网关协议接口,介于网络服务和python饮用应用之间的标准接口,能够处理多种通用的协议类型,包括http,http2和websocket.

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

```python
## ops11/ops11/wsgi.py
import os
from django.core.wsgi import get_wsgi_application
# 设置环境变量，加载setting.py中变量配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops11.settings')
application = get_wsgi_application()  

## django\core\wsgi.py
def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Return a WSGI callable.

    Avoids making django.core.handlers.WSGIHandler a public API, in case the
    internal WSGI implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    return WSGIHandler()
```

#### WSGIHandler

**WSGIHandler主要用来处理django的请求与响应逻辑，由于类内部实现了__call__方法，说明**WSGIHandler实际上是个回调函数，可直接通过类名调用。

**WSGIRequest：**Django在接收到http请求之后，会根据http请求携带的参数以及报文信息创建一个WSGIRequest对象，`WSGIRequest`对象上大部分的属性都是只读的。

```python
class WSGIHandler(base.BaseHandler):
    # 将请求封装成WSGIRequest对象，包含请求URL/path/meta/method等信息
    request_class = WSGIRequest

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 当调用wsgihandler时，继承父类方法，加载中间件
        self.load_middleware()

    def __call__(self, environ, start_response):
        # 好像是过去请求脚本的url前缀
        set_script_prefix(get_script_name(environ))
        # 在处理请求之前先发送request_started信号，信号接收为类本身，参数为请求变量
        signals.request_started.send(sender=self.__class__, environ=environ)
        # request_class = WSGIRequest， 初始化request请求对象即WSGIRequest，该请求包含请求中变量信息
        request = self.request_class(environ)
        # 
        response = self.get_response(request)

        response._handler_class = self.__class__

        status = '%d %s' % (response.status_code, response.reason_phrase)
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        # 获取请求响应后，将状态status和响应头reponse_headers作为参数传入start_respnse,
        # server提供的回调方法，将响应的header和status返回给server
        start_response(status, response_headers)
        # 如果有response有file_to_stream属性或变量里有file_wrapper属性，关闭响应文件流
        if getattr(response, 'file_to_stream', None) is not None and environ.get('wsgi.file_wrapper'):
            # If `wsgi.file_wrapper` is used the WSGI server does not call
            # .close on the response, but on the file wrapper. Patch it to use
            # response.close instead which takes care of closing all files.
            response.file_to_stream.close = response.close
            response = environ['wsgi.file_wrapper'](response.file_to_stream, response.block_size)
        # 返回请求实体
        return response
```

#### BaseHandler

##### load_middleware 加载中间件

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

WSGIHandler处理请求调用的函数

```python
# handler/base.py/BaseHandler
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