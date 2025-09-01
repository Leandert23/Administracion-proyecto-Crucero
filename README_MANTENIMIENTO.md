# Módulo de Mantenimiento - Sistema de Cruceros

## Descripción

Este módulo proporciona un sistema completo de gestión de mantenimiento para cruceros, basado en la información del contexto proporcionada. El sistema incluye gestión de ubicaciones, inventario de productos, equipos, tareas de mantenimiento y reportes de incidentes.

## Características Principales

### 🏗️ Gestión de Ubicaciones
- Sistema de ubicaciones siguiendo el formato **XABCD** (Cubierta-Uso-Identificador-Número)
- Soporte para diferentes tipos de uso: habitaciones, restaurantes, bares, almacenes, entretenimiento
- Validación automática de códigos de ubicación

### 📦 Gestión de Inventario
- **5 categorías de productos** basadas en el Excel del contexto:
  - Productos Químicos de Limpieza e Higiene
  - Consumibles de Higiene (Descartables)
  - Repuestos Críticos y Filtros
  - Fluidos y Lubricantes
  - Herramientas y Equipos de Seguridad
- Control de stock mínimo y actual
- Alertas de stock bajo
- Gestión por tipo de crucero (pequeño, mediano, grande)

### ⚙️ Gestión de Equipos
- Registro de equipos con ubicación específica
- Estados: Operativo, En Mantenimiento, Averiado, Fuera de Servicio
- Programación de revisiones preventivas
- Historial de mantenimientos

### 🔧 Tareas de Mantenimiento
- **4 tipos de tareas**: Preventivo, Correctivo, Emergencia, Inspección
- **4 niveles de prioridad**: Baja, Media, Alta, Crítica
- **4 estados**: Pendiente, En Progreso, Completada, Cancelada
- Asignación a técnicos
- Control de tiempos estimados vs reales
- Registro de productos utilizados

### 🚨 Reportes de Incidentes
- Reportes de incidentes con diferentes niveles de severidad
- Generación automática de tareas de mantenimiento
- Seguimiento de resolución

### 📊 Dashboard y Reportes
- Dashboard con estadísticas en tiempo real
- Gráficos de estado de equipos y tareas
- Alertas de tareas próximas a vencer
- Reportes de consumo de productos
- Equipos con revisión próxima

## Estructura del Proyecto

```
mantenimiento/
├── models.py              # Modelos de base de datos
├── views.py               # Vistas y lógica de negocio
├── forms.py               # Formularios
├── admin.py               # Configuración del admin de Django
├── urls.py                # URLs del módulo
├── apps.py                # Configuración de la aplicación
└── management/
    └── commands/
        └── populate_initial_data.py  # Comando para datos iniciales

templates/
├── base.html              # Template base
└── mantenimiento/
    └── dashboard.html     # Dashboard principal
```

## Modelos de Datos

### TipoCrucero
- Define los 3 tipos de crucero: pequeño (2000 pasajeros), mediano (4000), grande (6000)
- Capacidad de pasajeros, número de tripulantes, número de cubiertas

### Ubicacion
- Implementa el formato XABCD del contexto
- X = Cubierta (1-18)
- A = Uso (0-9: habitaciones, restaurantes, bares, etc.)
- B = Identificador (A-Z)
- CD = Número (01-99)

### Producto
- Productos de mantenimiento con categorías
- Unidades: litro, kg, rollo, paquete, unidad, set, par
- Notas y descripciones específicas

### InventarioProducto
- Stock por producto y tipo de crucero
- Cantidad requerida, stock mínimo, stock actual
- Estado automático: crítico, bajo, normal

### Equipo
- Equipos específicos del crucero
- Estados y programación de revisiones
- Ubicación y observaciones

### TareaMantenimiento
- Tareas con tipos, prioridades y estados
- Asignación y control de tiempos
- Relación con equipos y ubicaciones

### ReporteIncidente
- Incidentes con severidad y seguimiento
- Generación de tareas automáticas

## Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Poblar datos iniciales
```bash
python manage.py populate_initial_data
```

### 4. Crear superusuario (si no se creó automáticamente)
```bash
python manage.py createsuperuser
```

### 5. Ejecutar servidor
```bash
python manage.py runserver
```

## Acceso al Sistema

- **URL principal**: http://localhost:8000/
- **Admin Django**: http://localhost:8000/admin/

**Nota**: Para crear un superusuario, ejecuta: `python manage.py createsuperuser`

## Funcionalidades del Dashboard

### Estadísticas Principales
- Total de equipos
- Tareas pendientes
- Productos con stock bajo
- Incidentes pendientes

### Gráficos
- **Estado de Equipos**: Distribución por estado (operativo, mantenimiento, averiado, fuera de servicio)
- **Estado de Tareas**: Distribución por estado (pendiente, en progreso, completada, vencida)

### Alertas
- Tareas próximas a vencer (próximos 7 días)
- Equipos con revisión próxima (próximos 30 días)

### Acciones Rápidas
- Crear nueva tarea
- Reportar incidente
- Registrar equipo
- Agregar producto

## Datos Iniciales

El comando `populate_initial_data` crea automáticamente:

### Tipos de Crucero
- Crucero Pequeño (2000 pasajeros, 667 tripulantes, 12 cubiertas)
- Crucero Mediano (4000 pasajeros, 1333 tripulantes, 15 cubiertas)
- Crucero Grande (6000 pasajeros, 2000 tripulantes, 18 cubiertas)

### Productos (basados en el Excel)
- **Químicos**: Lejía, Jabón líquido, Detergente desengrasante, etc.
- **Consumibles**: Papel higiénico, Toallas, Servilletas, Gel desinfectante
- **Repuestos**: Filtros de aceite, combustible, aire HVAC, agua
- **Fluidos**: Aceite lubricante, aceite hidráulico
- **Herramientas**: Juegos de llaves, multímetros, termómetros, EPP

### Ubicaciones de Ejemplo
- Habitaciones en cubiertas 2-8
- Restaurantes y bares
- Almacenes
- Áreas de entretenimiento

### Equipos de Ejemplo
- Motores principales
- Generadores eléctricos
- Sistema HVAC
- Con estados y revisiones programadas

## Características Técnicas

### Tecnologías Utilizadas
- **Django 4.2.7**: Framework web
- **Bootstrap 5.3**: Frontend responsive
- **Font Awesome 6.4**: Iconos
- **Chart.js**: Gráficos interactivos
- **SQLite**: Base de datos (configurable)

### Seguridad
- Autenticación requerida para todas las vistas
- Validación de formularios
- Protección CSRF
- Filtros de permisos

### Responsive Design
- Interfaz adaptativa para móviles y tablets
- Sidebar colapsable en dispositivos pequeños
- Gráficos responsivos

## Personalización

### Configuración de Tipos de Crucero
Editar `settings.py`:
```python
MANTENIMIENTO_CONFIG = {
    'CRUCERO_TIPOS': [
        ('pequeño', 'Crucero Pequeño (2000 pasajeros)'),
        ('mediano', 'Crucero Mediano (4000 pasajeros)'),
        ('grande', 'Crucero Grande (6000 pasajeros)'),
    ],
    'UBICACION_FORMATO': 'XABCD',
}
```

### Agregar Nuevos Productos
1. Crear en el admin de Django
2. O agregar al comando `populate_initial_data.py`
3. Configurar inventario por tipo de crucero

### Personalizar Estados y Tipos
Los estados y tipos están definidos como choices en los modelos y se pueden modificar fácilmente.

## Reportes Disponibles

### Tareas Pendientes
- Lista de tareas pendientes
- Tareas vencidas
- Filtros por tipo, prioridad, asignado

### Equipos con Revisión Próxima
- Equipos con revisión vencida
- Equipos con revisión en próximos 30 días

### Consumo de Productos
- Productos más utilizados (último mes)
- Productos con stock bajo
- Estadísticas de consumo

## Contribución

Para contribuir al módulo:

1. Crear una rama para tu feature
2. Implementar cambios
3. Agregar tests si es necesario
4. Actualizar documentación
5. Crear pull request

## Licencia

Este módulo es parte del proyecto de Sistema de Administración de Cruceros.

## Contacto

Para soporte o consultas sobre el módulo de mantenimiento, contactar al equipo de desarrollo.

---

**Nota**: Este módulo está diseñado específicamente para la gestión de mantenimiento de cruceros basándose en la información del contexto proporcionada, incluyendo el formato de ubicaciones XABCD y las especificaciones de productos del Excel.
