from django.urls import path
from . import views

urlpatterns = [
    path('cruceros/', views.lista_cruceros, name='lista_cruceros'),
    path('cruceros/rapido/', views.crucero_creacion_rapida, name='crucero_creacion_rapida'),
    path('cruceros/<int:pk>/editar/', views.crucero_editar, name='crucero_editar'),
]
