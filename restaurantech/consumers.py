import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CozinhaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Cria um grupo chamado 'cozinha' para todos os tablets da cozinha
        self.grupo_cozinha = 'cozinha'
        
        await self.channel_layer.group_add(
            self.grupo_cozinha,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.grupo_cozinha,
            self.channel_name
        )

    # Recebe a mensagem enviada pelo Django e encaminha para o WebSocket do tablet
    async def novo_pedido(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'novo_pedido',
            'pedido_id': event['pedido_id'],
            'mesa': event['mesa'],
            'itens': event['itens']
        }))
