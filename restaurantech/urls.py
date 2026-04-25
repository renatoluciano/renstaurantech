from django.urls import path
from . import views

urlpatterns = [
    path('cozinha/', views.cozinha, name='cozinha'),
    path('mesa/', views.mesa, name='mesa'),
    path('fazer-pedido/', views.fazer_pedido, name='fazer_pedido'),
    path('garcom/', views.garcom, name='garcom'),
    path('notificar-pronto/', views.notificar_pronto, name='notificar_pronto'),
    path('pedir-conta/', views.pedir_conta, name='pedir_conta'),
    path('liberar-mesa/', views.liberar_mesa, name='liberar_mesa'),
]
