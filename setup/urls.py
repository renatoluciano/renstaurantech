from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurantech.urls')), # <-- Inclui as rotas do app aqui
]
