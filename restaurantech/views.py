from django.shortcuts import render

def cozinha(request):
    return render(request, 'restaurantech/cozinha.html')
