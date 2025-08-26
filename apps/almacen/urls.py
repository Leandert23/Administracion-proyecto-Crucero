from django.urls import path
from . import views

urlpatterns = [
    path('cruceros/', views.lista_cruceros, name='lista_cruceros'),
    path('cruceros/nuevo/', views.crucero_nuevo, name='crucero_nuevo'),
    path('cruceros/<int:pk>/editar/', views.crucero_editar, name='crucero_editar'),
]
