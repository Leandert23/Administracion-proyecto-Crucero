from django.apps import AppConfig

class AdministracionConfig(AppConfig):
    name = 'administracion'

    def ready(self):
        import administracion.signals
