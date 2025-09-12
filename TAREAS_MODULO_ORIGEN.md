# 📋 SISTEMA DE RASTREO DE MÓDULO DE ORIGEN EN TAREAS

## 📋 Descripción

He implementado un sistema completo para **rastrear y mostrar de qué módulo proviene cada tarea** en el sistema de mantenimiento. Ahora puedes ver claramente si una tarea fue creada desde Ventas, Restaurante, Servicios Médicos, o cualquier otro módulo.

## ✨ **NUEVAS FUNCIONALIDADES**

### **1. 🏷️ Columna "Módulo Origen" en la Lista de Tareas**
- **Nueva columna** que muestra el módulo de origen de cada tarea
- **Badges diferenciados** por color según el tipo de módulo
- **Iconos específicos** para identificar visualmente el origen

### **2. 🔍 Filtro por Módulo de Origen**
- **Dropdown de filtro** para mostrar tareas de módulos específicos
- **Nombres amigables** de los módulos (ej: "Servicios Médicos" en lugar de "servicios_medicos")
- **Integración completa** con el sistema de filtros existente

### **3. 📊 Filtro "Solo Tareas Externas"**
- **Checkbox especial** para mostrar únicamente tareas de módulos externos
- **Excluye automáticamente** tareas creadas desde el módulo de mantenimiento
- **Útil para ver** solo las solicitudes que vienen de otros departamentos

## 🎨 **DISEÑO VISUAL**

### **Badges por Tipo de Módulo:**

#### **🔧 Tareas de Mantenimiento:**
```html
<span class="badge bg-light text-dark">
    <i class="fas fa-tools me-1"></i>
    Mantenimiento
</span>
```

#### **🌐 Tareas de Módulos Externos:**
```html
<span class="badge bg-info">
    <i class="fas fa-external-link-alt me-1"></i>
    Servicios Médicos
</span>
```

### **Colores y Significado:**
- **Gris claro** (`bg-light text-dark`) - Tareas creadas en mantenimiento
- **Azul** (`bg-info`) - Tareas creadas en módulos externos
- **Icono de herramientas** - Módulo de mantenimiento
- **Icono de enlace externo** - Módulos externos

## 🔧 **FUNCIONALIDADES IMPLEMENTADAS**

### **1. Vista de Tareas Actualizada (`tarea_list`)**

#### **Filtros Agregados:**
```python
# Filtro por módulo de origen específico
modulo_origen = request.GET.get('modulo_origen')

# Filtro para mostrar solo tareas externas
solo_externas = request.GET.get('solo_externas') == '1'
if solo_externas:
    tareas = tareas.exclude(modulo_origen__in=['', 'mantenimiento']).exclude(modulo_origen__isnull=True)
```

#### **Contexto Enriquecido:**
```python
# Módulos de origen únicos para el filtro
modulos_origen = TareaMantenimiento.objects.exclude(
    modulo_origen__isnull=True
).exclude(
    modulo_origen=''
).values_list('modulo_origen', flat=True).distinct().order_by('modulo_origen')

# Mapeo de nombres amigables
MODULOS_DISPLAY = {
    'servicios_medicos': 'Servicios Médicos',
    'almacen': 'Almacén',
    'recursos_humanos': 'Recursos Humanos',
    'ventas': 'Ventas',
    'reservas': 'Reservas',
    'restaurante': 'Restaurante',
    'bares': 'Bares',
    'entretenimiento': 'Entretenimiento',
    'compras': 'Compras',
    'mantenimiento': 'Mantenimiento',
}
```

### **2. Template Actualizado (`tarea_list.html`)**

#### **Nueva Columna en la Tabla:**
```html
<th class="border-0 fw-semibold">
    <i class="fas fa-building me-2 text-secondary"></i>Módulo Origen
</th>
```

#### **Filtro por Módulo:**
```html
<div class="col-md-3">
    <label for="modulo_origen" class="form-label fw-semibold">
        <i class="fas fa-building me-1 text-info"></i>Módulo de Origen
    </label>
    <select name="modulo_origen" class="form-select">
        <option value="">Todos los módulos</option>
        {% for modulo in modulos_origen %}
        <option value="{{ modulo }}">{{ modulos_display|default:modulo|title }}</option>
        {% endfor %}
    </select>
</div>
```

#### **Checkbox para Tareas Externas:**
```html
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="solo_externas" value="1" id="toggleExternas">
    <label class="form-check-label fw-semibold" for="toggleExternas">
        <i class="fas fa-external-link-alt me-1 text-info"></i>Solo tareas de módulos externos
    </label>
</div>
```

## 📊 **CASOS DE USO**

### **Caso 1: Ver Todas las Tareas de Ventas**
```
1. Ir a la lista de tareas
2. Seleccionar "Ventas" en el filtro "Módulo de Origen"
3. Aplicar filtro
4. Ver solo tareas creadas desde el módulo de Ventas
```

### **Caso 2: Ver Solo Solicitudes Externas**
```
1. Ir a la lista de tareas
2. Marcar checkbox "Solo tareas de módulos externos"
3. Ver únicamente tareas que vienen de otros departamentos
4. Excluye tareas creadas internamente en mantenimiento
```

### **Caso 3: Filtrar por Módulo Específico**
```
1. Usar el dropdown "Módulo de Origen"
2. Seleccionar módulo específico (ej: "Servicios Médicos")
3. Combinar con otros filtros (estado, prioridad, etc.)
4. Ver tareas específicas de ese módulo
```

## 🎯 **BENEFICIOS DEL SISTEMA**

### **✅ Para el Personal de Mantenimiento:**
- **Visibilidad completa** del origen de cada tarea
- **Priorización inteligente** basada en el módulo solicitante
- **Seguimiento de responsabilidad** por departamento
- **Mejor organización** del trabajo

### **✅ Para la Gestión:**
- **Métricas por módulo** de solicitudes de mantenimiento
- **Identificación de módulos** con más necesidades
- **Análisis de patrones** de solicitudes
- **Reportes detallados** por departamento

### **✅ Para los Módulos Externos:**
- **Transparencia** en el proceso de solicitudes
- **Seguimiento** del estado de sus solicitudes
- **Confianza** en que sus solicitudes son rastreadas
- **Mejor comunicación** con mantenimiento

## 🔍 **EJEMPLOS DE USO**

### **Ejemplo 1: Tarea de Restaurante**
```
Título: "Reparar refrigerador industrial"
Módulo Origen: [Badge azul] 🏢 Restaurante
Prioridad: Alta
Estado: En Progreso
```

### **Ejemplo 2: Tarea de Servicios Médicos**
```
Título: "Mantenimiento equipo rayos X"
Módulo Origen: [Badge azul] 🏥 Servicios Médicos
Prioridad: Crítica
Estado: Asignada
```

### **Ejemplo 3: Tarea Interna de Mantenimiento**
```
Título: "Inspección preventiva motores"
Módulo Origen: [Badge gris] 🔧 Mantenimiento
Prioridad: Media
Estado: Completada
```

## 🛠️ **ARCHIVOS MODIFICADOS**

### **Backend:**
- `mantenimiento/views/tareas.py` - Lógica de filtros y contexto

### **Frontend:**
- `templates/mantenimiento/tarea_list.html` - Interfaz actualizada

### **Base de Datos:**
- Campos `modulo_origen` y `origen_url` ya existentes en el modelo

## 🎊 **RESULTADO FINAL**

### **✅ Información Completa:**
- **Cada tarea muestra** claramente su módulo de origen
- **Filtros avanzados** para organizar por módulo
- **Visualización clara** con badges y colores

### **✅ Gestión Mejorada:**
- **Priorización** basada en el módulo solicitante
- **Seguimiento** de responsabilidades por departamento
- **Métricas** de solicitudes por módulo

### **✅ Transparencia Total:**
- **Los módulos externos** pueden ver que sus solicitudes son rastreadas
- **El personal de mantenimiento** sabe exactamente de dónde viene cada tarea
- **La gestión** tiene visibilidad completa del flujo de trabajo

**¡Ahora puedes ver claramente de qué módulo proviene cada tarea y filtrar por módulo de origen para una mejor organización del trabajo de mantenimiento!** 🚀✨
