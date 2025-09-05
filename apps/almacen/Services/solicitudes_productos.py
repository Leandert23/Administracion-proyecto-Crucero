from typing import Dict, Any, Optional, List, Tuple
from apps.almacen.models import Producto
from .products import retirar_producto_fefo, retirar_producto_fifo

def solicitar_producto_por_id(
    producto_id: int, 
    cantidad: int, 
    modulo: str, 
    descripcion: Optional[str] = None
) -> Dict[str, Any]:
    """Retira stock de un producto utilizando el método FEFO (si hay caducidades) o FIFO.
    
    Esta función gestiona el retiro de productos del inventario aplicando el método
    FEFO (First Expired, First Out) cuando existen lotes con fechas de caducidad,
    o FIFO (First In, First Out) en caso contrario.
    
    Args:
        producto_id (int): Identificador único del producto a retirar.
        cantidad (int): Cantidad de unidades a retirar (debe ser mayor que 0).
        modulo (str): Módulo o departamento que realiza la solicitud. 
        descripcion (str, optional): Descripción adicional opcional para el movimiento.
            
    Returns:
        Dict[str, Any]: Diccionario con el resultado de la operación que incluye:
            - success (bool): Indica si la operación fue exitosa.
            - error (str, opcional): Tipo de error en caso de fallo.
            - mensaje (str, opcional): Mensaje descriptivo del resultado.
            - falta_cantidad (bool): Indica si hubo falta de stock.
            - cantidad_faltante (int): Cantidad faltante en caso de stock insuficiente.
            - producto_id (int, opcional): ID del producto procesado (éxito).
            - retirado (int, opcional): Cantidad retirada exitosamente (éxito).
            - detalle (str, opcional): Detalles técnicos del error (solo en errores internos).
            
    Raises:
        No levanta excepciones directamente, pero todas las excepciones son capturadas
        y devueltas en el formato de respuesta de error.
        
    Note:
        La función realiza validaciones de cantidad, existencia del producto y
        disponibilidad de stock antes de intentar cualquier retiro.
    """
    """Retira stock de un producto usando FEFO (si hay caducidades) o FIFO.

    Lógica:
        - FEFO si hay lotes con fecha_caducidad y cantidad > 0.
        - FIFO en caso contrario.
    Retorna un contrato simplificado.
    """
    if cantidad <= 0:
        return {
            'success': False,
            'error': 'cantidad_invalida',
            'mensaje': 'La cantidad debe ser mayor que 0',
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }

    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return {
            'success': False,
            'error': 'producto_no_encontrado',
            'mensaje': 'El producto solicitado no existe',
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }

    if producto.cantidad < cantidad:
        return {
            'success': False,
            'error': 'stock_insuficiente',
            'mensaje': f'Stock insuficiente. Disponible {producto.cantidad}, requerido {cantidad}',
            'falta_cantidad': True,
            'cantidad_faltante': cantidad - producto.cantidad
        }
    
    tiene_caducidades = producto.lotes.filter(
        cantidad_productos__gt=0,
        fecha_caducidad__isnull=False
    ).exists()
    
    metodo = 'FEFO' if tiene_caducidades else 'FIFO'

    try:
        if metodo == 'FEFO':
            retirar_producto_fefo(producto.id, cantidad, modulo, descripcion=descripcion)
        else:
            retirar_producto_fifo(producto.id, cantidad, modulo, descripcion=descripcion)
    except ValueError as error:
        return {
            'success': False,
            'error': 'operacion_invalida',
            'mensaje': str(error),
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }
    except Exception as error:
        return {
            'success': False,
            'error': 'error_interno',
            'mensaje': 'Error inesperado al retirar el producto',
            'detalle': str(error),
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }

    return {
        'success': True,
        'producto_id': producto.id,
        'retirado': cantidad
    }


def solicitar_lista_productos(
    lista_productos: List[Tuple[int, int]], 
    modulo: str = 'COMPRAS', 
    descripcion: Optional[str] = None
) -> Dict[str, Any]:
    """Procesa múltiples retiros de productos (wrapper sobre solicitar_producto).

    Args:
        lista_productos (List[Tuple[int,int]]): Lista de pares (producto_id, cantidad > 0).
        modulo (str): Módulo solicitante (se propaga a cada retiro).
        descripcion (str | None): Descripción común para todos los movimientos.

    Retorno:
        {
        'success': <bool>,          # True solo si TODOS los retiros individuales tuvieron success True
        'resultados': [             # Lista en el mismo orden de entrada
        <dict resultado solicitar_producto>, ...
        ]
        }

    Comportamiento:
        - No realiza rollback global: si un producto falla continúa con los siguientes.
        - Cada elemento de 'resultados' cumple el contrato de solicitar_producto.
    """
    resultados = []
    exito_global = True

    for producto_id, cantidad in lista_productos:
        resultado = solicitar_producto_por_id(
            producto_id, 
            cantidad, 
            modulo=modulo, 
            descripcion=descripcion
        )
        
        if not resultado.get('success'):
            exito_global = False
            
        resultados.append(resultado)

    return {
        'success': exito_global, 
        'resultados': resultados
    }

def solicitar_producto_por_nombre(
    nombre_producto: str,
    cantidad: int,
    modulo: str = 'COMPRAS',
    descripcion: Optional[str] = None
) -> Dict[str, Any]:
    """Versión de solicitar_producto que busca productos por nombre en lugar de ID.
    
    Realiza una búsqueda case-insensitive del producto por nombre. Si existen múltiples
    productos con el mismo nombre (posible cuando los nombres no son únicos globalmente
    entre diferentes cruceros), retorna un error de ambigüedad.
    
    Args:
        nombre_producto (str): Nombre del producto a buscar (búsqueda case-insensitive).
        cantidad (int): Cantidad de unidades a retirar (debe ser mayor que 0).
        modulo (str): Módulo o departamento que realiza la solicitud. 
        descripcion (str, optional): Descripción adicional opcional para el movimiento.
            
    Returns:
        Dict[str, Any]: Diccionario con el resultado de la operación con el mismo
        formato que solicitar_producto. Incluye:
            - success (bool): Indica si la operación fue exitosa.
            - error (str, opcional): Tipo de error en caso de fallo.
            - mensaje (str, opcional): Mensaje descriptivo del resultado.
            - falta_cantidad (bool): Indica si hubo falta de stock.
            - cantidad_faltante (int): Cantidad faltante en caso de stock insuficiente.
            - producto_id (int, opcional): ID del producto procesado (éxito).
            - retirado (int, opcional): Cantidad retirada exitosamente (éxito).
            - detalle (str, opcional): Detalles técnicos del error (solo en errores internos).
            
    Raises:
        No levanta excepciones directamente. Todas las excepciones son capturadas
        y devueltas en el formato de respuesta de error.
        
    Note:
        - La búsqueda es exacta pero case-insensitive (no distingue mayúsculas/minúsculas).
        - Requiere que el nombre del producto sea único para evitar ambigüedades.
        - Delega en solicitar_producto una vez encontrado el producto único.
    """
    """Versión por nombre de 'solicitar_producto'.

    Busca el producto por nombre (case-insensitive). Si hay múltiples coincidencias
    (posible si el nombre no es globalmente único entre cruceros), retorna error.

    Contrato de retorno idéntico a solicitar_producto.
    """
    if not nombre_producto or not nombre_producto.strip():
        return {
            'success': False,
            'error': 'nombre_invalido',
            'mensaje': 'El nombre del producto es requerido',
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }

    qs = Producto.objects.filter(nombre__iexact=nombre_producto.strip())
    total = qs.count()
    if total == 0:
        return {
            'success': False,
            'error': 'producto_no_encontrado',
            'mensaje': 'No existe un producto con ese nombre',
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }
    if total > 1:
        return {
            'success': False,
            'error': 'producto_ambiguo',
            'mensaje': 'Existe más de un producto con ese nombre; especifique por ID',
            'falta_cantidad': False,
            'cantidad_faltante': 0
        }

    producto = qs.first()
    return solicitar_producto_por_id(producto.id, cantidad, modulo=modulo, descripcion=descripcion)