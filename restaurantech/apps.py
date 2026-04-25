from django.apps import AppConfig

class RestaurantechConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurantech'

    def ready(self):
        import restaurantech.signals
