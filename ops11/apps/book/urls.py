from django.urls import path
from . import views

urlpatterns = [
    path('v1/book/publisher', views.PrintHello),
    path('v2/book/publisher', views.PublisherView.as_view()),
    path('v3/book/publisher', views.PublisherApiView.as_view()),
    path('v3/book/publisher/<int:pk>', views.PublisherApiView.as_view()),

    # generic api view
    path('v10/book/publisher', views.PublisherListAPIView.as_view()),
    path('v11/book/publisher', views.PublisherCreateAPIView.as_view()),
    path('v12/book/publisher', views.PublisherListCreateAPIView.as_view()),
    path('v12/book/publisher/<int:pk>', views.PublisherListCreateAPIView.as_view()),
]