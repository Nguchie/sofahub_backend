from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        import core.signals
        # Import models to ensure signals are connected
        from products.models import Product, RoomCategory
        from blog.models import BlogPost