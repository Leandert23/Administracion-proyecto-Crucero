from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal
from django.http import JsonResponse

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
  try:
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
  except Exception as e:
    return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'}, status=500)


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
  from apps.bares_snacks.models import ProductoBar, IngredienteReceta
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
  # Crear ingredientes de receta (por defecto cantidad=1, unidad=medida del producto)
  for ing in ingredientes:
    # Buscar la descripción de la unidad
    unidad = dict(ing.UNIDADES_MEDIDA).get(ing.medida, ing.medida)
    IngredienteReceta.objects.create(producto_bar=producto, ingrediente=ing, cantidad=1, unidad=unidad)
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
  # Devuelve todos los tipos de producto, pero marca solo los tres requeridos con 'mostrar': True
  tipos = [
    (tipo_id, tipo_nombre, tipo_id in ("ALIMENTOS_FRESCOS", "ALIMENTOS_SECOS", "BEBIDAS"))
    for tipo_id, tipo_nombre in Producto.TIPOS_PRODUCTO
  ]
  subtipos = Producto.SUBTIPOS_PRODUCTO
  # Agrupar subtipos por tipo
  subtipos_por_tipo = {}
  for tipo_id, tipo_nombre, _ in tipos:
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
      'subtipos': subtipos_por_tipo[tipo_id],
      'mostrar': mostrar
    }
    for tipo_id, tipo_nombre, mostrar in tipos
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
  data = json.loads(request.body)
  items = data.get('items') or data.get('ingredientes') or []
  # Reemplazar receta completa: simple y claro
  p.receta_items.all().delete()
  from decimal import Decimal
  creados = []
  from apps.almacen.models import Producto as ProdAlmacen
  for it in items:
    if isinstance(it, dict):
      ing_id = it.get('ingrediente_id') or it.get('id')
      cantidad = it.get('cantidad', 1)
      unidad = it.get('unidad')
    else:
      ing_id = it
      cantidad = 1
      unidad = None
    if not ing_id:
      continue
    try:
      ing = ProdAlmacen.objects.get(id=ing_id)
    except ProdAlmacen.DoesNotExist:
      continue
    cant = Decimal(str(cantidad)) if cantidad is not None else 1
    unidad_final = str(unidad or ing.medida)
    obj = IngredienteReceta.objects.create(producto_bar=p, ingrediente=ing, cantidad=cant, unidad=unidad_final)
    creados.append({
      'id': obj.id,
      'ingrediente_id': obj.ingrediente_id,
      'ingrediente_nombre': ing.nombre,
      'cantidad': float(obj.cantidad),
      'unidad': obj.unidad
    })
  return JsonResponse({'success': True, 'producto_id': p.id, 'items': creados})
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
from apps.recursos_humanos.models import Personal
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

  # Empleados
  empleados = Personal.objects.all()
  empleados_data = [
    {
      'nombre': f"{e.nombre} {e.apellido}",
      'cargo': e.puesto,
      'horario': '09:00 - 17:00', # Ajusta si tienes campo horario
      'disponible': True # Ajusta si tienes campo de disponibilidad
    } for e in empleados
  ]

  ingredientes_almacen = get_ingredientes_almacen()

  context = {
    'crucero': crucero,
    'ingresos_totales': ingresos_totales,
    'ingresos_reales': ingresos_reales,
    'productos_stock': productos_stock,
    'bajo_stock': bajo_stock,
    'empleados': empleados_data,
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
    empleado_id = payload.get('empleado_id')
    tipo_consumo = payload.get('tipo_consumo')  # 'bar' | 'camarote'
    lugarentrega_id = payload.get('lugarentrega_id')  # requerido si bar
    habitacion_id = payload.get('habitacion_id')  # requerido si camarote
    nota = (payload.get('nota') or '').strip()
    productos = payload.get('productos') or []  # [{producto_id, cantidad}]

    # Validaciones mínimas: ahora cliente y empleado son opcionales
    if not productos:
      return JsonResponse({'success': False, 'error': 'Debe incluir al menos un producto'}, status=400)

    from apps.bares_snacks.models import ProductoBar
    from apps.ventas.models import Cliente
    from apps.recursos_humanos.models import Personal
    from apps.cruceros.models import Instalacion, Habitacion

    # Verificar existencia entidades si se enviaron
    cliente = None
    empleado = None
    if cliente_id:
      try:
        cliente = Cliente.objects.get(id=cliente_id)
      except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entidad no encontrada: Cliente'}, status=404)
    if empleado_id:
      try:
        empleado = Personal.objects.get(id=empleado_id)
      except Personal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entidad no encontrada: Personal'}, status=404)

    instalacion = None
    habitacion = None
    if tipo_consumo == 'bar':
      if not lugarentrega_id:
        return JsonResponse({'success': False, 'error': 'lugarentrega_id es requerido para consumo en bar'}, status=400)
      try:
        instalacion = Instalacion.objects.get(id=lugarentrega_id)
      except Instalacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Instalación no encontrada'}, status=404)
    elif tipo_consumo == 'camarote':
      if not habitacion_id:
        return JsonResponse({'success': False, 'error': 'habitacion_id es requerido para consumo en camarote'}, status=400)
      try:
        habitacion = Habitacion.objects.get(id=habitacion_id)
      except Habitacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Habitación no encontrada'}, status=404)

    # Crear pedido
    try:
      # Generar número de factura
      def generar_numero_factura(pedido_id, lugar_nombre, productos):
          lugarCod = (lugar_nombre or '').upper().replace(" ","").replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")
          lugarCod = ''.join([c for c in lugarCod if c.isalpha()])[:3]
          if len(lugarCod) < 3:
              lugarCod = (lugarCod + 'XXX')[:3]
          correlativo = str(pedido_id).zfill(4)
          es_premium = any((d.get('plan') == 'pago' or d.get('plan') == 'premium') for d in productos)
          factura = f"BR-{lugarCod}-{correlativo}"
          if es_premium:
              factura += "-PR"
          return factura

      pedido = Pedidos.objects.create(
        empleado=empleado,
        cliente=cliente,
        lugarentrega=instalacion if tipo_consumo == 'bar' else None,
        habitacion=habitacion if tipo_consumo == 'camarote' else None,
        estado='pendiente'
      )
      # Asignar número de factura
      lugar_nombre = str(instalacion.nombre) if instalacion else None
      numero_factura = generar_numero_factura(pedido.id, lugar_nombre, productos)
      pedido.numero_factura = numero_factura
      pedido.save(update_fields=['numero_factura'])
    except IntegrityError as ie:
      diag = {
        'empleado_id': getattr(empleado, 'id', None),
        'cliente_id': getattr(cliente, 'id', None),
        'lugarentrega_id': getattr(instalacion, 'id', None),
        'habitacion_id': getattr(habitacion, 'id', None),
      }
      try:
        from apps.recursos_humanos.models import Personal as PersM
        diag['empleado_exists'] = bool(PersM.objects.filter(id=diag['empleado_id']).exists()) if diag['empleado_id'] else False
      except Exception:
        diag['empleado_exists'] = 'unknown'
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
        'plan': getattr(prod, 'plan', None),
        'receta': getattr(prod, 'receta', '') or '',
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
        'empleado_id': empleado.id if empleado else None,
  'empleado_nombre': (f"{empleado.nombre} {empleado.apellido}".strip() if empleado else None),
  'empleado_categoria': (empleado.categoria if empleado else None),
  'empleado_puesto': (empleado.puesto if empleado else None),
  'lugarentrega_id': instalacion.id if instalacion else None,
  'lugarentrega_nombre': str(instalacion) if instalacion else None,
  'habitacion_id': habitacion.id if habitacion else None,
  'habitacion_nombre': (f"Hab. {habitacion.numero} ({habitacion.codigo_ubicacion})" if habitacion else None),
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


@csrf_exempt
@require_POST
def actualizar_pedido_api(request, pedido_id: int):
  """Permite modificar un pedido solo si está en estado 'pendiente'. Reemplaza los detalles y puede actualizar empleado, lugar/nota."""
  import json
  from django.db import transaction
  try:
    p = Pedidos.objects.get(id=pedido_id)
  except Pedidos.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)
  if p.estado != 'pendiente':
    return JsonResponse({'success': False, 'error': 'Solo se puede modificar un pedido en estado pendiente'}, status=400)
  try:
    payload = json.loads(request.body or '{}')
  except json.JSONDecodeError:
    return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
  empleado_id = payload.get('empleado_id')
  tipo_consumo = payload.get('tipo_consumo')
  lugarentrega_id = payload.get('lugarentrega_id')
  habitacion_id = payload.get('habitacion_id')
  nota = (payload.get('nota') or '').strip()
  items = payload.get('productos') or []
  from apps.bares_snacks.models import ProductoBar
  from apps.recursos_humanos.models import Personal
  from apps.cruceros.models import Instalacion, Habitacion
  # Validar empleado si se envió
  if empleado_id is not None:
    if empleado_id:
      try:
        p.empleado = Personal.objects.get(id=empleado_id)
      except Personal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    else:
      p.empleado = None
  # Actualizar lugarentrega según tipo
  if tipo_consumo == 'bar':
    if lugarentrega_id:
      try:
        p.lugarentrega = Instalacion.objects.get(id=lugarentrega_id)
      except Instalacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Instalación no encontrada'}, status=404)
    else:
      return JsonResponse({'success': False, 'error': 'lugarentrega_id requerido para consumo en bar'}, status=400)
  elif tipo_consumo == 'camarote':
    p.lugarentrega = None
    if habitacion_id:
      try:
        p.habitacion = Habitacion.objects.get(id=habitacion_id)
      except Habitacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Habitación no encontrada'}, status=404)
    else:
      return JsonResponse({'success': False, 'error': 'habitacion_id requerido para consumo en camarote'}, status=400)
  # Nota (si quieres persistirla; actualmente _serialize pone nota None)
  # Si el modelo Pedidos no tiene campo nota, puedes omitir guardarla.
  try:
    with transaction.atomic():
      # Reemplazar detalles
      p.detalles.all().delete()
      detalles_resp = []
      for it in items:
        pid = it.get('producto_id') or it.get('id')
        cant = int(it.get('cantidad') or 0)
        if not pid or cant <= 0:
          continue
        try:
          prod = ProductoBar.objects.get(id=pid)
        except ProductoBar.DoesNotExist:
          continue
        DetallePedido.objects.create(pedido=p, producto=prod, cantidad=cant)
      p.save()
  except IntegrityError as ie:
    return JsonResponse({'success': False, 'error': f'Error al actualizar: {ie}'}, status=400)
  return JsonResponse({'success': True, 'pedido': _serialize_pedido(p)})


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
      'plan': getattr(d.producto, 'plan', None),
      'receta': getattr(d.producto, 'receta', '') or '',
      'subtotal': subtotal,
    })
    total += subtotal
  fecha_hora = timezone.localtime(p.fecha_hora)
  # Datos de empleado, si existe
  emp_nombre = None
  emp_categoria = None
  emp_puesto = None
  try:
    if p.empleado_id and getattr(p, 'empleado', None):
      emp_nombre = f"{getattr(p.empleado, 'nombre', '')} {getattr(p.empleado, 'apellido', '')}".strip()
      emp_categoria = getattr(p.empleado, 'categoria', None)
      emp_puesto = getattr(p.empleado, 'puesto', None)
  except Exception:
    pass
  return {
    'id': p.id,
    'estado': p.estado,
    'cliente_id': p.cliente_id,
    'empleado_id': p.empleado_id,
    'empleado_nombre': emp_nombre,
    'empleado_categoria': emp_categoria,
    'empleado_puesto': emp_puesto,
    'lugarentrega_id': p.lugarentrega_id,
    'lugarentrega_nombre': str(p.lugarentrega) if p.lugarentrega_id else None,
    'habitacion_id': getattr(p, 'habitacion_id', None),
    'habitacion_nombre': (f"Hab. {getattr(p.habitacion, 'numero', '')} ({getattr(p.habitacion, 'codigo_ubicacion', '')})" if getattr(p, 'habitacion_id', None) else None),
    'tipo_consumo': 'bar' if p.lugarentrega_id else 'camarote',
    'productos': detalles_resp,
    'total': total,
    'nota': None,
    'fecha_hora': fecha_hora.isoformat(),
    'fecha': fecha_hora.date().isoformat(),
    'hora': fecha_hora.strftime('%H:%M'),
    'numero_factura': getattr(p, 'numero_factura', None),
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
  # Si vamos a completar, intentamos actualizar stock de los ingredientes de cada producto
  if nuevo == 'completado' and actual != 'completado':
    from django.db import transaction
    try:
      with transaction.atomic():
        # cambiar estado primero en memoria, aplicar stock y persistir al final si todo ok
        # Construir requerimientos por ingrediente de almacén
        from apps.bares_snacks.models import IngredienteReceta
        from collections import defaultdict
        requeridos = defaultdict(float)  # producto_almacen_id -> cantidad total
        detalles = list(p.detalles.select_related('producto').all())
        # Para cada detalle, acumular ingredientes
        for det in detalles:
          prod = det.producto
          if not prod:
            continue
          for ir in prod.receta_items.select_related('ingrediente').all():
            if not ir.ingrediente_id:
              continue
            # cantidad puede ser decimal; multiplicar por cantidad del detalle
            try:
              cantidad_need = float(ir.cantidad) * float(det.cantidad)
            except Exception:
              cantidad_need = float(det.cantidad)
            requeridos[ir.ingrediente_id] += cantidad_need
        # Ejecutar retiros FIFO en almacén
        from apps.almacen.Services.products import retirar_producto_fifo
        import math
        for prod_id, cant in requeridos.items():
          # Convertir a entero, redondeando hacia arriba para garantizar disponibilidad
          cant_int = int(math.ceil(cant)) if cant > 0 else 0
          if cant_int <= 0:
            continue
          retirar_producto_fifo(prod_id, cant_int, modulo='BARES_SNACKS', descripcion=f'Pedido #{p.id}')
        # Finalmente, persistir estado
        p.estado = nuevo
        p.save(update_fields=['estado'])
    except Exception as e:
      return JsonResponse({'success': False, 'error': f'No se pudo completar el pedido por stock: {e}'}, status=400)
  else:
    p.estado = nuevo
    p.save(update_fields=['estado'])
  return JsonResponse({'success': True, 'pedido': _serialize_pedido(p)})


@csrf_exempt
@require_POST
def eliminar_detalle_pedido_api(request, pedido_id: int, detalle_id: int):
  """Elimina un solo detalle (producto) de un pedido pendiente. Si el pedido queda sin detalles, elimina el pedido.
  Respuestas:
    - { success: true, pedido_deleted: true, deleted_detalle_id }
    - { success: true, pedido: <pedido actualizado>, deleted_detalle_id }
  """
  try:
    p = Pedidos.objects.get(id=pedido_id)
  except Pedidos.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)
  if p.estado != 'pendiente':
    return JsonResponse({'success': False, 'error': 'Solo se puede modificar un pedido en estado pendiente'}, status=400)
  try:
    det = p.detalles.get(id=detalle_id)
  except DetallePedido.DoesNotExist:
    return JsonResponse({'success': False, 'error': 'Detalle no encontrado en el pedido'}, status=404)
  det.delete()
  if not p.detalles.exists():
    pid = p.id
    p.delete()
    return JsonResponse({'success': True, 'pedido_deleted': True, 'deleted_detalle_id': detalle_id, 'pedido_id': pid})
  # Pedido aún tiene otros detalles; devolver serializado
  return JsonResponse({'success': True, 'pedido': _serialize_pedido(p), 'deleted_detalle_id': detalle_id})


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


@require_GET
def empleado_info_api(request, empleado_id: int):
  """Devuelve info básica del empleado (Personal): nombre completo, categoria (cargo) y puesto."""
  try:
    from apps.recursos_humanos.models import Personal
    e = Personal.objects.get(id=empleado_id)
  except Exception:
    return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
  return JsonResponse({
    'success': True,
    'empleado': {
      'id': e.id,
      'nombre': e.nombre,
      'apellido': e.apellido,
      'nombre_completo': f"{e.nombre} {e.apellido}",
      'categoria': e.categoria,
      'puesto': e.puesto,
    }
  })


# ===================== ANALÍTICAS ===================== #
@require_GET
def analisis_mas_vendidos_api(request):
  """Devuelve productos más vendidos agrupados por categoría (historial = pedidos completados).
  Query params: limit (por categoría), default 5.
  Respuesta: { success, categorias: [{ categoria, items: [{producto_id,nombre,total}]}] }
  """
  from apps.bares_snacks.models import DetallePedido
  try:
    limit = int(request.GET.get('limit') or 5)
    if limit <= 0:
      limit = 5
  except ValueError:
    limit = 5
  # Aggregate total vendido por producto en pedidos completados
  qs = (DetallePedido.objects
        .filter(pedido__estado='completado')
        .values('producto_id', 'producto__nombre', 'producto__categoria')
        .annotate(total=Sum('cantidad'))
        .order_by('producto__categoria', '-total'))
  # Agrupar por categoría
  categorias = {}
  for row in qs:
    cat = row.get('producto__categoria') or 'Sin categoría'
    categorias.setdefault(cat, [])
    categorias[cat].append({
      'producto_id': row['producto_id'],
      'nombre': row.get('producto__nombre') or '',
      'total': int(row['total'] or 0),
    })
  # Limitar por categoría
  resp = []
  for cat, items in categorias.items():
    resp.append({
      'categoria': cat,
      'items': items[:limit]
    })
  # Orden alfabético por categoría
  resp.sort(key=lambda x: (x['categoria'] or '').lower())
  return JsonResponse({'success': True, 'categorias': resp})


@require_GET
def analisis_stock_api(request):
  """Devuelve resumen de stock: bajo (CRITICO/BAJO) y lista de productos con stock ideal (>= cantidad_ideal).
  Query params: limit_ideal (default 10)
  Respuesta: { success, bajo: [...], ideal: [...] }
  """
  from apps.almacen.models import Producto as ProdAlm
  try:
    limit_ideal = int(request.GET.get('limit_ideal') or 10)
  except ValueError:
    limit_ideal = 10
  bajo = []
  ideal = []
  for p in ProdAlm.objects.select_related('seccion__almacen').all():
    try:
      actual = int(p.cantidad)
    except Exception:
      actual = 0
    item = {
      'id': p.id,
      'nombre': p.nombre,
      'tipo': p.tipo,
      'subtipo': p.subtipo,
      'cantidad': actual,
      'cantidad_ideal': int(p.cantidad_ideal or 0),
      'estado': p.estado,
    }
    # Bajo: estrictamente por debajo del 30% del ideal
    try:
      ci = int(p.cantidad_ideal or 0)
    except Exception:
      ci = 0
    if ci > 0 and actual < (0.3 * ci):
      bajo.append(item)
    if actual >= (p.cantidad_ideal or 0):
      ideal.append(item)
  # ordenar bajo por % faltante desc
  def falta_ratio(it):
    ideal = it['cantidad_ideal'] or 1
    return max(0.0, 1.0 - (it['cantidad'] / ideal if ideal else 0))
  bajo.sort(key=falta_ratio, reverse=True)
  # ordenar ideal por cantidad_ideal desc y limitar
  ideal.sort(key=lambda it: it['cantidad_ideal'], reverse=True)
  if limit_ideal and limit_ideal > 0:
    ideal = ideal[:limit_ideal]
  return JsonResponse({'success': True, 'bajo': bajo, 'ideal': ideal})


@csrf_exempt
@require_POST
def solicitar_restock_api(request):
  """Crea una o varias Órdenes de Compra para reponer stock de productos de almacén.
  Entrada:
    - { producto_id, cantidad, comentario? }
    - o { items: [{ producto_id, cantidad }], comentario? }
  Salida: { success, creados: [{ id, producto_id, cantidad, estado }] }
  """
  import json
  try:
    payload = json.loads(request.body or '{}')
  except json.JSONDecodeError:
    return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
  items = payload.get('items')
  if not items:
    pid = payload.get('producto_id')
    cant = payload.get('cantidad')
    if pid and cant:
      items = [{ 'producto_id': pid, 'cantidad': cant }]
  if not items or not isinstance(items, list):
    return JsonResponse({'success': False, 'error': 'items vacío'}, status=400)
  from apps.almacen.models import Producto as ProdAlm, OrdenCompra
  creados = []
  for it in items:
    try:
      pid = int(it.get('producto_id'))
      cant = int(it.get('cantidad'))
    except Exception:
      continue
    if pid <= 0 or cant <= 0:
      continue
    try:
      prod = ProdAlm.objects.get(id=pid)
    except ProdAlm.DoesNotExist:
      continue
    oc = OrdenCompra.objects.create(producto=prod, cantidad_productos=cant, precio_lote=0, estado='PENDIENTE')
    creados.append({ 'id': oc.id, 'producto_id': prod.id, 'cantidad': cant, 'estado': oc.estado })
  if not creados:
    return JsonResponse({'success': False, 'error': 'No se pudo crear ninguna orden'}, status=400)
  return JsonResponse({'success': True, 'creados': creados})
