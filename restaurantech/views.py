import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Mesa, Categoria, Produto, Pedido, ItemPedido

# 1. TELA DA COZINHA
def cozinha(request):
    """Renderiza a página onde o cozinheiro recebe os pedidos em tempo real."""
    return render(request, 'restaurantech/cozinha.html')

# 2. TELA DA MESA (CLIENTE)
def mesa(request):
    """Busca as categorias e produtos ativos para exibir no cardápio."""
    categorias = Categoria.objects.all()
    produtos = Produto.objects.filter(disponivel=True)
    
    contexto = {
        'categorias': categorias,
        'produtos': produtos,
    }
    return render(request, 'restaurantech/mesa.html', contexto)

# 3. ROTA DE PROCESSAMENTO DO PEDIDO
@csrf_exempt
def fazer_pedido(request):
    """Processa a lista dinâmica do carrinho, salva no banco e avisa a cozinha."""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            itens_carrinho = dados.get('itens', [])
            
            if not itens_carrinho:
                return JsonResponse({'status': 'erro', 'mensagem': 'Carrinho vazio'}, status=400)

            mesa_obj, _ = Mesa.objects.get_or_create(numero=1, defaults={'capacidade': 4})
            pedido = Pedido.objects.create(mesa=mesa_obj)
            
            itens_para_cozinha = []
            for item in itens_carrinho:
                produto_id = item.get('id')
                produto = Produto.objects.get(id=produto_id)
                
                ItemPedido.objects.create(pedido=pedido, produto=produto, quantidade=1)
                itens_para_cozinha.append(f"1x {produto.nome}")

            # Dispara WebSocket para a cozinha
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
                print(f"Erro WebSocket: {e}")

            return JsonResponse({'status': 'sucesso', 'pedido_id': pedido.id})
            
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro'}, status=400)

# 4. TELA DO GARÇOM
def garcom(request):
    """Renderiza a página do tablet do garçom."""
    return render(request, 'restaurantech/garcom.html')

# 5. ROTA DE NOTIFICAÇÃO DE PRATO PRONTO
@csrf_exempt
def notificar_pronto(request):
    """Atualiza o pedido para PRONTO e avisa o garçom via WebSocket."""
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

# 6. ROTA DE PEDIDO DE CONTA
@csrf_exempt
def pedir_conta(request):
    """Muda o status da mesa para CONTA e avisa o garçom em tempo real."""
    if request.method == 'POST':
        try:
            mesa_obj = Mesa.objects.get(numero=1)
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

# 7. ROTA DE LIBERAÇÃO DE MESA
@csrf_exempt
def liberar_mesa(request):
    """Muda o status da mesa para LIVRE após pagamento."""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            numero_mesa = dados.get('mesa')
            
            mesa_obj = Mesa.objects.get(numero=numero_mesa)
            mesa_obj.status = 'LIVRE'
            mesa_obj.save()
            
            return JsonResponse({'status': 'sucesso'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
