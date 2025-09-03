from . import views
from django.urls import path , include

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('personas/', views.lista_personas, name='lista_personas'),
    path('api/agregar_personal/', views.agregar_personal, name='agregar_personal'),
]