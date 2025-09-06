from django.apps import AppConfig

class AdministracionConfig(AppConfig):
    name = 'apps.administracion'

    def ready(self):
        import apps.administracion.signals
