from django.urls import path
from . import views

urlpatterns = [
    path('cozinha/', views.cozinha, name='cozinha'),
]
