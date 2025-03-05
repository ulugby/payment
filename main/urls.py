from django.urls import path
from .views import PaymeCallBackAPIView, ClickWebhookAPIView

urlpatterns = [
    path("payme/update/", PaymeCallBackAPIView.as_view()),
    path("clickuz/update/", ClickWebhookAPIView.as_view()),
]