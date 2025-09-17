from django.urls import path
from . import views

app_name = 'creador_embarcaciones'

urlpatterns = [
    # Página de inicio
    path('', views.home, name='home'),

    # ========== URLs de Eliminación Masiva ==========
    # Eliminar todas las embarcaciones
    path('eliminar-todas-embarcaciones/', views.delete_all_embarcaciones, name='delete_all_embarcaciones'),

    # Eliminar todas las rutas y días
    path('eliminar-todas-rutas/', views.delete_all_rutas, name='delete_all_rutas'),

    # Eliminar todos los tipos de habitación
    path('eliminar-todos-tipos-habitacion/', views.delete_all_tipos_habitacion, name='delete_all_tipos_habitacion'),

    # Eliminar todos los tipos de local
    path('eliminar-todos-tipos-local/', views.delete_all_tipos_local, name='delete_all_tipos_local'),

    # ========== URLs para Embarcaciones ==========
    # Lista de embarcaciones
    path('embarcaciones/', views.EmbarcacionListView.as_view(), name='embarcacion_list'),

    # Crear nueva embarcación
    path('embarcaciones/crear/', views.EmbarcacionCreateView.as_view(), name='embarcacion_create'),

    # Detalles de embarcación
    path('embarcaciones/<int:pk>/', views.embarcacion_detail, name='embarcacion_detail'),

    # Editar embarcación
    path('embarcaciones/<int:pk>/editar/', views.embarcacion_update, name='embarcacion_update'),

    # Eliminar embarcación
    path('embarcaciones/<int:pk>/eliminar/', views.embarcacion_delete, name='embarcacion_delete'),

    # ========== URLs para Rutas ==========
    # Lista de rutas
    path('rutas/', views.RutaListView.as_view(), name='ruta_list'),

    # Crear nueva ruta
    path('rutas/crear/', views.RutaCreateView.as_view(), name='ruta_create'),

    # Detalles de ruta
    path('rutas/<int:pk>/', views.ruta_detail, name='ruta_detail'),

    # Editar ruta
    path('rutas/<int:pk>/editar/', views.ruta_update, name='ruta_update'),

    # Eliminar ruta
    path('rutas/<int:pk>/eliminar/', views.ruta_delete, name='ruta_delete'),

    # ========== URLs para Días ==========
    # Detalles de día
    path('dias/<int:pk>/', views.dia_detail, name='dia_detail'),

    # Editar día
    path('dias/<int:pk>/editar/', views.dia_update, name='dia_update'),

    # ========== URLs para Gestión de Estructura de Embarcaciones ==========
    # Detalles de embarcación con cubiertas
    path('embarcaciones/<int:pk>/detalles/', views.embarcacion_detail, name='embarcacion_detail'),

    # Detalles de cubierta específica
    path('embarcaciones/<int:embarcacion_pk>/cubiertas/<int:cubierta_pk>/', views.cubierta_detail, name='cubierta_detail'),

    # ========== URLs para Gestión de Locales ==========
    # Crear local en cubierta específica
    path('embarcaciones/<int:embarcacion_pk>/cubiertas/<int:cubierta_pk>/locales/crear/', views.local_create, name='local_create'),

    # Editar local
    path('locales/<int:pk>/editar/', views.local_update, name='local_update'),

    # Eliminar local
    path('locales/<int:pk>/eliminar/', views.local_delete, name='local_delete'),

    # ========== URLs para Gestión de Habitaciones ==========
    # Crear habitación en cubierta específica
    path('embarcaciones/<int:embarcacion_pk>/cubiertas/<int:cubierta_pk>/habitaciones/crear/', views.habitacion_create, name='habitacion_create'),

    # Editar habitación
    path('habitaciones/<int:pk>/editar/', views.habitacion_update, name='habitacion_update'),

    # Eliminar habitación
    path('habitaciones/<int:pk>/eliminar/', views.habitacion_delete, name='habitacion_delete'),

    # ========== URLs para Detalles Específicos ==========
    # Detalles específicos de local
    path('locales/<int:pk>/', views.local_detail, name='local_detail'),

    # Detalles específicos de habitación
    path('habitaciones/<int:pk>/', views.habitacion_detail, name='habitacion_detail'),

    # ========== URLs para Modales y Estándares ==========
    # Crear tipos estándar
    path('tipos/habitacion/crear/', views.crear_tipo_habitacion, name='crear_tipo_habitacion'),
    path('tipos/local/crear/', views.crear_tipo_local, name='crear_tipo_local'),

    # Obtener tipos vía AJAX
    path('api/tipos/habitacion/', views.obtener_tipos_habitacion, name='obtener_tipos_habitacion'),
    path('api/tipos/local/', views.obtener_tipos_local, name='obtener_tipos_local'),
]
