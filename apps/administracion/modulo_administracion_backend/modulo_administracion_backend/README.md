# Módulo de Administración - Backend

Este es el backend completo del módulo de administración del sistema de gestión de cruceros. Contiene todos los archivos necesarios para el funcionamiento del backend de Django.

## Estructura del Módulo

```
modulo_administracion_backend/
├── __init__.py
├── admin.py                 # Configuración del panel de administración de Django
├── apps.py                  # Configuración de la aplicación
├── forms.py                 # Formularios personalizados
├── models.py                # Modelos de base de datos
├── signals.py               # Señales de Django para comunicación entre módulos
├── urls.py                  # Configuración de URLs
├── utils.py                 # Utilidades y decoradores
├── views.py                 # Vistas y lógica de negocio
├── migrations/              # Migraciones de base de datos
│   ├── __init__.py
│   ├── 0001_initial.py
│   └── 0002_solicitudcompra.py
├── management/              # Comandos de gestión personalizados
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── asignar_rol_admin.py
│       ├── init_dashboard_data.py
│       └── init_roles.py
└── README.md               # Este archivo
```

## Modelos Principales

### 1. Administracion
- Gestiona la información financiera y operativa de cada crucero
- Campos: costos_totales, ganancias_totales, presupuesto_estimado, etc.
- Métodos: calcular_presupuesto_estimado(), actualizar_campos_financieros()

### 2. Alerta
- Sistema de alertas para notificaciones importantes
- Campos: mensaje, fecha, leida, administracion

### 3. SolicitudCompra
- Gestión de solicitudes de compra
- Estados: pending, approved, rejected
- Campos: monto, descripcion, estado, razon_rechazo

### 4. Sistema de Roles
- **Modulo**: Define los módulos del sistema
- **Rol**: Define roles específicos por módulo (admin, editor, lector, especialista)
- **UsuarioRol**: Asigna roles a usuarios con fechas de expiración

## Funcionalidades Principales

### Dashboard de Administración
- Vista general de todos los cruceros
- Datos financieros y operativos
- Sistema de alertas
- Gestión de solicitudes de compra

### Sistema de Roles y Permisos
- Control granular de acceso por módulo
- Roles con fechas de expiración
- Decoradores para verificación de permisos
- Gestión de usuarios y roles

### APIs REST
- `/api/cruceros-dashboard/` - Datos del dashboard
- `/api/purchase-requests/<id>/approve/` - Aprobar solicitudes
- `/api/purchase-requests/<id>/reject/` - Rechazar solicitudes

## Instalación y Configuración

### 1. Dependencias Requeridas
```python
# En settings.py, agregar a INSTALLED_APPS:
INSTALLED_APPS = [
    # ... otras apps
    'apps.administracion',
    'apps.cruceros',  # Dependencia requerida
]
```

### 2. Migraciones
```bash
python manage.py makemigrations administracion
python manage.py migrate
```

### 3. Comandos de Inicialización
```bash
# Inicializar roles y módulos básicos
python manage.py init_roles

# Inicializar datos del dashboard
python manage.py init_dashboard_data

# Asignar rol de administrador a un usuario
python manage.py asignar_rol_admin username
```

## Uso del Sistema

### Decoradores de Permisos
```python
from .utils import requerir_administrador_modulo, requerir_rol

@requerir_administrador_modulo('administracion')
def vista_admin(request):
    # Solo administradores del módulo administración
    pass

@requerir_rol('administracion', 'editor')
def vista_editor(request):
    # Solo editores del módulo administración
    pass
```

### Verificación de Roles en Vistas
```python
from .utils import usuario_tiene_rol, obtener_roles_usuario

def mi_vista(request):
    if usuario_tiene_rol(request.user, 'administracion', 'admin'):
        # Usuario es administrador
        pass
    
    roles = obtener_roles_usuario(request.user)
    # Obtener todos los roles del usuario
```

## Características Técnicas

### Seguridad
- Sistema de roles granular
- Verificación de permisos en cada vista
- Decoradores para control de acceso
- Validación de fechas de expiración de roles

### Escalabilidad
- Diseño modular
- Señales para comunicación entre módulos
- APIs REST para integración
- Comandos de gestión personalizados

### Mantenibilidad
- Código bien documentado
- Separación clara de responsabilidades
- Utilidades reutilizables
- Tests incluidos

## Integración con Otros Módulos

El módulo de administración se integra con:
- **Cruceros**: Para obtener información de los barcos
- **Compras**: Para gestionar solicitudes de compra
- **Ventas**: Para obtener datos de ganancias
- **Recursos Humanos**: Para datos de empleados

## Notas de Desarrollo

- Las señales están preparadas para comunicación con otros módulos
- El sistema de roles es extensible para nuevos módulos
- Los comandos de gestión facilitan la configuración inicial
- El dashboard es completamente funcional con datos simulados

## Soporte

Para cualquier duda o problema con el módulo de administración, revisar:
1. Los logs de Django
2. La configuración de roles y permisos
3. Las migraciones de base de datos
4. La integración con otros módulos
