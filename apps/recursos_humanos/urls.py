from django.urls import path
from .views import index, personal_delete, personal_update, generar_plantel, vaciar_plantel

urlpatterns = [
    path('', index, name='index'),
    path('generar-plantel/', generar_plantel, name='generar-plantel'),
    path('vaciar-plantel/', vaciar_plantel, name='vaciar-plantel'),
    path('personal/<int:pk>/delete/', personal_delete, name='personal-delete'),
    path('personal/<int:pk>/update/', personal_update, name='personal-update'),
]
