from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Mesa, Produto, Pedido, ItemPedido
import json

def mesa(request):
    return render(request, 'restaurantech/mesa.html')

@csrf_exempt
def fazer_pedido(request):
    if request.method == 'POST':
        # 1. Encontra ou cria a Mesa 1 para testes
        mesa_obj, _ = Mesa.objects.get_or_create(numero=1, defaults={'capacidade': 4})
        
        # 2. Cria o Pedido
        pedido = Pedido.objects.create(mesa=mesa_obj)
        
        # 3. Busca produtos fictícios no BD (certifique-se de criá-los no /admin primeiro)
        hamburguer, _ = Produto.objects.get_or_create(nome="Hambúrguer", defaults={'preco': 35.00, 'categoria_id': 1})
        refri, _ = Produto.objects.get_or_create(nome="Refrigerante", defaults={'preco': 7.00, 'categoria_id': 1})
        
        # 4. Vincula os itens ao pedido
        ItemPedido.objects.create(pedido=pedido, produto=hamburguer, quantidade=1)
        ItemPedido.objects.create(pedido=pedido, produto=refri, quantidade=1)
        
        # 5. Retorna sucesso (Isso dispara o Signal do Passo 21!)
        return JsonResponse({'status': 'sucesso', 'pedido_id': pedido.id})
