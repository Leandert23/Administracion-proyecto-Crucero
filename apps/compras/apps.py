from django.apps import AppConfig


class ComprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.compras'

    def ready(self):
        from .signals import conectar_manejar_decision_solicitud_almacen
        conectar_manejar_decision_solicitud_almacen()
