# 🚀 Sistema de Botón Universal para Módulos

## 📋 Descripción

Sistema completo que permite a cada módulo del crucero tener acceso a su funcionalidad específica con validaciones apropiadas por módulo. El botón se adapta automáticamente al módulo actual y muestra las acciones disponibles según las validaciones configuradas.

## ✨ Características

### 🔧 **Detección Automática de Módulo**
- Detecta el módulo actual por URL, elementos del DOM y título de página
- Se actualiza automáticamente al navegar entre módulos
- Soporte para múltiples métodos de identificación

### 🎯 **Validaciones por Módulo**
- **Validaciones Universales**: Acceso a mantenimiento, reportes, etc.
- **Validaciones Específicas**: Cada módulo tiene sus propias reglas
- **Control de Acceso**: Basado en roles y permisos

### 📱 **Diseño Responsivo**
- Botón flotante que se adapta a todos los dispositivos
- Modal responsivo con información del módulo
- Optimizado para móviles, tablets y desktop

## 🏗️ Módulos Soportados

### 1. **Mantenimiento** 🔧
- **Color**: Azul (#3b82f6)
- **Icono**: fas fa-tools
- **Acciones**: Equipos, Tareas, Inventario, Incidentes, Piscinas, Reportes

### 2. **Servicios Médicos** 🏥
- **Color**: Rojo (#ef4444)
- **Icono**: fas fa-user-md
- **Acciones**: Pacientes, Inventario Médico, Citas, Mantenimiento, Reportes, Personal

### 3. **Almacén** 📦
- **Color**: Naranja (#f59e0b)
- **Icono**: fas fa-warehouse
- **Acciones**: Inventario, Stock, Pedidos, Mantenimiento, Reportes, Proveedores

### 4. **Recursos Humanos** 👥
- **Color**: Púrpura (#8b5cf6)
- **Icono**: fas fa-users-cog
- **Acciones**: Personal, Horarios, Mantenimiento, Reportes, Vacaciones

### 5. **Ventas** 💰
- **Color**: Verde (#10b981)
- **Icono**: fas fa-shopping-bag
- **Acciones**: Ventas, Procesar Venta, Productos, Mantenimiento, Reportes

### 6. **Reservas** 📅
- **Color**: Cian (#06b6d4)
- **Icono**: fas fa-calendar-check
- **Acciones**: Reservas, Nueva Reserva, Habitaciones, Mantenimiento, Reportes

### 7. **Restaurante** 🍽️
- **Color**: Naranja (#f97316)
- **Icono**: fas fa-utensils
- **Acciones**: Menú, Pedidos, Inventario, Mantenimiento, Reportes

### 8. **Bares** 🍸
- **Color**: Rosa (#ec4899)
- **Icono**: fas fa-cocktail
- **Acciones**: Menú, Pedidos, Inventario, Mantenimiento, Reportes

### 9. **Entretenimiento** 🎵
- **Color**: Lima (#84cc16)
- **Icono**: fas fa-music
- **Acciones**: Actividades, Horarios, Mantenimiento, Reportes

### 10. **Compras** 🛒
- **Color**: Índigo (#6366f1)
- **Icono**: fas fa-shopping-cart
- **Acciones**: Compras, Nueva Orden, Proveedores, Mantenimiento, Reportes

## 🔒 Sistema de Validaciones

### Validaciones Universales
- **canRequestMaintenance**: Todos los módulos pueden solicitar mantenimiento
- **canViewReports**: Acceso a reportes del módulo

### Validaciones Específicas por Módulo

#### Servicios Médicos
- `canViewPatients`: Ver información de pacientes
- `canManageMedicalInventory`: Gestionar inventario médico
- `canScheduleAppointments`: Agendar citas médicas

#### Recursos Humanos
- `canViewStaff`: Ver personal
- `canManageSchedules`: Gestionar horarios
- `canViewPayroll`: Ver nóminas (solo administradores)
- `canManageVacations`: Gestionar vacaciones

#### Mantenimiento
- `canViewEquipment`: Ver equipos
- `canCreateTasks`: Crear tareas
- `canManageInventory`: Gestionar inventario
- `canViewReports`: Ver reportes
- `canManagePools`: Gestionar piscinas
- `canHandleIncidents`: Manejar incidentes

## 📱 Diseño Responsivo

### Desktop (> 768px)
- Botón flotante en esquina superior derecha
- Modal centrado con grid de acciones
- Efectos hover y animaciones

### Tablet (768px - 992px)
- Botón adaptado con texto reducido
- Modal optimizado para pantalla media
- Grid de acciones ajustado

### Móvil (< 768px)
- Botón solo con icono
- Modal full-screen
- Lista vertical de acciones
- Navegación táctil optimizada

## 🚀 Instalación y Uso

### 1. **Archivos Incluidos**
```
static/js/module_button.js    # Sistema principal
static/css/dashboard.css      # Estilos responsivos
templates/base.html           # Integración en template base
```

### 2. **Integración Automática**
El sistema se inicializa automáticamente cuando se carga la página:
```javascript
// Se ejecuta automáticamente
window.moduleButtonSystem = new ModuleButtonSystem();
```

### 3. **Personalización por Módulo**
Cada módulo puede personalizar sus configuraciones editando el objeto `moduleConfigs` en `module_button.js`.

## 🎨 Personalización

### Cambiar Colores
```javascript
// En module_button.js, línea ~50
mantenimiento: {
    color: '#3b82f6', // Cambiar color del botón
    // ...
}
```

### Agregar Acciones
```javascript
// En module_button.js, línea ~60
actions: [
    { name: 'Nueva Acción', url: '/nueva-accion/', icon: 'fas fa-icon' },
    // ...
]
```

### Modificar Validaciones
```javascript
// En module_button.js, línea ~55
validations: {
    canNewAction: true, // Nueva validación
    // ...
}
```

## 🔧 API del Sistema

### Métodos Principales
```javascript
// Detectar módulo actual
moduleButtonSystem.detectCurrentModule()

// Mostrar modal del módulo
moduleButtonSystem.showModuleModal()

// Validar acceso a acción
moduleButtonSystem.validateActionAccess(action, validations)

// Actualizar botón del módulo
moduleButtonSystem.updateModuleButton()
```

### Eventos
- **Cambio de URL**: Actualización automática del módulo
- **Navegación**: Detección de cambios en el sidebar
- **Click en botón**: Apertura del modal del módulo

## 📊 Compatibilidad

### Navegadores Soportados
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

### Dispositivos
- ✅ Desktop (1200px+)
- ✅ Laptop (992px - 1199px)
- ✅ Tablet (768px - 991px)
- ✅ Móvil (320px - 767px)

## 🛠️ Mantenimiento

### Agregar Nuevo Módulo
1. Agregar configuración en `moduleConfigs`
2. Definir validaciones específicas
3. Configurar acciones disponibles
4. Probar detección automática

### Modificar Validaciones
1. Editar objeto `validations` del módulo
2. Actualizar método `validateActionAccess`
3. Probar acceso a acciones

### Personalizar Estilos
1. Modificar CSS en `dashboard.css`
2. Ajustar media queries para responsive
3. Personalizar colores y efectos

## 🎯 Beneficios

### Para Desarrolladores
- ✅ Sistema reutilizable para todos los módulos
- ✅ Validaciones centralizadas y consistentes
- ✅ Código mantenible y escalable
- ✅ Documentación completa

### Para Usuarios
- ✅ Acceso rápido a funcionalidades del módulo
- ✅ Interfaz intuitiva y responsiva
- ✅ Validaciones claras de permisos
- ✅ Experiencia consistente entre módulos

### Para el Proyecto
- ✅ Estándar unificado para todos los módulos
- ✅ Fácil integración en módulos existentes
- ✅ Escalabilidad para futuros módulos
- ✅ Mantenimiento simplificado

## 📝 Notas de Implementación

- El sistema detecta automáticamente el módulo actual
- Las validaciones se aplican en tiempo real
- El diseño es completamente responsivo
- Compatible con el sistema de mantenimiento existente
- Fácil de personalizar y extender

---

**¡Sistema listo para usar en todos los módulos del crucero!** 🚢✨
