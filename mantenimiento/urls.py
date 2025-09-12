from django.urls import path
from .views.dashboard import (
    dashboard, dashboard_update_data, create_task_api, task_count_api
)
from .views.equipos import equipo_list, equipo_create, equipo_detail, equipo_update, equipo_delete
from .views.tareas import (
    tarea_list, tarea_create, tarea_detail, tarea_update, tarea_delete,
    tarea_asignar_personal, tarea_eliminar_personal, tarea_registrar_producto, tarea_cambiar_estado, tarea_workflow,
    tarea_crear_preventiva, tarea_crear_correctiva, tarea_finalizar, tarea_siguiente_estado
)
from .views.piscinas import (
    piscina_list, piscina_create, piscina_detail, piscina_update,
    piscina_trends, medicion_piscina_create, piscina_update_data
)
from .views.inventario import inventario_list, inventario_update, stock_bajo
from .views.productos import producto_list, producto_create, producto_detail, producto_update, producto_delete
from .views.ubicaciones import ubicacion_list, ubicacion_create, ubicacion_detail, ubicacion_update, ubicacion_delete
from .views.incidentes import incidente_list, incidente_create, incidente_detail, incidente_update, incidente_resolver
from .views.reportes import reportes, reporte_tareas_pendientes, reporte_equipos_vencidos, reporte_consumo_productos
from .views.solicitudes import (
    solicitar_mantenimiento, solicitud_enviada, mis_solicitudes, solicitud_detail,
    gestionar_solicitudes, editar_solicitud, convertir_solicitud, cambiar_estado_solicitud
)

app_name = 'mantenimiento'

urlpatterns = [
    # Dashboard principal
    path('', dashboard, name='dashboard'),
    path('api/dashboard-update/', dashboard_update_data, name='dashboard_update_data'),

    # APIs para sistema universal de tareas
    path('api/tasks/create/', create_task_api, name='create_task_api'),
    path('api/tasks/count/', task_count_api, name='task_count_api'),
    
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
    path('tareas/<int:pk>/eliminar-personal/<int:asignacion_id>/', tarea_eliminar_personal, name='tarea_eliminar_personal'),
    path('tareas/<int:pk>/registrar-producto/', tarea_registrar_producto, name='tarea_registrar_producto'),
    path('tareas/<int:pk>/cambiar-estado/', tarea_cambiar_estado, name='tarea_cambiar_estado'),
    path('tareas/<int:pk>/workflow/', tarea_workflow, name='tarea_workflow'),
    path('tareas/<int:pk>/next/', tarea_siguiente_estado, name='tarea_siguiente_estado'),
    path('tareas/<int:pk>/finalizar/', tarea_finalizar, name='tarea_finalizar'),
    
    # Incidentes
    path('incidentes/', incidente_list, name='incidente_list'),
    path('incidentes/crear/', incidente_create, name='incidente_create'),
    path('incidentes/<int:pk>/', incidente_detail, name='incidente_detail'),
    path('incidentes/<int:pk>/editar/', incidente_update, name='incidente_update'),
    path('incidentes/<int:pk>/resolver/', incidente_resolver, name='incidente_resolver'),
    
    # Reportes
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
    path('api/piscinas/<int:pk>/update/', piscina_update_data, name='piscina_update_data'),
    
    # Solicitudes de Mantenimiento
    path('solicitar-mantenimiento/', solicitar_mantenimiento, name='solicitar_mantenimiento'),
    path('solicitar-mantenimiento/preventivo/', solicitar_mantenimiento, {'tipo': 'preventivo'}, name='solicitar_mantenimiento_preventivo'),
    path('solicitar-mantenimiento/correctivo/', solicitar_mantenimiento, {'tipo': 'correctivo'}, name='solicitar_mantenimiento_correctivo'),
    path('solicitud-enviada/<int:solicitud_id>/', solicitud_enviada, name='solicitud_enviada'),
    path('mis-solicitudes/', mis_solicitudes, name='mis_solicitudes'),
    path('solicitud/<int:solicitud_id>/', solicitud_detail, name='solicitud_detail'),
    
    # Gestión de Solicitudes (Módulo Mantenimiento)
    path('gestionar-solicitudes/', gestionar_solicitudes, name='gestionar_solicitudes'),
    path('editar-solicitud/<int:solicitud_id>/', editar_solicitud, name='editar_solicitud'),
    path('convertir-solicitud/<int:solicitud_id>/', convertir_solicitud, name='convertir_solicitud'),
    path('api/cambiar-estado-solicitud/<int:solicitud_id>/', cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
]
