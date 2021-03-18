# Django生命周期

![](_v_images/20210317153817337_1671648617.png =1000x)  

1. 客户端发起 `http` 请求，访问 `web` 服务器，如 `nginx`, `nginx` 转发给 `wsgi` 即网关；

2. `wsgi` 通过解析用户的数据分配给 `Django` 后端；

3. `Django`收到用户请求后，会先到中间件，中间件如下所示，请求会从上往下依次，当其中一个中间不允许此请求继续，则会返回相应的异常，当请求能够通过中间件，则继续下一步；
```
MIDDLEWARE = [
    # 为request/response提供了几种安全改进
    'django.middleware.security.SecurityMiddleware',

    # 开启session会话支持
    'django.contrib.sessions.middleware.SessionMiddleware',

    # 通用中间件，会处理一些URL，比如baidu.com会自动的处理成www.baidu.com。比如/blog/111会处理成/blog/111/自动加上反斜杠
    'django.middleware.common.CommonMiddleware',

    # 添加跨站点请求伪造的保护，通过向POST表单添加一个隐藏的表单字段，并检查请求中是否有正确的值
    'django.middleware.csrf.CsrfViewMiddleware',

    # 在视图函数执行前向每个接收到的user对象添加HttpRequest属性，表示当前登录的用户，无它用不了request.user
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # 开启基于Cookie和会话的消息支持，无它无message
    'django.contrib.messages.middleware.MessageMiddleware',

    # 对点击劫持的保护
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

4. 通过中间件后，通过用户请求的 `uri` 匹配路由系统(`urls.py`)的规则，转发到对应的 `app` 中；

5. 调用 `app` 中不同的视图类，在视图类中
    - 进行 `ORM` 操作处理数据并返回相应数据；
    - 取模版中的内容，取到后进行模版渲染;

6. 返回的数据在通过路由系统达到对应的接口

7. 响应的数据在通过中间件由下至上到达 `wsgi`

8. `wsgi` 将响应的数据封装成浏览器客户端识别的格式，完成渲染

## wsgi
- `Web Server Gateway Interface`，`WSGI` 不是服务器/`python` 模块/框架/`API` 或者任何软件，只是一种规范。

- 描述 `web server` 如何与 `web application` 通信的规范。`server` 和 `application` 的规范在 `PEP 3333` 中有具体描述。要实现 `WSGI` 协议，必须同时实现 `web server` 和 `web application` ，当前运行在 `WSGI` 协议之上的 `web` 框架有 `Torando,Flask,Django`

```
WSGI server负责从客户端接收请求，将request转发给application，将application返回的response返回给客户端；
WSGI application接收由server转发的request，处理请求，并将处理结果返回给server。application中可以包括多个栈式的中间件(middlewares)，这些中间件需要同时实现server与application，因此可以在WSGI服务器与WSGI应用之间起调节作用：对服务器来说，中间件扮演应用程序，对应用程序来说，中间件扮演服务器
```


## 中间件
- 中间件是一个用来处理 `Django` 的请求和响应的框架级别的钩子。它是一个轻量、低级别的插件系统，用于在全局范围内改变 `Django` 的输入和输出。每个中间件组件都负责做一些特定的功能

- 中间件类似于 `django` 的门卫，数据在进入和离开时都需要经过中间件 。

- 它能用来控制用户访问频率，做全局登陆校验，用户访问白名单，黑名单等……

```
中间件(Middleware)在整个Django的request/response处理机制中的角色如下

HttpRequest -> Middleware -> View -> Middleware -> HttpResponse
```