# 🚀 SISTEMA UNIVERSAL DE GESTIÓN DE TAREAS - CRUCERO

## 📋 Descripción General

Este sistema implementa un **botón universal** que permite a cualquier módulo del crucero crear tareas directamente en el sistema de mantenimiento, funcionando como un **"almacén centralizado de tareas"** donde se pueden gestionar, asignar y completar todas las tareas del barco.

## ✨ Características Principales

### 🔧 **Botón Universal Inteligente**
- **Detección automática** del módulo actual
- **Interfaz adaptativa** según el módulo detectado
- **Contador en tiempo real** de tareas pendientes
- **Modal responsivo** para creación de tareas

### 📱 **Interfaz Moderna**
- **Botón flotante** en esquina inferior derecha
- **Animaciones suaves** y efectos visuales
- **Colores diferenciados** por módulo
- **Notificaciones visuales** de éxito/error

### 🌐 **APIs RESTful**
- **POST /api/tasks/create/** - Crear tareas desde cualquier módulo
- **GET /api/tasks/count/** - Contar tareas pendientes
- **GET /api/dashboard-update/** - Actualización del dashboard

---

## 🏗️ Arquitectura del Sistema

```
🚢 SISTEMA UNIVERSAL DE TAREAS
├── 📱 Frontend (JavaScript ES6)
│   ├── UniversalTaskButton Class
│   ├── Detección automática de módulo
│   ├── Modal de creación de tareas
│   └── Notificaciones en tiempo real
├── 🔧 Backend (Django)
│   ├── API REST para creación de tareas
│   ├── Validaciones y procesamiento
│   └── Integración con modelos existentes
├── 💾 Base de Datos
│   ├── Campos modulo_origen y origen_url
│   ├── Rastreo completo de origen
│   └── Historial de cambios
└── 🎨 UI/UX
    ├── Diseño responsivo
    ├── Animaciones y transiciones
    ├── Tema unificado
    └── Accesibilidad completa
```

---

## 🔗 Módulos Integrados

### ✅ **Módulos Preparados**
1. **🏥 Servicios Médicos** - Mantenimiento de equipos médicos
2. **📦 Almacén** - Gestión de equipos de almacén
3. **👥 Recursos Humanos** - Mantenimiento de equipos RRHH
4. **💰 Ventas** - Equipos de punto de venta
5. **📅 Reservas** - Sistemas de reservas
6. **🍽️ Restaurante** - Equipos de cocina
7. **🍸 Bares** - Equipos de bar
8. **🎵 Entretenimiento** - Equipos audiovisuales
9. **🛒 Compras** - Sistemas de compras
10. **🔧 Mantenimiento** - Sistema central

---

## 🚀 Cómo Funciona

### **1. Detección Automática del Módulo**
```javascript
// El sistema detecta automáticamente el módulo por URL
detectCurrentModule() {
    const path = window.location.pathname;

    if (path.includes('/servicios-medicos')) return 'servicios_medicos';
    if (path.includes('/almacen')) return 'almacen';
    // ... otros módulos
}
```

### **2. Creación de Tareas Directas**
```javascript
// Cualquier módulo puede crear tareas directamente
const taskData = {
    titulo: "Reparar equipo de refrigeración",
    descripcion: "El equipo presenta fallos en el sistema de enfriamiento",
    prioridad: "alta",
    tipo: "correctivo",
    ubicacion_solicitud: "Cubierta 5 - Cocina Principal",
    equipo_afectado: "Refrigerador industrial",
    tiempo_estimado: 2.5,
    modulo_origen: "restaurante",
    origen_url: window.location.href
};

fetch('/api/tasks/create/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskData)
});
```

### **3. Procesamiento en Mantenimiento**
- Las tareas aparecen automáticamente en `/tareas/`
- Se pueden asignar técnicos y gestionar el workflow
- Se registra el historial completo de cambios
- Se actualizan los inventarios cuando se consumen productos

---

## 📊 APIs Disponibles

### **POST /api/tasks/create/**
Crear una nueva tarea desde cualquier módulo.

**Parámetros:**
```json
{
    "titulo": "string (requerido)",
    "descripcion": "string (requerido)",
    "prioridad": "baja|media|alta|critica|emergencia",
    "tipo": "preventivo|correctivo|emergencia|inspeccion|limpieza|reparacion",
    "ubicacion_solicitud": "string",
    "equipo_afectado": "string",
    "tiempo_estimado": "number (horas)",
    "modulo_origen": "string",
    "origen_url": "string"
}
```

**Respuesta:**
```json
{
    "success": true,
    "task_id": 123,
    "message": "Tarea creada exitosamente",
    "task_url": "/tareas/123/"
}
```

### **GET /api/tasks/count/**
Obtener el conteo de tareas pendientes.

**Respuesta:**
```json
{
    "success": true,
    "count": 15
}
```

---

## 🎨 Interfaz de Usuario

### **Botón Universal**
- **Posición:** Esquina inferior derecha
- **Color:** Según el módulo actual
- **Tamaño:** Adaptable (220px mínimo)
- **Estados:** Normal, hover, loading

### **Modal de Creación**
- **Título dinámico** según módulo
- **Campos inteligentes** con validación en tiempo real
- **Animaciones suaves** de entrada/salida
- **Responsive** para móviles y tablets

### **Notificaciones**
- **Éxito:** Verde con checkmark
- **Error:** Rojo con X
- **Auto-cierre** después de 5 segundos
- **Animaciones** de entrada/salida

---

## 🔒 Sistema de Seguridad

### **Validaciones**
- **CSRF Protection** en todas las requests
- **Validación de datos** en backend
- **Limpieza de entrada** automática
- **Control de acceso** por usuario

### **Rastreo**
- **Módulo de origen** registrado automáticamente
- **URL de origen** para seguimiento
- **Usuario creador** identificado
- **Historial completo** de cambios

---

## 📈 Beneficios del Sistema

### **Para los Módulos**
- ✅ **Creación rápida** de tareas sin navegación
- ✅ **Interfaz familiar** adaptada al módulo
- ✅ **Seguimiento automático** del estado de tareas
- ✅ **Notificaciones** de progreso

### **Para Mantenimiento**
- ✅ **Centralización** de todas las tareas del barco
- ✅ **Priorización inteligente** por módulo y urgencia
- ✅ **Asignación eficiente** de recursos
- ✅ **Reportes unificados** de productividad

### **Para el Usuario Final**
- ✅ **Experiencia unificada** en todos los módulos
- ✅ **Acceso directo** a funcionalidades críticas
- ✅ **Transparencia** en el estado de las tareas
- ✅ **Colaboración** entre departamentos

---

## 🚀 Implementación en Nuevos Módulos

### **Paso 1: Incluir el JavaScript**
```html
<!-- En el template base de tu módulo -->
<script src="{% static 'js/cruise_maintenance_button.js' %}"></script>
```

### **Paso 2: Agregar Configuración**
```javascript
// En cruise_maintenance_button.js agregar tu módulo
tu_modulo: {
    name: 'Tu Módulo',
    icon: 'fas fa-tu-icono',
    color: '#tu-color',
    // ... configuración específica
}
```

### **Paso 3: Crear Tareas**
```javascript
// Desde cualquier parte de tu módulo
const taskButton = window.universalTaskButton;
if (taskButton) {
    taskButton.showTaskCreationModal();
}
```

---

## 📊 Estadísticas y Monitoreo

### **Métricas Disponibles**
- **Tareas por módulo** de origen
- **Tiempo de respuesta** promedio
- **Tasa de completitud** por módulo
- **Productos más consumidos** por módulo

### **Dashboard Unificado**
- **Vista general** de todas las tareas
- **Filtros por módulo** de origen
- **Gráficos de productividad**
- **Alertas de tareas** pendientes

---

## 🎯 Casos de Uso

### **Ejemplo 1: Restaurante**
```
👨‍🍳 Cocinero detecta problema en refrigerador
   ↓
🍽️ Presiona "Crear Tarea" en módulo restaurante
   ↓
📝 Llena formulario: "Refrigerador no enfría correctamente"
   ↓
🔧 Tarea aparece automáticamente en mantenimiento
   ↓
👷‍♂️ Técnico asignado repara el equipo
   ↓
✅ Tarea completada, restaurante notificado
```

### **Ejemplo 2: Servicios Médicos**
```
👩‍⚕️ Enfermera detecta equipo médico con fallos
   ↓
🏥 Presiona "Crear Tarea" en módulo médico
   ↓
📋 Especifica: "Equipo rayos X presenta errores"
   ↓
🔧 Mantenimiento recibe tarea con prioridad alta
   ↓
🛠️ Equipo técnico repara con urgencia
   ↓
✅ Equipo funcional, paciente atendido
```

---

## 🔧 Configuración Avanzada

### **Personalización de Colores**
```javascript
// Modificar colores por módulo
const moduleColors = {
    restaurante: '#f97316',
    servicios_medicos: '#ef4444',
    // ... otros
};
```

### **Configuración de Prioridades**
```javascript
// Prioridades por defecto según módulo
const moduleDefaults = {
    servicios_medicos: { prioridad: 'alta', tiempo: 4 },
    restaurante: { prioridad: 'media', tiempo: 2 },
    // ... otros
};
```

### **Campos Personalizados**
```javascript
// Campos adicionales por módulo
const customFields = {
    restaurante: ['tipo_cocina', 'horario_afectado'],
    servicios_medicos: ['tipo_equipo_medico', 'pacientes_afectados'],
    // ... otros
};
```

---

## 📚 Documentación Técnica

### **Archivos Principales**
- `static/js/cruise_maintenance_button.js` - Sistema frontend
- `mantenimiento/views/dashboard.py` - APIs backend
- `mantenimiento/models.py` - Campos de rastreo
- `mantenimiento/urls.py` - Rutas de las APIs

### **Dependencias**
- **Django 4.2+** para backend
- **JavaScript ES6+** para frontend
- **Bootstrap 5.3+** para estilos
- **Font Awesome 6.4+** para iconos

### **Compatibilidad**
- ✅ **Chrome 80+**
- ✅ **Firefox 75+**
- ✅ **Safari 13+**
- ✅ **Edge 80+**
- ✅ **Móviles modernos**

---

## 🎊 Conclusión

Este **Sistema Universal de Gestión de Tareas** transforma el mantenimiento del crucero en un **sistema colaborativo y eficiente** donde:

- **Todos los módulos** pueden crear tareas instantáneamente
- **Mantenimiento actúa** como centro de control unificado
- **Los usuarios** tienen visibilidad completa del proceso
- **La productividad** aumenta significativamente
- **La colaboración** entre departamentos mejora

**¡El mantenimiento ya no es un departamento aislado, sino el corazón que mantiene latiendo a todo el crucero!** 🚢💙</contents>
</xai:function_call">SISTEMA_UNIVERSAL_TAREAS.md
