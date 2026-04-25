from django.urls import path
from . import views

urlpatterns = [
    path('cozinha/', views.cozinha, name='cozinha'),
    path('mesa/', views.mesa, name='mesa'),
    path('fazer-pedido/', views.fazer_pedido, name='fazer_pedido'),
    path('garcom/', views.garcom, name='garcom'),
]
