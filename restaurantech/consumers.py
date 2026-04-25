import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CozinhaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.grupo_cozinha = 'cozinha'
        await self.channel_layer.group_add(self.grupo_cozinha, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.grupo_cozinha, self.channel_name)

    async def novo_pedido(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'novo_pedido',
            'pedido_id': event['pedido_id'],
            'mesa': event['mesa'],
            'itens': event['itens']
        }))

class GarcomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.grupo_garcom = 'garcons'
        await self.channel_layer.group_add(self.grupo_garcom, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.grupo_garcom, self.channel_name)

    async def prato_pronto(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'prato_pronto',
            'mesa': event['mesa'],
            'pedido_id': event['pedido_id']
        }))

    async def solicitacao_conta(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'solicitacao_conta',
            'mesa': event['mesa'],
            'total': event['total']
        }))
