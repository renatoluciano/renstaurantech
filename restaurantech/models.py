from django.db import models

class Mesa(models.Model):
    STATUS_CHOICES = [
        ('LIVRE', 'Livre'),
        ('OCUPADA', 'Ocupada'),
        ('CONTA', 'Aguardando Conta'),
    ]

    numero = models.IntegerField(unique=True)
    capacidade = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='LIVRE')

    @property
    def total_da_conta(self):
        # Soma apenas o que ainda NÃO foi entregue ao cliente
        pedidos = self.pedido_set.filter(status__in=['RECEBIDO', 'PREPARANDO', 'PRONTO'])
        total = 0
        for pedido in pedidos:
            for item in pedido.itens.all():
                total += item.produto.preco * item.quantidade
        return total

    def __str__(self):
        return f"Mesa {self.numero} - Total Atual: R$ {self.total_da_conta}"

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Pedido(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('RECEBIDO', 'Recebido'),
        ('PREPARANDO', 'Em Preparação'),
        ('PRONTO', 'Pronto para Entrega'),
        ('ENTREGUE', 'Entregue'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='RECEBIDO')

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.numero}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    observacao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Mesa {self.pedido.mesa.numero})"
