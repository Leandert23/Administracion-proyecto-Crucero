"""Vistas organizadas por dominio.

Este paquete expone las vistas públicas que `urls.py` necesita. Internamente,
cada área se implementa en su propio módulo para mantener el orden y evitar
archivos gigantes.
"""

# Tareas
from .tareas import (
    tarea_list,
    tarea_create,
    tarea_detail,
    tarea_update,
    tarea_delete,
    tarea_asignar_personal,
    tarea_registrar_producto,
    tarea_cambiar_estado,
    tarea_crear_preventiva,
    tarea_crear_correctiva,
    tarea_workflow,
)

# Dashboard
from .dashboard import dashboard

# Ubicaciones
from .ubicaciones import (
    ubicacion_list,
    ubicacion_create,
    ubicacion_detail,
    ubicacion_update,
    ubicacion_delete,
)

# Productos e inventario
from .productos import (
    producto_list,
    producto_create,
    producto_detail,
    producto_update,
    producto_delete,
)
from .inventario import (
    inventario_list,
    inventario_update,
    stock_bajo,
)

# Equipos
from .equipos import (
    equipo_list,
    equipo_create,
    equipo_detail,
    equipo_update,
    equipo_delete,
)

# Incidentes y reportes
from .incidentes import (
    incidente_list,
    incidente_create,
    incidente_detail,
    incidente_update,
    incidente_resolver,
)
from .reportes import (
    reportes,
    reporte_tareas_pendientes,
    reporte_equipos_vencidos,
    reporte_consumo_productos,
)

# Piscinas
from .piscinas import (
    piscina_list,
    piscina_create,
    piscina_update,
    piscina_detail,
    medicion_piscina_create,
    piscina_trends,
)


