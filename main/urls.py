from django.urls import path
from .views import PaymeCallBackAPIView, ClickCallBackAPIView

urlpatterns = [
    path("payme/update/", PaymeCallBackAPIView.as_view()),
    path("clickuz/update/", ClickCallBackAPIView.as_view()),
]