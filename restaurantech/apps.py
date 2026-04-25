from django.apps import AppConfig

class RestaurantechConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurantech'

    def ready(self):
        # Desativamos a linha abaixo colocando o caractere '#' na frente.
        # Isso impede que o Django carregue o arquivo de signals redundante.
        # import restaurantech.signals 
        pass
