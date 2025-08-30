from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cruceros, name='lista_cruceros'),
    path("<int:crucero_id>/", views.mostrar_inicio, name="gestion_crucero"),
]
