from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    # Página principal
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de ubicaciones
    path('ubicaciones/', views.ubicacion_list, name='ubicacion_list'),
    path('ubicaciones/crear/', views.ubicacion_create, name='ubicacion_create'),
    path('ubicaciones/<int:pk>/', views.ubicacion_detail, name='ubicacion_detail'),
    path('ubicaciones/<int:pk>/editar/', views.ubicacion_update, name='ubicacion_update'),
    path('ubicaciones/<int:pk>/eliminar/', views.ubicacion_delete, name='ubicacion_delete'),
    
    # Gestión de productos
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/crear/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/', views.producto_detail, name='producto_detail'),
    path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    
    # Inventario
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('inventario/actualizar/<int:pk>/', views.inventario_update, name='inventario_update'),
    path('inventario/stock-bajo/', views.stock_bajo, name='stock_bajo'),
    
    # Equipos
    path('equipos/', views.equipo_list, name='equipo_list'),
    path('equipos/crear/', views.equipo_create, name='equipo_create'),
    path('equipos/<int:pk>/', views.equipo_detail, name='equipo_detail'),
    path('equipos/<int:pk>/editar/', views.equipo_update, name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.equipo_delete, name='equipo_delete'),
    
    # Tareas de mantenimiento
    path('tareas/', views.tarea_list, name='tarea_list'),
    path('tareas/crear/', views.tarea_create, name='tarea_create'),
    path('tareas/<int:pk>/', views.tarea_detail, name='tarea_detail'),
    path('tareas/<int:pk>/editar/', views.tarea_update, name='tarea_update'),
    path('tareas/<int:pk>/eliminar/', views.tarea_delete, name='tarea_delete'),
    path('tareas/<int:pk>/iniciar/', views.tarea_iniciar, name='tarea_iniciar'),
    path('tareas/<int:pk>/completar/', views.tarea_completar, name='tarea_completar'),
    
    # Reportes de incidentes
    path('incidentes/', views.incidente_list, name='incidente_list'),
    path('incidentes/crear/', views.incidente_create, name='incidente_create'),
    path('incidentes/<int:pk>/', views.incidente_detail, name='incidente_detail'),
    path('incidentes/<int:pk>/editar/', views.incidente_update, name='incidente_update'),
    path('incidentes/<int:pk>/resolver/', views.incidente_resolver, name='incidente_resolver'),
    
    # Reportes y estadísticas
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/tareas-pendientes/', views.reporte_tareas_pendientes, name='reporte_tareas_pendientes'),
    path('reportes/equipos-vencidos/', views.reporte_equipos_vencidos, name='reporte_equipos_vencidos'),
    path('reportes/consumo-productos/', views.reporte_consumo_productos, name='reporte_consumo_productos'),
    
    # API endpoints para AJAX
    path('api/ubicaciones/', views.api_ubicaciones, name='api_ubicaciones'),
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/equipos/', views.api_equipos, name='api_equipos'),
    path('api/tareas/', views.api_tareas, name='api_tareas'),
]
