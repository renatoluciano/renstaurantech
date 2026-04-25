from django.db import models

class Mesa(models.Model):
    # Opções de status para a mesa
    STATUS_CHOICES = [
        ('LIVRE', 'Livre'),
        ('OCUPADA', 'Ocupada'),
        ('CONTA', 'Aguardando Conta'),
    ]

    numero = models.IntegerField(unique=True)
    capacidade = models.IntegerField()
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='LIVRE'
    )

    def __str__(self):
        return f"Mesa {self.numero}"
    
class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    disponivel = models.BooleanField(default=True) # Para pausar vendas se acabar o estoque

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

