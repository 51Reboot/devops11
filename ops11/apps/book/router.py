from rest_framework import routers

from . import views

book_router = routers.DefaultRouter()

# /api/v20/book/publisher
# /api/v20/book/publisher/<pk>
# /api/v20/book/publisher/set_password
# /api/v20/book/publisher/<pk>/set_password
book_router.register(r'v20/book/publisher', views.PublisherModelViewSet)
book_router.register(r'v21/book/books', views.BookModelViewSet)
book_router.register(r'v22/book/books', views.BookBaseModelViewSet)

"""
练习
- 用 ModelViewSet 来实现 book 的查询功能
v20/book/books/
- put | delete 禁用掉
"""