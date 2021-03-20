## django生命周期框架图

### ![image](https://cdn.nlark.com/yuque/0/2021/png/370651/1615900572760-4a8597de-efd8-442d-8432-0245db7e9c37.png)



#### django请求生命周期流程步骤如下：

1：客户端发起HTTP请求，该请求一般会到达web服务器(nginx、apache)等，nginx转发给wsgi(web服务器网关接口）

2：wsgi将用户请求的数据解析后交给django应用

3：django中中间件会首先处理这部分请求（Security/csrf/session)，包括对请求数据得安全性校验和在此封装

```
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

4：请求在到达django项目下的 `urls.py` 总路由，总路由根据请求的url匹配子级路由，进入对应的app应用中

5：根据请求的url不通调用应用不同的视图函数，在视图函数中进行ORM操作处理数据或返回数据

6：返回的数据在通过路由系统达到对应的接口

7：响应的数据在通过中间件由下至上到达wsgi

8：wsgi将响应的数据封装成浏览器客户端识别的格式，再完成渲染。