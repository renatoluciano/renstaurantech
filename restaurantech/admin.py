from django.contrib import admin
from .models import Mesa, Categoria, Produto, Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0 # Remove linhas vazias extras que o Django cria por padrão
    
    # Define as colunas que vão aparecer na listagem do pedido
    readonly_fields = ('preco_unitario', 'subtotal')
    fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal', 'observacao')

    # Método que busca o preço direto da tabela de produtos
    def preco_unitario(self, obj):
        if obj.produto:
            return f"R$ {obj.produto.preco}"
        return "R$ 0.00"
    preco_unitario.short_description = "Preço Unitário"

    # Método que multiplica a quantidade pelo preço unitário
    def subtotal(self, obj):
        if obj.produto:
            valor = obj.produto.preco * obj.quantidade
            return f"R$ {valor}"
        return "R$ 0.00"
    subtotal.short_description = "Subtotal"


class PedidoAdmin(admin.ModelAdmin):
    inlines = [ItemPedidoInline]
    list_display = ('id', 'mesa', 'status', 'valor_total_pedido', 'data_criacao')
    list_filter = ('status', 'mesa')

    # Método que soma todos os subtotais para dar o valor final deste pedido
    def valor_total_pedido(self, obj):
        total = 0
        for item in obj.itens.all():
            total += item.produto.preco * item.quantidade
        return f"R$ {total}"
    valor_total_pedido.short_description = "Total do Pedido"


class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'status', 'capacidade', 'total_da_conta')
    list_filter = ('status',)


admin.site.register(Mesa, MesaAdmin)
admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Pedido, PedidoAdmin)
