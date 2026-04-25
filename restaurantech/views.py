import json # Adicionado este import que estava faltando para a função notificar_pronto
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
        
            # 1. Atualiza o status no banco de dados para PRONTO
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.status = 'PRONTO'
            pedido.save()
        
            # 2. Pega o controle das frequências de rádio
            channel_layer = get_channel_layer()
        
            # 3. Grita para o grupo dos garçons
            async_to_sync(channel_layer.group_send)(
                'garcons', # Nome do grupo definido no passo 24
                {
                    'type': 'prato_pronto', # Função do GarcomConsumer
                    'pedido_id': pedido_id,
                    'mesa': mesa
                }
            )
        
            return JsonResponse({'status': 'sucesso'})
        
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
            
    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido'}, status=400)
