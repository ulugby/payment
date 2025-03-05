from django.urls import path
from .views import OrderCreate, homepage

urlpatterns = [
    path('order-create/', OrderCreate.as_view()),
    path('', homepage, name='homepage'),
]