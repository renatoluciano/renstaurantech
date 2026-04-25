import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Mesa, Categoria, Produto, Pedido, ItemPedido

# 1. KITCHEN SCREEN
def cozinha(request):
    """Renders the page where the chef receives real-time orders."""
    return render(request, 'restaurantech/cozinha.html')

# 2. TABLE SCREEN (CLIENT)
def mesa(request):
    """Fetches active categories and products to display on the menu."""
    categorias = Categoria.objects.all()
    produtos = Produto.objects.filter(disponivel=True)
    
    contexto = {
        'categorias': categorias,
        'produtos': produtos,
    }
    return render(request, 'restaurantech/mesa.html', contexto)

# 3. ORDER PROCESSING ROUTE
@csrf_exempt
def fazer_pedido(request):
    """Processes the dynamic list from the cart, saves to DB, and alerts the kitchen."""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            itens_carrinho = dados.get('itens', [])
            
            if not itens_carrinho:
                return JsonResponse({'status': 'erro', 'mensagem': 'Carrinho vazio'}, status=400)

            # Finds or creates table 1 for testing
            mesa_obj, _ = Mesa.objects.get_or_create(numero=1, defaults={'capacidade': 4})
            
            # SECURITY LOCK: Prevents new orders if the bill has already been requested
            if mesa_obj.status == 'CONTA':
                return JsonResponse({
                    'status': 'erro', 
                    'mensagem': 'A conta já foi solicitada. Não é possível adicionar novos pedidos!'
                }, status=403)

            pedido = Pedido.objects.create(mesa=mesa_obj)
            
            itens_para_cozinha = []
            for item in itens_carrinho:
                produto_id = item.get('id')
                produto = Produto.objects.get(id=produto_id)
                ItemPedido.objects.create(pedido=pedido, produto=produto, quantidade=1)
                itens_para_cozinha.append(f"1x {produto.nome}")

            # Triggers WebSocket to the kitchen
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'cozinha',
                    {
                        'type': 'novo_pedido',
                        'pedido_id': pedido.id,
                        'mesa': 1,
                        'itens': itens_para_cozinha
                    }
                )
            except Exception as e:
                print(f"WebSocket Error: {e}")

            return JsonResponse({'status': 'sucesso', 'pedido_id': pedido.id})
            
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro'}, status=400)

# 4. WAITER SCREEN
def garcom(request):
    """Renders the waiter tablet page loading tables requesting the bill."""
    mesas_aguardando = Mesa.objects.filter(status='CONTA')
    contexto = {
        'mesas_aguardando': mesas_aguardando
    }
    return render(request, 'restaurantech/garcom.html', contexto)

# 5. READY PLATE NOTIFICATION ROUTE
@csrf_exempt
def notificar_pronto(request):
    """Updates the order to READY and alerts the waiter via WebSocket."""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            pedido_id = dados.get('pedido_id')
            mesa = dados.get('mesa')
        
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.status = 'PRONTO'
            pedido.save()
        
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'garcons',
                {
                    'type': 'prato_pronto',
                    'pedido_id': pedido_id,
                    'mesa': mesa
                }
            )
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)

# 6. BILL REQUEST ROUTE
@csrf_exempt
def pedir_conta(request):
    """Muda o status da mesa para CONTA e avisa o garçom em tempo real."""
    if request.method == 'POST':
        try:
            mesa_obj = Mesa.objects.get(numero=1)
            
            # 🚨 NOVA TRAVA DE SEGURANÇA AQUI:
            # Verifica se o método property do Passo 18 resultou em zero
            if mesa_obj.total_da_conta == 0:
                return JsonResponse({
                    'status': 'erro', 
                    'mensagem': 'Você não pode pedir a conta sem ter feito nenhum pedido!'
                }, status=400)
            
            mesa_obj.status = 'CONTA'
            mesa_obj.save()
            
            total = mesa_obj.total_da_conta
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'garcons',
                {
                    'type': 'solicitacao_conta',
                    'mesa': 1,
                    'total': float(total)
                }
            )
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro'}, status=400)
# 7. TABLE RELEASE ROUTE
@csrf_exempt
def liberar_mesa(request):
    """Changes table status to FREE and completes active orders."""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            numero_mesa = dados.get('mesa')
            
            mesa_obj, _ = Mesa.objects.get_or_create(numero=numero_mesa, defaults={'capacidade': 4})
            mesa_obj.status = 'LIVRE'
            mesa_obj.save()
            
            # Clears the bill by completing active orders
            Pedido.objects.filter(mesa=mesa_obj).exclude(status='ENTREGUE').update(status='ENTREGUE')
            
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro'}, status=400)

# 8. MARK AS DELIVERED ROUTE
@csrf_exempt
def marcar_entregue(request):
    """Allows the waiter to mark the order as delivered."""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            pedido_id = dados.get('pedido_id')
            
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.status = 'ENTREGUE'
            pedido.save()
            
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro'}, status=400)
