[toc]


### 一、Django中间件

中间件是Django用来处理请求和响应的钩子框架，用于全局性地控制Django输入和输出。


- Django中间件作用

    - 修改请求，即传送到`view`中的`HttpRequest`对象。
    - 修改响应，即`view`返回的`HttpResponse`对象。



- Django默认中间件配置

Django配置文件`setting.py`的`MIDDLEWARE`配置项列表中定义了如何启用中间件组件：

```bash
MIDDLEWARE = [
    # 安全中间件：提供网站安全保护功能
    'django.middleware.security.SecurityMiddleware',
    
    # 会话中间件：会话保持功能（HTTP是无状态的），操作cookie
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # 通用中间件：提供禁止某些UA访问，URL自动补充，设置Content-Length等功能
    'django.middleware.common.CommonMiddleware',
    
    # CSRF防御中间件：提供CSRF防御机制的中间件（跨域）
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # 认证框架: 提供认证服务，将用户请求与request关联起来，保存经过验证的用户身份信息
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # 消息中间件：基于cookie或者会话的消息功能
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # X框架操作中间件：头部信息中增加 X-Frame-OptionsLAI 防止简单的点击劫持
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```


- 中间件请求顺序

    - 请求阶段：**自顶而下**
    - 响应阶段：**自下而上**

![](https://note.youdao.com/yws/public/resource/43fcc9bafc33508fa1f7b8eaedb7d8c0/xmlnote/9AAE8D2BB93444B497A35776AB665EB6/72173)

> **注意：** `MIDDLEWARE` 的顺序很重要，具有先后关系，因为有些中间件会依赖其他中间件。



- 自定义中间件
```
from django.utils.deprecation import MiddlewareMixin

class MD1(MiddlewareMixin): 
    pass
```
| 请求方法 | 返回值 | 执行时机 |
| -------- | ------ | -------- |
| `process_request(self,request)` | `None` <br> `HttpResponse`  | 接收到请求，执行视图之前 |
| `process_view(self, request, view_func, view_args, view_kwargs)` | `None` <br> `HttpResponse` <br> `view_func(request) ` | `process_request`之后，路由转发视图，执行视图之前 |
| `process_exception(self, request, exception)` | `None(500)` <br> `HttpResponse(200)` | 视图执行中发生异常 |
| `process_response(self, request, response)` | `HttpResponse(必须)` | 视图执行完毕，返回响应 |


最后附一张Django生命周期执行流程，加深理解：

![](https://note.youdao.com/yws/public/resource/43fcc9bafc33508fa1f7b8eaedb7d8c0/xmlnote/3B3323BBBEDD49F4A3DDFC52B95DB494/72319)




### 二、WSGI协议实现

WSGI(Web Server Gateway Interface) 是一种描述web server如何web application通信的规范。

- WSGI协议主要包括`server`和`application`两部分

    - `WSGI server`：接收客户端请求，将`request`转发给`applicaton`；将`application`的`response`返回给客户端。
    - `WSGI application`：接收`server`转发的`request`，处理并返回结果给`server`;

> 中间件在`server`与`application`之间起到调节作用（`server <-> middleware <-> application`）


- wsgi server请求处理流程

![](https://note.youdao.com/yws/public/resource/43fcc9bafc33508fa1f7b8eaedb7d8c0/xmlnote/35AB76A20D75474FB1C1F89DFEA62D44/72400)

- `BaseHandler`
```python
class WSGIHandler(base.BaseHandler):
    request_class = WSGIRequest
    
    # 加载中间件 BaseHandler.load_middleware 逆序加载
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_middleware()
    
    # 回调方法，将响应的header与status返回给server
    def __call__(self, environ, start_response):
        ...
        response = self.get_response(request)
        
        ...
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        start_response(status, response_headers)
        
        ...
        return response
```

- `BaseHandler`
```
class BaseHandler:
    ...
    
    # 加载setting.MIDDLEWARE配置的中间件
    def load_middleware(self, is_async=False):
        ...
        
        # reversed(settings.MIDDLEWARE) 自下而上逆序通过中间件处理响应
        for middleware_path in reversed(settings.MIDDLEWARE):
            middleware = import_string(middleware_path)
            middleware_can_sync = getattr(middleware, 'sync_capable', True)
            middleware_can_async = getattr(middleware, 'async_capable', False)
            ...
    
   # 通过get_response方法加载Django项目的ROOT_URLCONF，然后根据url规则找到对应的view方法(类)，view逻辑会根据request实例生成并返回具体的respo
    def get_response(self, request):
        """Return an HttpResponse object for the given HttpRequest."""
        # Setup default url resolver for this thread
        set_urlconf(settings.ROOT_URLCONF)
        response = self._middleware_chain(request)
        response._resource_closers.append(request.close)
        if response.status_code >= 400:
            log_response(
                '%s: %s', response.reason_phrase, request.path,
                response=response,
                request=request,
            )
        return response

request_finished.connect(reset_urlconf)
```
