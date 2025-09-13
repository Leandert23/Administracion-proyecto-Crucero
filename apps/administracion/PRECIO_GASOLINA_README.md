# Configuración de Precio de Gasolina por Crucero

## Descripción
El sistema permite configurar el precio de gasolina de forma dinámica para cada crucero individualmente. Solo los usuarios administradores pueden modificar estos valores.

## Características

### 1. Precio Dinámico por Crucero
- Cada crucero puede tener su propio precio de gasolina
- El precio se utiliza para calcular el presupuesto estimado
- Se muestra en el dashboard del crucero

### 2. Interfaz de Administración
- Solo usuarios con permisos de administrador pueden configurar precios
- Interfaz organizada en secciones para mejor usabilidad
- Validación de valores (no pueden ser negativos)

### 3. Visualización en Dashboard
- Muestra el precio actual configurado
- Indica claramente cuando no está configurado
- Botón directo para configurar (solo para administradores)

## Cómo Configurar el Precio

### Opción 1: Panel de Administración de Django
1. Acceder a `/admin/administracion/dashboard/`
2. Seleccionar el crucero a configurar
3. Modificar el campo "Precio de combustible"
4. Guardar los cambios

### Opción 2: Comando de Gestión
```bash
# Configurar precio para todos los cruceros
python manage.py configurar_precio_gasolina --precio 15.50

# Configurar precio para un crucero específico
python manage.py configurar_precio_gasolina --precio 12.75 --crucero-id 1

# Solo configurar cruceros sin precio (precio = 0)
python manage.py configurar_precio_gasolina --precio 18.00 --solo-sin-configurar
```

### Opción 3: Desde el Dashboard
1. Ir al dashboard del crucero
2. Hacer clic en "Configurar Precio" (solo para administradores)
3. Modificar el valor en el panel de administración
4. Guardar

## Validaciones
- El precio debe ser mayor a 0
- No se permiten valores negativos
- Se valida automáticamente al guardar

## Cálculo del Presupuesto
El precio de gasolina se utiliza en la fórmula:
```
costo_combustible = distancia × precio_combustible × consumo_combustible × días
```

## Estados del Precio
- **Configurado**: Se muestra en verde con el valor
- **No configurado**: Se muestra en rojo como "No configurado"
- **Valor 0**: Se considera como no configurado

## Archivos Modificados
- `models.py`: Campo `precio_combustible` en modelo Dashboard
- `views.py`: Lógica para obtener precio dinámico
- `admin.py`: Interfaz de administración mejorada
- `dashboard_crucero.html`: Visualización mejorada del precio
- `management/commands/configurar_precio_gasolina.py`: Comando de gestión
