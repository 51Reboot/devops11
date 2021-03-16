### wsgi 简述

**wsgi**：web服务器网关接口，指定了web服务器和Python web应用或web框架之间的标准接口，以提高web应用在一系列web服务器间的移植性。

- WSGI是一套接口标准协议/规范；

- 通信（作用）区间是Web服务器和Python Web应用程序之间；

- 目的是制定标准，以保证不同Web服务器可以和不同的Python程序之间相互通信

  

### 源码分析

HTTP请求先到达**WSGIHandler**，WSGIRequest该类封装了请求的信息（environ/path_info/META/path/methodcontent_length）等，

#### WSGIHandler()

```python
class WSGIHandler(base.BaseHandler):
    request_class = WSGIRequest

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_middleware()

    def __call__(self, environ, start_response):
        set_script_prefix(get_script_name(environ))
        signals.request_started.send(sender=self.__class__, environ=environ)
        request = self.request_class(environ)
        response = self.get_response(request)

        response._handler_class = self.__class__

        status = '%d %s' % (response.status_code, response.reason_phrase)
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        start_response(status, response_headers)
        if getattr(response, 'file_to_stream', None) is not None and environ.get('wsgi.file_wrapper'):
            response.file_to_stream.close = response.close
            response = environ['wsgi.file_wrapper'](response.file_to_stream, response.block_size)
        return response
```



#### BaseHandler