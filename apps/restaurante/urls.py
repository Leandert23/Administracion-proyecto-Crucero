from django.urls import path, include
from . import views

app_name = 'restaurantes'

urlpatterns = [
    # Main views
    path('', views.dashboard, name='dashboard'),
    path('stock/', views.stock_view, name='stock'),
    path('employees/', views.employees_view, name='employees'),
    path('maintenance/', views.maintenance_view, name='maintenance'),
    path('consumption/', views.consumption_view, name='consumption'),
    # Registros de consumo
    path('records/', views.records_view, name='records'),

    # Vistas específicas para restaurantes
    path('buffet/', views.buffet_view, name='buffet'),
    path('main-dining-room/', views.main_dining_room_view, name='main_dining_room'),
    path('especialidades/', views.especialidades_view, name='especialidades'),

    # AJAX endpoints
    path('ajax/add-item/', views.add_menu_item, name='add_menu_item'),
    path('ajax/add-employee/', views.add_employee, name='add_employee'),
    path('ajax/add-maintenance/', views.add_maintenance, name='add_maintenance'),
    path('ajax/register-consumption/', views.register_consumption, name='register_consumption'),
    path('ajax/get-menu-items/', views.get_menu_items, name='get_menu_items'),
    path('ajax/get-menus-for-day/', views.get_menus_for_day, name='get_menus_for_day'),
    path('ajax/register-bulk-consumption/', views.register_bulk_consumption, name='register_bulk_consumption'),
    path('ajax/get-restaurants/', views.get_restaurants, name='get_restaurants'),
]