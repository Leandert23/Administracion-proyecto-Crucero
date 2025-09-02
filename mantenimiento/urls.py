from django.urls import path
from .views import (
    dashboard,
    # ubicaciones
    ubicacion_list, ubicacion_create, ubicacion_detail, ubicacion_update, ubicacion_delete,
    # productos
    producto_list, producto_create, producto_detail, producto_update, producto_delete,
    # inventario
    inventario_list, inventario_update, stock_bajo,
    # equipos
    equipo_list, equipo_create, equipo_detail, equipo_update, equipo_delete,
    # tareas
    tarea_list, tarea_create, tarea_detail, tarea_update, tarea_delete,
    tarea_asignar_personal, tarea_registrar_producto, tarea_cambiar_estado, tarea_finalizar,
    tarea_crear_preventiva, tarea_crear_correctiva, tarea_workflow,
    # incidentes
    incidente_list, incidente_create, incidente_detail, incidente_update, incidente_resolver,
    # reportes
    reportes, reporte_tareas_pendientes, reporte_equipos_vencidos, reporte_consumo_productos,
    # piscinas
    piscina_list, piscina_create, piscina_update, piscina_detail, medicion_piscina_create, piscina_trends,
)

app_name = 'mantenimiento'

urlpatterns = [
    # Página principal
    path('', dashboard, name='dashboard'),
    
    # Gestión de ubicaciones
    path('ubicaciones/', ubicacion_list, name='ubicacion_list'),
    path('ubicaciones/crear/', ubicacion_create, name='ubicacion_create'),
    path('ubicaciones/<int:pk>/', ubicacion_detail, name='ubicacion_detail'),
    path('ubicaciones/<int:pk>/editar/', ubicacion_update, name='ubicacion_update'),
    path('ubicaciones/<int:pk>/eliminar/', ubicacion_delete, name='ubicacion_delete'),
    
    # Gestión de productos
    path('productos/', producto_list, name='producto_list'),
    path('productos/crear/', producto_create, name='producto_create'),
    path('productos/<int:pk>/', producto_detail, name='producto_detail'),
    path('productos/<int:pk>/editar/', producto_update, name='producto_update'),
    path('productos/<int:pk>/eliminar/', producto_delete, name='producto_delete'),
    
    # Inventario
    path('inventario/', inventario_list, name='inventario_list'),
    path('inventario/actualizar/<int:pk>/', inventario_update, name='inventario_update'),
    path('inventario/stock-bajo/', stock_bajo, name='stock_bajo'),
    
    # Equipos
    path('equipos/', equipo_list, name='equipo_list'),
    path('equipos/crear/', equipo_create, name='equipo_create'),
    path('equipos/<int:pk>/', equipo_detail, name='equipo_detail'),
    path('equipos/<int:pk>/editar/', equipo_update, name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', equipo_delete, name='equipo_delete'),
    
    # Tareas de mantenimiento
    path('tareas/', tarea_list, name='tarea_list'),
    path('tareas/crear/', tarea_create, name='tarea_create'),
    path('tareas/crear-preventiva/', tarea_crear_preventiva, name='tarea_crear_preventiva'),
    path('tareas/crear-correctiva/', tarea_crear_correctiva, name='tarea_crear_correctiva'),
    path('tareas/<int:pk>/', tarea_detail, name='tarea_detail'),
    path('tareas/<int:pk>/editar/', tarea_update, name='tarea_update'),
    path('tareas/<int:pk>/eliminar/', tarea_delete, name='tarea_delete'),

    path('tareas/<int:pk>/asignar-personal/', tarea_asignar_personal, name='tarea_asignar_personal'),
    path('tareas/<int:pk>/registrar-producto/', tarea_registrar_producto, name='tarea_registrar_producto'),
    path('tareas/<int:pk>/cambiar-estado/', tarea_cambiar_estado, name='tarea_cambiar_estado'),
    path('tareas/<int:pk>/finalizar/', tarea_finalizar, name='tarea_finalizar'),
    path('tareas/<int:pk>/workflow/', tarea_workflow, name='tarea_workflow'),
    
    # Reportes de incidentes
    path('incidentes/', incidente_list, name='incidente_list'),
    path('incidentes/crear/', incidente_create, name='incidente_create'),
    path('incidentes/<int:pk>/', incidente_detail, name='incidente_detail'),
    path('incidentes/<int:pk>/editar/', incidente_update, name='incidente_update'),
    path('incidentes/<int:pk>/resolver/', incidente_resolver, name='incidente_resolver'),
    
    # Reportes y estadísticas
    path('reportes/', reportes, name='reportes'),
    path('reportes/tareas-pendientes/', reporte_tareas_pendientes, name='reporte_tareas_pendientes'),
    path('reportes/equipos-vencidos/', reporte_equipos_vencidos, name='reporte_equipos_vencidos'),
    path('reportes/consumo-productos/', reporte_consumo_productos, name='reporte_consumo_productos'),
    
    # Piscinas
    path('piscinas/', piscina_list, name='piscina_list'),
    path('piscinas/crear/', piscina_create, name='piscina_create'),
    path('piscinas/<int:pk>/', piscina_detail, name='piscina_detail'),
    path('piscinas/<int:pk>/editar/', piscina_update, name='piscina_update'),
    path('piscinas/<int:pk>/tendencias/', piscina_trends, name='piscina_trends'),
    path('piscinas/medicion/crear/', medicion_piscina_create, name='medicion_piscina_create'),

]
