##  Django 生命周期

![img](https://upload-images.jianshu.io/upload_images/12367348-65a3d9b4623f7432.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)





![image-20210323111224485](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20210323111224485.png)



### 1、客户端发送请求
在浏览器输入url，譬如www.baidu.com，浏览器会自动补全协议（http），变为http://www.baidu.com，现在部分网站都实现了HSTS机制，服务器自动从http协议重定向到https协议

### 2、路由转发

IP查找：因特网内每个公有IP都是唯一的，域名相当于IP的别名，因为无法去记住一大堆无意义的IP地址，但如果用一堆有意义的字母组成，大家就能快速访问对应网站

DNS解析：通过域名去查找IP，先从本地缓存查找，其中本地的hosts文件也绑定了对应IP，若在本机中无法查到，那么就会去请求本地区域的域名服务器（通常是对应的网络运营商如电信），这个通过网络设置中的LDNS去查找，如果还是没有找到的话，那么就去根域名服务器查找，这里有所有因特网上可访问的域名和IP对应信息（根域名服务器全球共13台）

路由转发：通过网卡、路由器、交换机等设备，实现两个IP地址之间的通信。用到的主要就是路由转发技术，根据路由表去转发报文，还有子网掩码、IP广播等

### 3、建立连接

通过TCP协议的三次握手建立连接

### 4、传输报文
建立连接后，客户端会通过TCP依次、有序的发送一定大小的报文，其中包括了超时重传、阻塞窗口等等概念，用来保证数据包的完整、有序

http协议使用的明文传输，所有内容都是直接可读的

https协议是基于SSL/TLS加密，而SSL/TLS是基于TCP协议的，也就是http协议报文包装成TCP报文进行的加密，使用https协议的话，如果本地没有证书和公钥，那么会从服务器获取证书并且进行验证。

### 5、nginx处理

当前django框架开发的web项目，主流使用的服务器架构是：nginx+uWSGI+django。
nginx监听公网IP的某个端口，譬如80，接收到请求后，分2种情况处理请求：
如果是静态资源（如javascript、css、图片等）的请求，那么nginx直接获取到该资源，返回给用户。
如果是动态内容的请求，那么nginx就将请求转发到uWSGI，使用的协议一般都是uwsgi，性能最好。
有些reqeust会分多个数据包进行发送，nginx会缓存等待整个request接收完成才调用uWSGI
如果使用的https，那么加密、解密都在nginx中进行处理

### 6、uWSGI处理
uWSGI监听本机IP的某个端口，譬如3308，接收到nginx转发来的请求后，通过将http协议转换为WSGI协议，和**django程序之间进行通信**。

### 7、WSGIHandler处理

当django接受到一个请求时，会初始化一个WSGIHandler，可以在**项目下的wsgi.py**文件进行跟踪查看。

### 8、middleware的process_request
中间件的process_request方法列表对request对象进行处理

### 9、URLConf路由匹配
通过urls.py文件中的 urlpatterns 配置找到对应的 视图函数或者视图类的方法，如果没有找到匹配的方法，那么就会触发异常，==由中间件的process_exception 进行处理==

### 10、middleware的process_view
调用中间件的 process_view 方法进行预处理

### 11、views处理request
调用对应的视图函数或视图类的方法处理request，譬如获取GET和POST参数，并且调用特定的模型对象执行数据库操作，如果没有数据库操作，==那么就直接跳到后续的14步了==

### 12、models处理
视图方法中，一般情况下都需要调用模型类进行数据操作，一般是通过模型的manager管理类进行操作的，如：MyModel.objects.get(pk=1)
如果没有数据操作，==那么这一步和下一步就忽略==

### 13、数据库操作
如果django通过模型类执行对数据库的增删改查，那么此时整个流程就会在对应的数据库中执行

### 14、views处理数据

视图方法获取到数据后：
将数据封装到一个context字典当中，然后调用指定的template.html，通过模板中的变量、标签和过滤器等，再结合传入的数据context，会触发中间件的process_template_response方法，最终渲染成HttpResponse
==不调用模板，直接返回数据，譬如 JsonResponse、FileResponse等==
**执行redirect，生成一个重定向的HttpResponse，触发中间件的process_response后，返回到客户端，结束该web请求的生命周期**

### 15、middleware的process_response
调用中间件的 process_response 方法进行处理，最后一个中间件的process_response执行完成后，返回到WSGIHandler类中
至此，django编程的处理部分完毕

### 16、WSGIHandler处理
WSGIHandler类获取到response后

先处理response的响应行和响应头，然后调用 start_response 返回http协议的 响应行和响应头 到uWSGI，这个 start_response 只能调用一次

第一步处理完成后，如果是文件需要对response进行，否则就直接将response作为http协议的body部分返回给uWSGI

### 17、uWSGI处理
uWSGI接收到django程序的返回后，将所有内容包装成http协议的内容后，通过uwsgi协议返回给nginx服务器处理
### 18、nginx处理
nginx获取到uWSGI的返回后，将response通过TCP协议返回给客户端
### 19、客户端接收响应
客户端接收到服务器的响应后，做对应的操作，譬如：显示在浏览器中，或是javascript的处理等

==**至此，整个web请求的生命周期结束。**==





## 中间件

中间件是一个用来处理Django的请求和响应的框架级别的钩子。它是一个轻量、低级别的插件系统，用于在全局范围内改变Django的输入和输出。每个中间件组件负责做一些特定的功能。

### 中间件的五种方法

### 1 process_request

>  在视图函数之前，在路由匹配之前

### 2 process_response

>   执行时间：最后执行

### 3 process_view

>  执行时间：在process_request方法及路由匹配之后，视图之前

### 4 process_template_response

此方法必须在视图函数返回的对象有一个render()方法（或者表明该对象是一个TemplateResponse对象或等价方法）时，才被执行

> 执行时间：视图之后，process_exception之前

### 5 process_exception
此方法只在视图中触发异常时才被执行.

> 执行时间：视图之后，process_response之前





## 其他相关知识点

### TCP协议

> ==TCP== (Transmission Control Protocol，传输控制协议)是一种面向连接(连接导向)的、可靠的基于字节流的传输层通信协议。

TCP将用户数据打包成报文段，它发送后启动一个定时器，另一端收到的数据进行确认、对失序的数据重新排序、丢弃重复数据。

==三次握手==（建立连接的过程，只能客户端发起）：

* 客户端主动发送SYN包到服务器，并进入SYN_SEND状态，等待服务器确认
* 服务器收到SYN包并确认，发送SYN+ACK到客户端，服务器进入SYN_RECV状态
* 客户端收到SYN+ACK包，发送ACK确认连接，发送完毕后客户端和服务端进入ESTABLISHED状态，完成三次握手

==四次挥手==（断开连接的过程，可以是客户端发起，也可以是服务器端发起，下面以客户端演示）：

* 主机A主动发送FIN包，等待主机B确认
* 主机B收到FIN包并确认，发送ACK包到主机A
* 主机B发送FIN包到主机A，并等待主机A确认
* 主机A收到FIN包并确认，发送ACK包到主机B，并且丢弃连接，主机B收到ACK包后，丢弃连接



### web协议

> 是web服务器和web请求处理程序之间传输数据的一种标准协议   发展史为：CGI -> FCGI -> WSGI

* CGI：通用网关接口（Common Gateway Interface/CGI），最早的web协议

* FCGI：Fast CGI，在CGI基础上，提高了服务性能

* WSGI：Web Server Gateway Interface，专用于python程序，在CGI的基础上改进的协议

* uwsgi：uWSGI服务程序自有的协议（不是一个web协议），常用于在uWSGI服务器与其他网络服务器程序的数据通信，与WSGI没有关系。

  uWSGI是一个Web服务器程序，它实现了WSGI、uwsgi、http等协议。uWSGI起何作用，取决于架构方式

  - 如果架构是Nginx+uWSGI+Django， 那么uWSGI是一个中间件

  - 如果架构是uWSGI+Django，那么uWSGI是一个web服务器
    



### nginx服务器
> nginx是一个高性能的HTTP和反向代理服务器。

**正向代理**，例如平时使用的加速器、翻墙等代理就是正向代理，客户机请求代理服务器，代理服务器转发请求到对应的目标服务器

**反向代理**，部署在Web服务器上，代理所有外部网络对内部网络的访问。浏览器访问服务器，必须经过这个代理，是被动的。

<u>正向代理的主动方是客户端，反向代理的主动方是Web服务器</u>。

**反向代理的作用**：

*  安全
* 负载均衡
* 提升Web服务器的IO性能