from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal

@require_GET
def productos_bar_api(request):
  from apps.bares_snacks.models import Menu, ProductoBar
  data = []
  # Productos gestionados (ProductoBar)
  for p in ProductoBar.objects.all():
    data.append({
      'id': p.id,
      'nombre': p.nombre,
      'categoria': p.categoria,
      'tipo': p.plan,  # 'gratis' o 'pago'
      'precio': float(p.precio_vta or 0),
      'ingredientes': [],  # se llenará cuando se implemente receta estructurada
      'tipo_categoria': p.tipo_almacen,
      'subtipo_categoria': p.subtipo_almacen,
      'origen': 'producto_bar'
    })
  # Productos de menú (existentes)
  productos_menu = Menu.objects.all()
  for menu in productos_menu:
    data.append({
      'id': menu.id,
      'nombre': menu.nombre,
      'categoria': menu.categoria.nombre if menu.categoria else '',
      'tipo': 'pago' if menu.precio_vta > 0 else 'gratis',
      'precio': float(menu.precio_vta),
      'ingredientes': [],
      'origen': 'menu'
    })
  return JsonResponse(data, safe=False)


@require_GET
def bares_list_api(request):
  # Lista instalaciones de tipo "Bares y Cafés" como opciones de punto de venta
  from apps.cruceros.models import Instalacion
  from apps.bares_snacks.models import Bar
  instalaciones = Instalacion.objects.filter(tipo='bares_cafes').select_related('crucero')
  data = []
  for inst in instalaciones:
    bar = Bar.objects.filter(ubicacion_id=inst.id).only('id').first()
    data.append({
      'id': inst.id,  # este es el ID de Instalacion
      'nombre': inst.nombre,
      'crucero': inst.crucero.nombre if getattr(inst, 'crucero', None) else '',
      'bar_id': bar.id if bar else None,
    })
  return JsonResponse(data, safe=False)


@require_GET
def puntos_venta_bares_api(request):
  # Trae los puntos de venta a partir de Instalaciones tipo "bares_cafes".
  # Si falta el Bar para una instalación, lo crea para asegurar FK válida.
  from apps.bares_snacks.models import Bar
  from apps.cruceros.models import Instalacion
  from datetime import timedelta

  ahora = timezone.now()
  instalaciones = Instalacion.objects.filter(tipo='bares_cafes').select_related('crucero')
  data = []
  for inst in instalaciones:
    bar, _ = Bar.objects.get_or_create(
      ubicacion=inst,
      defaults={
        'nombre': inst.nombre,
        'hora_aper': ahora,
        'hora_cierre': ahora + timedelta(hours=8),  # cumple la restricción hcierre>haper
      }
    )
    data.append({
      'id': bar.id,
      'nombre': bar.nombre,
      'instalacion_id': inst.id,
      'instalacion_codigo': getattr(inst, 'codigo_ubicacion', ''),
      'instalacion_nombre': str(inst),
      'crucero': getattr(getattr(inst, 'crucero', None), 'nombre', ''),
    })
  return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def eliminar_producto_bar_api(request):
  from apps.bares_snacks.models import Menu, ProductoBar
  import json
  data = json.loads(request.body or '{}')
  producto_id = data.get('id')
  origen = data.get('origen')  # 'producto_bar' | 'menu' | None
  if not producto_id:
    return JsonResponse({'success': False, 'error': 'ID requerido'}, status=400)
  # Estrategia: si se especifica origen, intentar sólo ese; si no, probar ProductoBar y luego Menu
  if origen == 'producto_bar':
    try:
      ProductoBar.objects.get(id=producto_id).delete()
      return JsonResponse({'success': True, 'deleted_origin': 'producto_bar'})
    except ProductoBar.DoesNotExist:
      return JsonResponse({'success': False, 'error': 'ProductoBar no encontrado'}, status=404)
  if origen == 'menu':
    try:
      Menu.objects.get(id=producto_id).delete()
      return JsonResponse({'success': True, 'deleted_origin': 'menu'})
    except Menu.DoesNotExist:
      return JsonResponse({'success': False, 'error': 'Menu no encontrado'}, status=404)
  # Sin origen: intentar ambos
  try:
    ProductoBar.objects.get(id=producto_id).delete()
    return JsonResponse({'success': True, 'deleted_origin': 'producto_bar'})
  except ProductoBar.DoesNotExist:
    pass
  try:
    Menu.objects.get(id=producto_id).delete()
    return JsonResponse({'success': True, 'deleted_origin': 'menu'})
  except Menu.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)


@csrf_exempt
@require_POST
def actualizar_producto_bar_api(request):
  # Espera JSON con { id, nombre?, plan?, precio?, categoria?, tipo_categoria?, subtipo_categoria?, receta? }
  import json
  from apps.bares_snacks.models import ProductoBar
  try:
    data = json.loads(request.body or '{}')
  except json.JSONDecodeError:
    return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

  pid = data.get('id')
  if not pid:
    return JsonResponse({'success': False, 'error': 'id requerido'}, status=400)

  try:
    p = ProductoBar.objects.get(id=pid)
  except ProductoBar.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'ProductoBar no encontrado'}, status=404)

  nombre = data.get('nombre')
  if nombre is not None:
    p.nombre = nombre.strip()

  plan = data.get('tipo') or data.get('plan')
  if plan in ('gratis', 'pago'):
    p.plan = plan

  # precio puede venir como string/numero
  if 'precio' in data or 'precio_vta' in data:
    raw = data.get('precio', data.get('precio_vta'))
    try:
      p.precio_vta = Decimal(str(raw or 0))
    except Exception:
      return JsonResponse({'success': False, 'error': 'precio inválido'}, status=400)

  categoria = data.get('categoria') or data.get('categoria_filtro')
  if categoria is not None:
    p.categoria = categoria

  tipo_cat = data.get('tipo_categoria')
  if tipo_cat is not None:
    p.tipo_almacen = tipo_cat

  subtipo_cat = data.get('subtipo_categoria')
  if subtipo_cat is not None:
    p.subtipo_almacen = subtipo_cat

  receta = data.get('receta')
  if receta is not None:
    p.receta = receta

  p.save()
  return JsonResponse({
    'success': True,
    'producto': {
      'id': p.id,
      'nombre': p.nombre,
      'tipo': p.plan,
      'precio': float(p.precio_vta or 0),
      'categoria': p.categoria,
      'tipo_categoria': p.tipo_almacen,
      'subtipo_categoria': p.subtipo_almacen,
      'receta': p.receta,
    }
  })
from django.views.decorators.http import require_GET
@require_GET
def productos_almacen_filtrados_api(request):
  from apps.almacen.models import Producto
  tipo = request.GET.get('tipo')
  subtipo = request.GET.get('subtipo')
  productos = Producto.objects.filter(tipo=tipo)
  if subtipo:
    productos = productos.filter(subtipo=subtipo)
  data = [
    {
      'id': p.id,
      'nombre': p.nombre,
      'tipo': p.tipo,
      'subtipo': p.subtipo,
      'cantidad': p.cantidad,
      'medida': p.medida
    }
    for p in productos
  ]
  return JsonResponse(data, safe=False)
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def crear_producto_bar_api(request):
  if request.method != 'POST':
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
  data = json.loads(request.body)
  nombre = (data.get('nombre') or '').strip()
  tipo_categoria = (data.get('tipo_categoria') or '').strip()
  subtipo_categoria = (data.get('subtipo_categoria') or '').strip()
  tipo_plan = data.get('tipo')  # 'pago' o 'gratis'
  precio = data.get('precio', 0) or 0
  ingredientes_ids = data.get('ingredientes', [])
  if not nombre or not tipo_categoria or not subtipo_categoria:
    return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios'}, status=400)
  from apps.almacen.models import Producto
  from apps.bares_snacks.models import ProductoBar
  ingredientes = Producto.objects.filter(id__in=ingredientes_ids)
  sin_stock = [i for i in ingredientes if i.cantidad <= 0]
  # Crear registro ProductoBar
  producto = ProductoBar.objects.create(
    nombre=nombre,
    categoria=data.get('categoria_filtro') or data.get('categoria') or '',
    tipo_almacen=tipo_categoria,
    subtipo_almacen=subtipo_categoria,
    plan= 'pago' if tipo_plan=='pago' else 'gratis',
    precio_vta= precio if precio else 0,
    receta=''  # pendiente de implementar
  )
  return JsonResponse({
    'success': True,
    'producto': {
      'id': producto.id,
      'nombre': producto.nombre,
      'categoria': producto.categoria,
      'tipo': producto.plan,
      'precio': float(producto.precio_vta),
      'tipo_categoria': producto.tipo_almacen,
      'subtipo_categoria': producto.subtipo_almacen,
      'receta': producto.receta
    },
    'sin_stock': [i.nombre for i in sin_stock]
  })
from django.views.decorators.http import require_GET

@require_GET
def categorias_almacen_api(request):
  from apps.almacen.models import Producto
  tipos = Producto.TIPOS_PRODUCTO
  subtipos = Producto.SUBTIPOS_PRODUCTO
  # Agrupar subtipos por tipo
  subtipos_por_tipo = {}
  for tipo_id, tipo_nombre in tipos:
    subtipos_por_tipo[tipo_id] = []
  for sub_id, sub_nombre in subtipos:
    # Buscar a qué tipo pertenece el subtipo
    for tipo_id, subtipo_set in Producto.SUBTIPOS_POR_TIPO.items():
      if sub_id in subtipo_set:
        subtipos_por_tipo[tipo_id].append({'id': sub_id, 'nombre': sub_nombre})
        break
  data = [
    {
      'id': tipo_id,
      'nombre': tipo_nombre,
      'subtipos': subtipos_por_tipo[tipo_id]
    }
    for tipo_id, tipo_nombre in tipos
  ]
  return JsonResponse(data, safe=False)
from django.views.decorators.http import require_http_methods

@require_GET
def receta_producto_bar_api(request, producto_id: int):
  from apps.bares_snacks.models import ProductoBar, IngredienteReceta
  try:
    p = ProductoBar.objects.get(id=producto_id)
  except ProductoBar.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'ProductoBar no encontrado'}, status=404)
  items = [
    {
      'id': it.id,
      'ingrediente_id': it.ingrediente_id,
      'ingrediente_nombre': getattr(it.ingrediente, 'nombre', ''),
      'cantidad': float(it.cantidad),
      'unidad': it.unidad,
    }
    for it in p.receta_items.select_related('ingrediente').all()
  ]
  return JsonResponse({'success': True, 'producto_id': p.id, 'items': items})


@csrf_exempt
@require_http_methods(["POST"])
def guardar_receta_producto_bar_api(request, producto_id: int):
  import json
  from apps.bares_snacks.models import ProductoBar, IngredienteReceta
  from apps.almacen.models import Producto as ProdAlmacen
  try:
    p = ProductoBar.objects.get(id=producto_id)
  except ProductoBar.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'ProductoBar no encontrado'}, status=404)
  try:
    payload = json.loads(request.body or '{}')
  except json.JSONDecodeError:
    return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
  items = payload.get('items') or []
  # Reemplazar receta completa: simple y claro
  p.receta_items.all().delete()
  creados = []
  for it in items:
    ing_id = it.get('ingrediente_id') or it.get('id')
    if not ing_id:
      continue
    try:
      ing = ProdAlmacen.objects.get(id=ing_id)
    except ProdAlmacen.DoesNotExist:
      continue
    cant = Decimal(str(it.get('cantidad') or 1))
    unidad = str(it.get('unidad') or '')
    obj = IngredienteReceta.objects.create(producto_bar=p, ingrediente=ing, cantidad=cant, unidad=unidad)
    creados.append({
      'id': obj.id,
      'ingrediente_id': obj.ingrediente_id,
      'ingrediente_nombre': ing.nombre,
      'cantidad': float(obj.cantidad),
      'unidad': obj.unidad
    })
  return JsonResponse({'success': True, 'producto_id': p.id, 'items': creados})
from apps.bares_snacks.models import Menu

def productos_disponibles_api(request):
  productos = []
  for menu in Menu.objects.all():
    productos.append({
      'id': menu.id,
      'nombre': menu.nombre,
      'categoria': menu.categoria.nombre if menu.categoria else '',
      'tipo': 'pago' if menu.precio_vta > 0 else 'gratis',
      'precio': float(menu.precio_vta),
      'ingredientes': [],
      'cantidad_posible': 0
    })
  return JsonResponse(productos, safe=False)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def ingredientes_almacen_api(request):
  from apps.almacen.models import Producto
  ingredientes = Producto.objects.all()
  data = [
    {
      'id': ingrediente.id,
      'nombre': ingrediente.nombre,
      'tipo': ingrediente.tipo,
      'cantidad': ingrediente.cantidad
    } for ingrediente in ingredientes
  ]
  return JsonResponse(data, safe=False)
from django.shortcuts import render
from django.shortcuts import HttpResponse

from apps.bares_snacks.models import Pedidos, DetallePedido
from apps.almacen.models import Producto
from apps.cruceros.models import Crucero

def get_ingredientes_almacen():
  # Devuelve todos los productos de almacen como ingredientes
  return Producto.objects.all()
#from apps.recursos_humanos.models import Personal
from django.db.models import Sum, Q


def bares_view(request, crucero_id):
  crucero = Crucero.objects.get(id=crucero_id)
  # Ingresos totales: suma de todos los pedidos completados
  detalles_completados = DetallePedido.objects.select_related('producto').filter(pedido__estado='completado')
  ingresos_totales = 0
  ingresos_reales = 0
  for d in detalles_completados:
    precio = (d.producto.precio_vta if d.producto else 0) or 0
    subtotal = d.cantidad * precio
    ingresos_totales += subtotal
    # criterio premium: plan = 'pago'
    if d.producto and d.producto.plan == 'pago':
      ingresos_reales += subtotal

  # Stock de productos
  productos = Producto.objects.all()
  productos_stock = [
    {
      'nombre': p.nombre,
      'cantidad': p.cantidad,
      'estado': p.estado
    } for p in productos
  ]
  bajo_stock = [p for p in productos_stock if p['estado'] in ['CRITICO', 'BAJO', 'NO HAY STOCK']]


  ingredientes_almacen = get_ingredientes_almacen()

  context = {
    'crucero': crucero,
    'ingresos_totales': ingresos_totales,
    'ingresos_reales': ingresos_reales,
    'productos_stock': productos_stock,
    'bajo_stock': bajo_stock,
    'ingredientes_almacen': ingredientes_almacen,
  }
  return render(request, 'bares_snacks/bares.html', context)


@require_GET
def habitaciones_list_api(request):
  """Devuelve habitaciones desde cruceros.Habitacion.
  Opcional: filtrar por ?crucero_id=.
  Formato: { id, codigo: codigo_ubicacion, lado, lado_code: EST|BAB, label }
  """
  from apps.cruceros.models import Habitacion
  try:
    crucero_id = int(request.GET.get('crucero_id')) if request.GET.get('crucero_id') else None
  except ValueError:
    crucero_id = None
  qs = Habitacion.objects.all()
  if crucero_id:
    qs = qs.filter(crucero_id=crucero_id)
  data = []
  for h in qs.select_related('crucero', 'tipo_habitacion'):
    lado_code = 'BAB' if h.lado == 'babor' else 'EST'
    codigo = h.codigo_ubicacion or ''
    label = f"HAB: {codigo} {lado_code}"
    data.append({
      'id': h.id,
      'codigo': codigo,
      'lado': h.lado,
      'lado_code': lado_code,
      'label': label,
      'numero': h.numero,
      'crucero': getattr(h.crucero, 'nombre', ''),
    })
  return JsonResponse(data, safe=False)


# ===================== NUEVO: Crear Pedido con Detalles ===================== #
@csrf_exempt
@require_POST
def crear_pedido_api(request):
  import json
  try:
    try:
      payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
      return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    # Campos básicos
    cliente_id = payload.get('cliente_id')
    tipo_consumo = payload.get('tipo_consumo')  # 'bar' | 'camarote'
    lugarentrega_id = payload.get('lugarentrega_id')  # requerido si bar
    nota = (payload.get('nota') or '').strip()
    productos = payload.get('productos') or []  # [{producto_id, cantidad}]

    if not productos:
      return JsonResponse({'success': False, 'error': 'Debe incluir al menos un producto'}, status=400)

    from apps.bares_snacks.models import ProductoBar
    from apps.ventas.models import Cliente
    #from apps.recursos_humanos.models import Personal
    from apps.cruceros.models import Instalacion

    # Verificar existencia entidades si se enviaron
    cliente = None
    if cliente_id:
      try:
        cliente = Cliente.objects.get(id=cliente_id)
      except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entidad no encontrada: Cliente'}, status=404)

    instalacion = None
    if tipo_consumo == 'bar':
      if not lugarentrega_id:
        return JsonResponse({'success': False, 'error': 'lugarentrega_id es requerido para consumo en bar'}, status=400)
      try:
        instalacion = Instalacion.objects.get(id=lugarentrega_id)
      except Instalacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Instalación no encontrada'}, status=404)

    # Crear pedido
    try:
      pedido = Pedidos.objects.create(
        cliente=cliente,
        lugarentrega=instalacion,
        estado='pendiente'
      )
    except IntegrityError as ie:
      diag = {
        'cliente_id': getattr(cliente, 'id', None),
        'lugarentrega_id': getattr(instalacion, 'id', None),
      }
      try:
        from apps.ventas.models import Cliente as CliM
        diag['cliente_exists'] = bool(CliM.objects.filter(id=diag['cliente_id']).exists()) if diag['cliente_id'] else False
      except Exception:
        diag['cliente_exists'] = 'unknown'
      try:
        from apps.cruceros.models import Instalacion as InstM
        diag['lugarentrega_exists'] = bool(InstM.objects.filter(id=diag['lugarentrega_id']).exists()) if diag['lugarentrega_id'] else True
      except Exception:
        diag['lugarentrega_exists'] = 'unknown'
      return JsonResponse({'success': False, 'error': f'FK error al crear pedido: {ie}', 'diagnostico': diag}, status=400)

    # Crear detalles
    detalles_resp = []
    from decimal import Decimal
    for item in productos:
      pid = item.get('producto_id') or item.get('id')
      cantidad = int(item.get('cantidad') or 0)
      if not pid or cantidad <= 0:
        continue
      try:
        prod = ProductoBar.objects.get(id=pid)
      except ProductoBar.DoesNotExist:
        continue
      try:
        detalle = DetallePedido.objects.create(
          pedido=pedido,
          producto=prod,
          cantidad=cantidad,
        )
      except IntegrityError as ie:
        diag = {
          'pedido_id': getattr(pedido, 'id', None),
          'producto_id': getattr(prod, 'id', None),
          'producto_exists': True,
        }
        return JsonResponse({'success': False, 'error': f'FK error al crear detalle: {ie}', 'diagnostico': diag}, status=400)
      precio_actual = float(prod.precio_vta or 0)
      detalles_resp.append({
        'id': detalle.id,
        'producto_id': prod.id,
        'nombre': prod.nombre,
        'cantidad': detalle.cantidad,
        'precio': precio_actual,
        'subtotal': float(detalle.cantidad * (prod.precio_vta or 0))
      })

    total = sum(d['subtotal'] for d in detalles_resp)
    fecha_hora = timezone.localtime(pedido.fecha_hora)
    return JsonResponse({
      'success': True,
      'pedido': {
        'id': pedido.id,
        'estado': pedido.estado,
  'cliente_id': cliente.id if cliente else None,
        'lugarentrega_id': instalacion.id if instalacion else None,
        'lugarentrega_nombre': str(instalacion) if instalacion else None,
        'tipo_consumo': tipo_consumo,
        'productos': detalles_resp,
        'total': total,
        'nota': nota,
        'fecha_hora': fecha_hora.isoformat(),
        'fecha': fecha_hora.date().isoformat(),
        'hora': fecha_hora.strftime('%H:%M')
      }
    })
  except Exception as e:
    # Asegurar respuesta JSON aún ante errores no controlados (evita HTML 500)
    return JsonResponse({'success': False, 'error': f'Error interno: {e}'}, status=500)


@csrf_exempt
@require_POST
def eliminar_pedido_api(request, pedido_id: int):
  """Elimina un pedido existente y sus detalles. Solo permite si está en estado 'pendiente'."""
  try:
    p = Pedidos.objects.get(id=pedido_id)
  except Pedidos.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)
  if p.estado != 'pendiente':
    return JsonResponse({'success': False, 'error': 'Solo se pueden eliminar pedidos en estado pendiente'}, status=400)
  p.delete()
  return JsonResponse({'success': True, 'deleted_id': pedido_id})


def _serialize_pedido(p):
  detalles_resp = []
  total = 0.0
  for d in p.detalles.select_related('producto').all():
    precio = float((getattr(d.producto, 'precio_vta', 0) or 0)) if d.producto else 0.0
    subtotal = float(d.cantidad * (getattr(d.producto, 'precio_vta', 0) or 0)) if d.producto else 0.0
    detalles_resp.append({
      'id': d.id,
      'producto_id': getattr(d.producto, 'id', None),
      'nombre': getattr(d.producto, 'nombre', ''),
      'cantidad': d.cantidad,
      'precio': precio,
      'subtotal': subtotal,
    })
    total += subtotal
  fecha_hora = timezone.localtime(p.fecha_hora)
  return {
    'id': p.id,
    'estado': p.estado,
    'cliente_id': p.cliente_id,
    'lugarentrega_id': p.lugarentrega_id,
    'lugarentrega_nombre': str(p.lugarentrega) if p.lugarentrega_id else None,
    'tipo_consumo': 'bar' if p.lugarentrega_id else 'camarote',
    'productos': detalles_resp,
    'total': total,
    'nota': None,
    'fecha_hora': fecha_hora.isoformat(),
    'fecha': fecha_hora.date().isoformat(),
    'hora': fecha_hora.strftime('%H:%M'),
  }


@require_GET
def pedidos_list_api(request):
  """Lista pedidos. scope=activos|historial; activos = no completados, historial = completados."""
  scope = (request.GET.get('scope') or 'activos').lower()
  qs = Pedidos.objects.all().order_by('-fecha_hora')
  if scope == 'historial':
    qs = qs.filter(estado='completado')
  else:
    qs = qs.exclude(estado='completado')
  limit = None
  try:
    limit = int(request.GET.get('limit')) if request.GET.get('limit') else None
  except ValueError:
    limit = None
  if limit:
    qs = qs[:limit]
  data = [_serialize_pedido(p) for p in qs.prefetch_related('detalles__producto')]
  return JsonResponse({'success': True, 'items': data})


@csrf_exempt
@require_POST
def actualizar_estado_pedido_api(request, pedido_id: int):
  """Actualiza el estado de un pedido respetando transiciones simples."""
  import json
  try:
    payload = json.loads(request.body or '{}')
  except json.JSONDecodeError:
    return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
  nuevo = payload.get('estado')
  if nuevo not in ('pendiente', 'en_proceso', 'completado'):
    return JsonResponse({'success': False, 'error': 'Estado inválido'}, status=400)
  try:
    p = Pedidos.objects.get(id=pedido_id)
  except Pedidos.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)
  actual = p.estado
  # Reglas de transición: pendiente -> en_proceso -> completado
  valido = (
    (actual == 'pendiente' and nuevo in ('pendiente', 'en_proceso')) or
    (actual == 'en_proceso' and nuevo in ('en_proceso', 'completado')) or
    (actual == 'completado' and nuevo == 'completado')
  )
  if not valido:
    return JsonResponse({'success': False, 'error': f'Transición no permitida: {actual} → {nuevo}'}, status=400)
  p.estado = nuevo
  p.save(update_fields=['estado'])
  return JsonResponse({'success': True, 'pedido': _serialize_pedido(p)})


@require_POST
@csrf_exempt
def disponibilidad_productos_api(request):
  """
  Calcula la cantidad disponible por producto bar seleccionado a partir de su receta y el stock actual en almacén.
  Entrada JSON: { productos: [{producto_id, cantidad?}] }
  Salida: { success: true, items: [{ producto_id, nombre, disponible, detalle: [{ingrediente_id,nombre,stock,cant_necesaria,unidad}...] }] }
  """
  import json
  from apps.bares_snacks.models import ProductoBar, IngredienteReceta
  from apps.almacen.models import Producto as ProdAlmacen
  try:
    payload = json.loads(request.body or '{}')
  except json.JSONDecodeError:
    return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
  items = payload.get('productos') or []
  ids = [it.get('producto_id') or it.get('id') for it in items if (it.get('producto_id') or it.get('id'))]
  productos = ProductoBar.objects.filter(id__in=ids).prefetch_related('receta_items__ingrediente')
  resp = []
  for p in productos:
    # Si no hay receta, asumimos infinito (o al menos 1) de disponibilidad; mostraremos -1 para indicar desconocido
    receta = list(p.receta_items.all())
    if not receta:
      resp.append({
        'producto_id': p.id,
        'nombre': p.nombre,
        'disponible': -1,
        'detalle': []
      })
      continue
    # Cantidad máxima producible = min( floor(stock_i / cant_necesaria_i) )
    max_por_ingred = []
    detalle = []
    for it in receta:
      stock = getattr(it.ingrediente, 'cantidad', 0) or 0
      necesaria = float(it.cantidad)
      producible = int(stock // necesaria) if necesaria > 0 else 0
      max_por_ingred.append(producible)
      detalle.append({
        'ingrediente_id': it.ingrediente_id,
        'nombre': it.ingrediente.nombre,
        'stock': stock,
        'cant_necesaria': float(it.cantidad),
        'unidad': it.unidad,
      })
    disponible = min(max_por_ingred) if max_por_ingred else 0
    resp.append({
      'producto_id': p.id,
      'nombre': p.nombre,
      'disponible': disponible,
      'detalle': detalle
    })
  return JsonResponse({'success': True, 'items': resp})
