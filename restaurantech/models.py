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
