from django.urls import path
from .views import PaymeCallBackAPIView

urlpatterns = [
    path("payme/update/", PaymeCallBackAPIView.as_view()),
]