from django.urls import path
from . import views

urlpatterns = [
    # Telas principais
    path('cozinha/', views.cozinha, name='cozinha'),
    path('garcom/', views.garcom, name='garcom'),
    
    # Mesa dinâmica (Exige o número da mesa na URL)
    path('mesa/<int:numero_mesa>/', views.mesa, name='mesa'),
    path('fazer-pedido/<int:numero_mesa>/', views.fazer_pedido, name='fazer_pedido'),
    path('pedir-conta/<int:numero_mesa>/', views.pedir_conta, name='pedir_conta'),
    
    # Ações do Garçom e Cozinha
    path('notificar-pronto/', views.notificar_pronto, name='notificar_pronto'),
    path('liberar-mesa/', views.liberar_mesa, name='liberar_mesa'),
    path('marcar-entregue/', views.marcar_entregue, name='marcar_entregue'),
]
