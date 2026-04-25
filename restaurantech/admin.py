from django.contrib import admin
from .models import Mesa, Categoria, Produto, Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    inlines = [ItemPedidoInline]
    list_display = ('id', 'mesa', 'status', 'data_criacao')
    list_filter = ('status', 'mesa')

class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'status', 'capacidade', 'total_da_conta')
    list_filter = ('status',)

admin.site.register(Mesa, MesaAdmin)
admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Pedido, PedidoAdmin)
