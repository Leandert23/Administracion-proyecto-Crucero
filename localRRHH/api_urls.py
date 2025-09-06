from django.urls import path
from .api_views import PersonalListCreateAPI, PersonalRetrieveUpdateDeleteAPI

urlpatterns = [
    path('personal/', PersonalListCreateAPI.as_view(), name='personal-list-create'),
    path('personal/<int:pk>/', PersonalRetrieveUpdateDeleteAPI.as_view(), name='personal-rud'),
]
