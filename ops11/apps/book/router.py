from rest_framework import routers

from . import views

book_router = routers.DefaultRouter()

# /api/v20/book/publisher
# /api/v20/book/publisher/<pk>
# /api/v20/book/publisher/set_password
# /api/v20/book/publisher/<pk>/set_password
book_router.register(r'v20/book/publisher', views.PublisherModelViewSet)
