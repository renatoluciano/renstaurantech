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
    """Renderiza a página do tablet da mesa para o cliente fazer o pedido."""
    return render(request, 'restaurantech/mesa.html')

# 3. ROTA DE PROCESSAMENTO DO PEDIDO
@csrf_exempt
def fazer_pedido(request):
    """Processa o clique do botão no tablet, salva no banco e avisa a cozinha."""
    if request.method == 'POST':
        try:
            # ETAPA A: Cria a mesa e a categoria caso não existam no banco
            mesa_obj, _ = Mesa.objects.get_or_create(
                numero=1, 
                defaults={'capacidade': 4}
            )
            categoria_obj, _ = Categoria.objects.get_or_create(
                nome="Geral"
            )
            
            # ETAPA B: Cria os produtos fictícios caso não existam no banco
            hamburguer, _ = Produto.objects.get_or_create(
                nome="Hamburguer", 
                defaults={'preco': 35.00, 'categoria': categoria_obj}
            )
            refri, _ = Produto.objects.get_or_create(
                nome="Refrigerante", 
                defaults={'preco': 7.00, 'categoria': categoria_obj}
            )
            
            # ETAPA C: Cria o pedido e vincula os itens no banco de dados
            pedido = Pedido.objects.create(mesa=mesa_obj)
            ItemPedido.objects.create(pedido=pedido, produto=hamburguer, quantidade=1)
            ItemPedido.objects.create(pedido=pedido, produto=refri, quantidade=1)
            
            # ETAPA D: Tenta disparar a mensagem via WebSocket para a cozinha
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'cozinha', # Nome do grupo definido no arquivo consumers.py
                    {
                        'type': 'novo_pedido', # Nome da função dentro do CozinhaConsumer
                        'pedido_id': pedido.id,
                        'mesa': 1,
                        'itens': ['1x Hamburguer', '1x Refrigerante']
                    }
                )
            except Exception as websocket_error:
                # Se o WebSocket falhar (falta de Redis, etc), o código não quebra!
                print(f"Aviso: Pedido salvo no banco, mas falhou ao enviar via WebSocket: {websocket_error}")

            # Retorna sucesso absoluto para o navegador do tablet
            return JsonResponse({'status': 'sucesso', 'pedido_id': pedido.id})
            
        except Exception as e:
            # Se der qualquer erro crítico no Python ao salvar no banco, avisa no terminal
            print(f"Erro Crítico no Servidor: {e}")
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido'}, status=400)
