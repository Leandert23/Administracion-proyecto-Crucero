from django.urls import path
from .api_views import PersonalListCreateAPI, PersonalRetrieveUpdateDeleteAPI
from .views import generar_plantel, vaciar_plantel

urlpatterns = [
    path('personal/', PersonalListCreateAPI.as_view(), name='personal-list-create'),
    path('personal/<int:pk>/', PersonalRetrieveUpdateDeleteAPI.as_view(), name='personal-rud'),
    path('generar-plantel/', generar_plantel, name='generar-plantel'),
    path('vaciar-plantel/', vaciar_plantel, name='vaciar-plantel'),
]
