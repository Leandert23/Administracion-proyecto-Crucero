# Módulo de Administración

Este módulo proporciona funcionalidades de administración y gestión del sistema para la aplicación de administración de cruceros.

## Características

### 🎛️ Dashboard Principal
- Vista general del estado del sistema
- Estadísticas rápidas de ventas, inventario y actividades
- Actividades recientes del sistema
- Actividades por módulo

### ⚙️ Configuración del Sistema
- Gestión de configuraciones generales del sistema
- Edición de parámetros del sistema
- Historial de cambios de configuración

### 📋 Logs de Actividad
- Registro completo de actividades del sistema
- Filtros por tipo de actividad, módulo, usuario y fecha
- Paginación para manejo de grandes volúmenes de datos
- Información detallada de cada actividad

### 💾 Respaldos del Sistema
- Creación de respaldos manuales del sistema
- Historial de respaldos realizados
- Estados de respaldo (iniciado, en proceso, completado, fallido)
- Información de tamaño y fecha de respaldos

### 📊 Reportes del Sistema
- Generación de reportes personalizados
- Tipos de reportes: ventas, inventario, usuarios, actividades, financiero
- Múltiples formatos de exportación (PDF, Excel, CSV)
- Historial de reportes generados

### 📈 Estadísticas del Sistema
- Gráficos de actividades por día
- Usuarios más activos
- Métricas de uso del sistema
- Visualización con Chart.js

## Modelos de Datos

### ConfiguracionSistema
- Almacena configuraciones generales del sistema
- Campos: nombre, valor, descripcion, fechas de creación/actualización

### LogActividad
- Registra todas las actividades del sistema
- Campos: usuario, crucero, tipo_actividad, descripcion, modulo, fecha_hora, ip_address, user_agent

### BackupSistema
- Gestiona los respaldos del sistema
- Campos: nombre_archivo, ruta_archivo, tamaño_archivo, estado, fechas, usuario, descripcion

### ReporteSistema
- Almacena información de reportes generados
- Campos: nombre, tipo_reporte, parametros, archivo_generado, fecha_generacion, usuario, crucero

## URLs

- `/administracion/<crucero_id>/` - Dashboard principal
- `/administracion/<crucero_id>/configuracion/` - Configuración del sistema
- `/administracion/<crucero_id>/logs/` - Logs de actividad
- `/administracion/<crucero_id>/respaldos/` - Gestión de respaldos
- `/administracion/<crucero_id>/reportes/` - Generación de reportes
- `/administracion/<crucero_id>/estadisticas/` - Estadísticas del sistema

## Características Técnicas

### Seguridad
- Todas las vistas requieren autenticación (`@login_required`)
- Registro de actividades con IP y User-Agent
- Validación de permisos por crucero

### Estética
- Diseño consistente con el resto de la aplicación
- Sidebar común con navegación integrada
- Responsive design para dispositivos móviles
- Uso de colores y tipografía estándar del sistema

### Funcionalidades
- Integración completa con otros módulos
- Sistema de logs automático
- Filtros avanzados en todas las vistas
- Paginación para mejor rendimiento
- Gráficos interactivos con Chart.js

## Instalación

1. El módulo ya está incluido en `INSTALLED_APPS`
2. Ejecutar migraciones: `python manage.py migrate`
3. El módulo estará disponible en `/administracion/`

## Uso

1. Acceder al dashboard desde cualquier módulo usando el sidebar
2. Navegar entre las diferentes secciones de administración
3. Configurar el sistema según las necesidades
4. Monitorear actividades y generar reportes
5. Realizar respaldos regulares del sistema

## Dependencias

- Django 5.2+
- Chart.js para gráficos
- Apps: cruceros, ventas, almacen (para estadísticas)
