from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Pedido

@receiver(post_save, sender=Pedido)
def notificar_cozinha(sender, instance, created, **kwargs):
    if created and instance.status == 'RECEBIDO':
        channel_layer = get_channel_layer()
        
        itens_lista = []
        for item in instance.itens.all():
            itens_lista.append(f"{item.quantidade}x {item.produto.nome}")

        async_to_sync(channel_layer.group_send)(
            'cozinha',
            {
                'type': 'novo_pedido',
                'pedido_id': instance.id,
                'mesa': instance.mesa.numero,
                'itens': itens_lista
            }
        )
