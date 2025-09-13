# Datos de prueba mockeados que coinciden con la estructura real de comidasPreviu
MOCK_INGREDIENTES_COMIDAS_PREVIA = [
    {
        'id': 1,
        'ingredientes': 'Tomate cherry',
        'tipo': 'Verdura',
        'subtipo': 'Fruto',
        'clase_alimenticia': 'Frutas y verduras',
        'detalle': 'Tomates cherry frescos importados, ideales para ensaladas',
        'platos': 'Ensaladas, Salsas',
        'origen': 'México',
        'fuente': 'Proveedor local'
    },
    {
        'id': 2,
        'ingredientes': 'Cebolla blanca',
        'tipo': 'Verdura',
        'subtipo': 'Bulbo',
        'clase_alimenticia': 'Verduras',
        'detalle': 'Cebollas blancas de calidad premium, dulces y crujientes',
        'platos': 'Salsas, Guarniciones, Ensaladas',
        'origen': 'Chile',
        'fuente': 'Importación directa'
    },
    {
        'id': 3,
        'ingredientes': 'Pechuga de pollo',
        'tipo': 'Proteína',
        'subtipo': 'Carne blanca',
        'clase_alimenticia': 'Carnes',
        'detalle': 'Pechuga de pollo sin hueso ni piel, de granja libre',
        'platos': 'Platos principales, Ensaladas proteicas',
        'origen': 'Argentina',
        'fuente': 'Granja certificada'
    },
    {
        'id': 4,
        'ingredientes': 'Arroz basmati',
        'tipo': 'Cereal',
        'subtipo': 'Arroz',
        'clase_alimenticia': 'Cereales',
        'detalle': 'Arroz basmati premium, grano largo y aromático',
        'platos': 'Platos principales, Guarniciones',
        'origen': 'India',
        'fuente': 'Importación especializada'
    },
    {
        'id': 5,
        'ingredientes': 'Aceite de oliva virgen',
        'tipo': 'Condimento',
        'subtipo': 'Aceite',
        'clase_alimenticia': 'Grasas',
        'detalle': 'Aceite de oliva virgen extra primera prensada, intenso sabor',
        'platos': 'Cocción, Aderezos, Conservación',
        'origen': 'España',
        'fuente': 'Cooperativa olivícola'
    }
]

from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Crucero, Restaurante, MenuItem, Employee, MaintenanceItem, ConsumptionRecord, Menu, Platillo, Ingrediente, IngredientePlatillo, PersonalRRHH
from .models import ServiceInvoice, ServiceInvoiceItem, BuffetBulkRecord

def dashboard(request):
    """Vista principal del dashboard del restaurante"""
    context = {
        'total_cruceros': Crucero.objects.count(),
        'total_restaurants': Restaurante.objects.count(),
        'total_employees': Employee.objects.filter(active=True).count(),
        'low_stock_items': MenuItem.objects.filter(quantity__lt=10).count(),
        'pending_maintenance': MaintenanceItem.objects.filter(status='pendiente').count(),
    }
    return render(request, 'restaurant/dashboard.html', context)

def stock_view(request):
    """Vista para gestión de stock/inventario"""
    cruceros = Crucero.objects.all()

    # Crucero activo (definido por el módulo general); fallback por querystring opcional
    current_cruise_id = request.session.get('current_cruise_id') or request.GET.get('cruise')
    current_cruise = None
    if current_cruise_id:
        try:
            current_cruise = Crucero.objects.get(id=current_cruise_id)
        except Crucero.DoesNotExist:
            current_cruise_id = None

    # Filtros
    selected_restaurant = request.GET.get('restaurant', '')

    # Filtrar restaurantes por crucero activo
    restaurants = Restaurante.objects.all()
    if current_cruise_id:
        restaurants = restaurants.filter(crucero_id=current_cruise_id)

    # Items del menú filtrados por crucero activo y, opcionalmente, por restaurante
    menu_items = MenuItem.objects.all()
    if current_cruise_id:
        menu_items = menu_items.filter(restaurant__crucero_id=current_cruise_id)
    if selected_restaurant:
        menu_items = menu_items.filter(restaurant_id=selected_restaurant)

    context = {
        'cruceros': cruceros,  # compatibilidad
        'restaurants': restaurants,
        'menu_items': menu_items,
        'selected_cruise': current_cruise_id,  # compatibilidad con plantillas previas
        'selected_restaurant': selected_restaurant,
        'current_cruise_id': current_cruise_id,
        'current_cruise': current_cruise,
    }
    return render(request, 'restaurant/stock.html', context)

def employees_view(request):
    """Vista para gestión de empleados (usa el modelo Employee real)."""
    employees = Employee.objects.select_related('restaurant').all()

    estado_filter = request.GET.get('estado', '')  # '1' activos, '2' inactivos
    if estado_filter == '1':
        employees = employees.filter(active=True)
    elif estado_filter == '2':
        employees = employees.filter(active=False)

    context = {
        'employees': employees,
        'estado_filter': estado_filter,
    }
    return render(request, 'restaurant/employees.html', context)

def maintenance_view(request):
    """Vista para gestión de mantenimiento"""
    maintenance_items = MaintenanceItem.objects.all().select_related('restaurant')
    restaurants = Restaurante.objects.all()
    
    context = {
        'maintenance_items': maintenance_items,
        'restaurants': restaurants,
    }
    return render(request, 'restaurant/maintenance.html', context)

def consumption_view(request):
    """Vista para registro de consumo"""
    cruceros = Crucero.objects.all()
    restaurants = Restaurante.objects.all()

    # Si llega un restaurante seleccionado, redirigir a la vista adecuada
    sel_rest = request.GET.get('restaurante')
    if sel_rest:
        r = None
        if sel_rest.isdigit():
            try:
                r = Restaurante.objects.get(id=sel_rest)
            except Restaurante.DoesNotExist:
                r = None
        else:
            # tratar como tipo (buffet, main, restaurant)
            r = Restaurante.objects.filter(type=sel_rest).first()
        if r:
            if r.type == 'buffet':
                return redirect('restaurant:buffet_bulk', restaurant_id=r.id)
            return redirect('restaurant:order_entry', restaurant_id=r.id)

    # Obtener crucero activo (definido por el módulo general). Fallback: None.
    current_cruise_id = request.session.get('current_cruise_id') or request.GET.get('cruise')
    current_cruise = None
    if current_cruise_id:
        try:
            current_cruise = Crucero.objects.get(id=current_cruise_id)
        except Crucero.DoesNotExist:
            current_cruise_id = None

    # Obtener día actual del crucero desde sesión (controlado desde Inicio); fallback por query
    current_day = request.session.get('current_cruise_day') or request.GET.get('day')

    context = {
        'cruceros': cruceros,  # se mantiene por compatibilidad aunque ya no se muestra
        'restaurants': restaurants,
        'current_cruise_id': current_cruise_id,
        'current_cruise': current_cruise,
        'current_day': current_day,
    }
    return render(request, 'restaurant/consumption.html', context)

def buffet_view(request):
    """Vista específica para el restaurante Buffet"""
    return render(request, 'restaurant/buffet.html')

def main_dining_room_view(request):
    """Vista específica para el Main Dining Room"""
    return render(request, 'restaurant/main_dining_room.html')

def especialidades_view(request):
    """Vista específica para el restaurante de Especialidades"""
    return render(request, 'restaurant/especialidades.html')

# ----------------------------
# Pedidos (facturación no buffet)
# ----------------------------
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect

@require_http_methods(["GET", "POST"])
def order_entry_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurante, id=restaurant_id)
    if restaurant.type == 'buffet':
        return redirect('restaurant:buffet_bulk', restaurant_id=restaurant.id)
    platillos = Platillo.objects.filter(activo=True, restaurantes=restaurant).order_by('nombre') | Platillo.objects.filter(activo=True, menu__restaurante=restaurant)
    platillos = platillos.distinct()
    cruise_day = request.session.get('current_cruise_day')

    if request.method == 'POST':
        room = request.POST.get('room_number','').strip()
        items_data = []
        for key, val in request.POST.items():
            if key.startswith('item_'):
                try:
                    plat_id = int(key.split('_')[1])
                    qty = int(val)
                    if qty > 0:
                        items_data.append((plat_id, qty))
                except ValueError:
                    continue
        if not items_data:
            messages.error(request, 'Debe seleccionar al menos un platillo con cantidad > 0')
        else:
            invoice = ServiceInvoice.objects.create(restaurant=restaurant, cruise_id=request.session.get('current_cruise_id'), cruise_day=cruise_day, room_number=room or 'N/D')
            for plat_id, qty in items_data:
                try:
                    p = Platillo.objects.get(id=plat_id)
                except Platillo.DoesNotExist:
                    continue
                ServiceInvoiceItem.objects.create(invoice=invoice, platillo=p, quantity=qty, unit_price=p.precio, line_total=0, included=(p.precio == 0))
            invoice.recalc_total()
            messages.success(request, f'Factura {invoice.code} creada.')
            return redirect('restaurant:order_entry', restaurant_id=restaurant.id)

    context = {
        'restaurant': restaurant,
        'platillos': platillos,
    }
    return render(request, 'restaurant/order_entry.html', context)

@require_http_methods(["GET", "POST"])
def buffet_bulk_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurante, id=restaurant_id)
    if restaurant.type != 'buffet':
        return redirect('restaurant:order_entry', restaurant_id=restaurant.id)
    platillos = Platillo.objects.filter(activo=True, restaurantes=restaurant).order_by('nombre') | Platillo.objects.filter(activo=True, menu__restaurante=restaurant)
    platillos = platillos.distinct()
    cruise_day = request.session.get('current_cruise_day')
    if request.method == 'POST':
        created = 0
        for key, val in request.POST.items():
            if key.startswith('item_'):
                try:
                    plat_id = int(key.split('_')[1])
                    qty = int(val)
                    if qty > 0:
                        BuffetBulkRecord.objects.create(restaurant=restaurant, cruise_id=request.session.get('current_cruise_id'), cruise_day=cruise_day, platillo_id=plat_id, quantity=qty)
                        created += 1
                except ValueError:
                    continue
        if created:
            messages.success(request, f'{created} registros buffet creados.')
        else:
            messages.error(request, 'No se ingresaron cantidades.')
        return redirect('restaurant:buffet_bulk', restaurant_id=restaurant.id)
    return render(request, 'restaurant/buffet_bulk.html', {'restaurant': restaurant, 'platillos': platillos})

def records_view(request):
    """Vista para registros de consumo"""
    # Usar crucero activo desde sesión o query como fallback
    current_cruise_id = request.session.get('current_cruise_id') or request.GET.get('cruise', '')
    consumption_records = ConsumptionRecord.objects.all().select_related('menu_item', 'menu_item__restaurant')
    if current_cruise_id:
        consumption_records = consumption_records.filter(menu_item__restaurant__crucero_id=current_cruise_id)

    cruceros = Crucero.objects.all()  # compatibilidad

    # Obtener objeto de crucero activo
    current_cruise = None
    if current_cruise_id:
        try:
            current_cruise = Crucero.objects.get(id=current_cruise_id)
        except Crucero.DoesNotExist:
            current_cruise = None

    # Construir datos por día (1..8)
    days_range = list(range(1, 9))
    days = {d: {'items': [], 'total': 0.0} for d in days_range}
    for rec in consumption_records:
        day = getattr(rec, 'cruise_day', None)
        if day not in days:
            continue
        mi = rec.menu_item
        unit_price = float(getattr(mi, 'price', 0) or 0)
        included = bool(getattr(mi, 'included', False))
        line_total = 0.0 if included else unit_price * int(getattr(rec, 'quantity', 0) or 0)
        days[day]['items'].append({
            'name': mi.name,
            'restaurant': getattr(mi.restaurant, 'name', ''),
            'qty': int(getattr(rec, 'quantity', 0) or 0),
            'included': included,
            'unit_price': unit_price,
            'line_total': line_total,
        })
        days[day]['total'] += line_total

    # Integrar facturas y registros buffet dentro de cada día
    invoice_qs = ServiceInvoice.objects.select_related('restaurant').order_by('-created_at')
    buffet_qs = BuffetBulkRecord.objects.select_related('restaurant', 'platillo').order_by('-created_at')
    if current_cruise_id:
        invoice_qs = invoice_qs.filter(cruise_id=current_cruise_id)
        buffet_qs = buffet_qs.filter(cruise_id=current_cruise_id)
    for inv in invoice_qs:
        d = inv.cruise_day or 0
        if d in days:
            days[d].setdefault('invoices', []).append(inv)
    for br in buffet_qs:
        d = br.cruise_day or 0
        if d in days:
            days[d].setdefault('buffet', []).append(br)

    # Lista auxiliar para plantillas con nuevas claves
    days_list = []
    for d in days_range:
        days_list.append({
            'day': d,
            'items': days[d]['items'],
            'total': days[d]['total'],
            'invoices': days[d].get('invoices', []),
            'buffet_records': days[d].get('buffet', []),
        })

    context = {
        'consumption_records': consumption_records,
        'cruceros': cruceros,
        'selected_cruise': current_cruise_id,
        'current_cruise_id': current_cruise_id,
        'current_cruise': current_cruise,
        'days': days,
        'days_range': days_range,
        'days_list': days_list,
    }
    return render(request, 'restaurant/records.html', context)

def get_restaurants(request):
    """Devuelve lista mínima de restaurantes para selects (AJAX GET)"""
    restaurants = Restaurante.objects.all().values('id', 'name', 'type', 'area_total')
    # Mapear display de type
    items = []
    for r in restaurants:
        obj = Restaurante(id=r['id'], name=r['name'], type=r['type'])
        # Incluir dimensión si existe
        dimension_display = ""
        if r['area_total']:
            dimension_display = f" ({r['area_total']} m²)"
        else:
            dimension_display = " (Sin dimensión)"

        items.append({
            'id': r['id'],
            'name': r['name'],
            'type_display': obj.get_type_display(),
            'area_total': r['area_total'],
            'dimension_display': dimension_display
        })
    return JsonResponse({'restaurants': items})

# AJAX Views
@csrf_exempt
@require_POST
def add_menu_item(request):
    """Agregar nuevo item al menú"""
    try:
        data = json.loads(request.body)
        restaurant = Restaurante.objects.get(id=data['restaurant_id'])
        
        menu_item = MenuItem.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            restaurant=restaurant,
            quantity=int(data['quantity']),
            price=float(data.get('price', 0)),
            included=data.get('included', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Item agregado exitosamente',
            'item': {
                'id': menu_item.id,
                'name': menu_item.name,
                'quantity': menu_item.quantity,
                'price': float(menu_item.price),
                'included': menu_item.included
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def add_employee(request):
    """Agregar nuevo empleado"""
    try:
        data = json.loads(request.body)
        restaurant = Restaurante.objects.get(id=data['restaurant_id'])
        
        employee = Employee.objects.create(
            name=data['name'],
            position=data['position'],
            shift=data['shift'],
            restaurant=restaurant,
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Empleado agregado exitosamente',
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'position': employee.get_position_display(),
                'shift': employee.get_shift_display(),
                'restaurant': employee.restaurant.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
@require_POST
def add_maintenance(request):
    """Agregar item de mantenimiento"""
    try:
        data = json.loads(request.body)
        restaurant = Restaurante.objects.get(id=data['restaurant_id'])
        
        maintenance_item = MaintenanceItem.objects.create(
            area=data['area'],
            description=data['description'],
            priority=data['priority'],
            restaurant=restaurant,
            reported_by=data.get('reported_by', 'Sistema')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Problema de mantenimiento reportado exitosamente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
@require_POST
def register_consumption(request):
    """Registrar consumo"""
    try:
        data = json.loads(request.body)
        menu_item = MenuItem.objects.get(id=data['menu_item_id'])
        quantity = int(data['quantity'])
        
        # Verificar stock disponible
        if menu_item.quantity < quantity:
            return JsonResponse({
                'success': False, 
                'message': f'Stock insuficiente. Solo hay {menu_item.quantity} unidades disponibles.'
            })
        
        # Actualizar stock
        menu_item.quantity -= quantity
        menu_item.save()
        
        # Crear registro de consumo
        consumption_record = ConsumptionRecord.objects.create(
            menu_item=menu_item,
            cruise_day=int(data['cruise_day']),
            quantity=quantity
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Consumo registrado exitosamente',
            'new_stock': menu_item.quantity
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def get_menu_items(request):
    """Obtener items del menú por restaurante"""
    restaurant_id = request.GET.get('restaurant_id')
    if restaurant_id:
        menu_items = MenuItem.objects.filter(restaurant_id=restaurant_id)
        items_data = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'included': item.included
            }
            for item in menu_items
        ]
        return JsonResponse({'items': items_data})
    return JsonResponse({'items': []})


def get_menus_for_day(request):
    """Retorna los menús disponibles para un crucero en un día dado.
    Responde JSON con { menus: [ { name, items: [{id,name,price,included}] } ] }
    """
    cruise_id = request.GET.get('cruise_id')
    day = request.GET.get('day')
    # Aquí simplificamos: devolvemos todos los restaurantes del crucero y sus items.
    if not cruise_id or not day:
        return JsonResponse({'menus': []})

    restaurants = Restaurante.objects.filter(crucero_id=cruise_id)
    menus = []
    for r in restaurants:
        items = MenuItem.objects.filter(restaurant=r)
        items_data = []
        for it in items:
            items_data.append({
                'id': it.id,
                'name': it.name,
                'price': float(it.price),
                'included': it.included,
            })
        if items_data:
            menus.append({'name': r.name, 'items': items_data})

    return JsonResponse({'menus': menus})


@csrf_exempt
@require_POST
def register_bulk_consumption(request):
    """Recibe { cruise_id, day, items: [{id, qty}] } y registra varios consumos.
    Actualiza stock y crea registros ConsumptionRecord.
    """
    try:
        data = json.loads(request.body)
        cruise_id = data.get('cruise_id')
        day = int(data.get('day'))
        items = data.get('items', [])

        created = []
        for it in items:
            item_id = it.get('id')
            qty = int(it.get('qty', 0))
            if qty <= 0:
                continue
            menu_item = MenuItem.objects.get(id=item_id)
            # Check stock
            if menu_item.quantity < qty and not menu_item.included:
                return JsonResponse({'success': False, 'message': f'Stock insuficiente para {menu_item.name}'} )

            # If not included, deduct stock
            if not menu_item.included:
                menu_item.quantity -= qty
                menu_item.save()

            cr = ConsumptionRecord.objects.create(
                menu_item=menu_item,
                cruise_day=day,
                quantity=qty
            )
            created.append({'id': cr.id, 'menu_item': menu_item.name})

        return JsonResponse({'success': True, 'message': 'Consumos registrados', 'created': created})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Nuevas vistas para la sección de Gestión
def gestion_view(request):
    """Vista principal de la sección de Gestión"""
    try:
        total_menus = Menu.objects.count()
    except Exception:
        total_menus = 0
    try:
        total_platillos = Platillo.objects.count()
    except Exception:
        total_platillos = 0
    orm_count = 0
    legacy_count = 0
    try:
        orm_count = Ingrediente.objects.count()
    except Exception:
        orm_count = 0
    # Intentar siempre contar en la tabla legacy si existe
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM restaurant_ingredientes')
            legacy_count = cursor.fetchone()[0] or 0
    except Exception:
        legacy_count = 0
    total_ingredientes = legacy_count if legacy_count > 0 else orm_count
    try:
        total_restaurantes = Restaurante.objects.count()
    except Exception:
        total_restaurantes = 0

    context = {
        'total_menus': total_menus,
        'total_platillos': total_platillos,
        'total_ingredientes': total_ingredientes,
        'total_restaurantes': total_restaurantes,
    }
    return render(request, 'restaurant/gestion.html', context)

def ingredientes_overview(request):
    """Devuelve ingredientes con columnas dinámicas desde tabla legada o desde ORM.
    Respuesta JSON: { source: 'legacy'|'orm', columns: [...], rows: [ {col: val}... ], total: n }
    """
    from django.db import connection
    source = 'orm'
    columns = []
    rows = []
    total = 0
    # Parámetros de paginación
    try:
        page = int(request.GET.get('page', '1'))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    try:
        page_size = int(request.GET.get('page_size', '25'))
        if page_size < 1:
            page_size = 25
        if page_size > 100:
            page_size = 100
    except ValueError:
        page_size = 25
    offset = (page - 1) * page_size

    # Filtros
    q = (request.GET.get('q') or '').strip()
    clase_f = (request.GET.get('clase') or '').strip()
    subtipo_f = (request.GET.get('subtipo') or '').strip()
    def fetch_from_table(table_name: str):
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                cols_info = cursor.fetchall()
                if cols_info:
                    cols = [c[1] for c in cols_info]
                    # Normalizar nombres para hacer matching case-insensitive y con espacios
                    import re
                    def norm(s: str) -> str:
                        return re.sub(r"[\s\-]+", "_", s.lower())
                    lower_map = {norm(c): c for c in cols}
                    def pick_col(candidates):
                        for cand in candidates:
                            if cand in lower_map:
                                return lower_map[cand]
                        return None
                    # Heurística de columnas (normalizadas)
                    name_col = pick_col(['nombre','ingrediente','ingredientes'])
                    clase_col = pick_col(['clase_alimenticia','clase','categoria','clasealimenticia','clasealimenticia'])
                    subtipo_col = pick_col(['subtipo','sub_tipo'])
                    # Helper para citar identificadores (columnas con espacios)
                    def qi(identifier: str) -> str:
                        return f'"{identifier}"'
                    # Conteo total sin filtros para decidir si permitir fallback
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                        total_all = cursor.fetchone()[0] or 0
                    except Exception:
                        total_all = 0

                    where = []
                    params = []
                    if q and name_col:
                        where.append(f"{qi(name_col)} LIKE ? COLLATE NOCASE")
                        params.append(f"%{q}%")
                    if clase_f and clase_col:
                        where.append(f"TRIM({qi(clase_col)}) = TRIM(?) COLLATE NOCASE")
                        params.append(clase_f)
                    if subtipo_f and subtipo_col:
                        where.append(f"TRIM({qi(subtipo_col)}) = TRIM(?) COLLATE NOCASE")
                        params.append(subtipo_f)
                    where_sql = (' WHERE ' + ' AND '.join(where)) if where else ''
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name}{where_sql}', params)
                    tot = cursor.fetchone()[0] or 0
                    # Datos filtrados (si hay)
                    data = []
                    if tot > 0:
                        cursor.execute(
                            f'SELECT * FROM {table_name}{where_sql} ORDER BY 1 LIMIT {int(page_size)} OFFSET {int(offset)}',
                            params
                        )
                        data = cursor.fetchall()
                    # Opciones para filtros (siempre, independientemente de tot)
                    subs = []
                    clases = []
                    if subtipo_col:
                        try:
                            cursor.execute(
                                f'SELECT DISTINCT {qi(subtipo_col)} FROM {table_name} WHERE {qi(subtipo_col)} IS NOT NULL LIMIT 200'
                            )
                            subs = [r[0] for r in cursor.fetchall() if r and r[0] is not None]
                        except Exception:
                            subs = []
                    if clase_col:
                        try:
                            cursor.execute(
                                f'SELECT DISTINCT {qi(clase_col)} FROM {table_name} WHERE {qi(clase_col)} IS NOT NULL LIMIT 200'
                            )
                            clases = [r[0] for r in cursor.fetchall() if r and r[0] is not None]
                        except Exception:
                            clases = []
                    # Si la tabla existe, siempre devolvemos resultado aunque tot sea 0
                    return cols, tot, [dict(zip(cols, r)) for r in data], {
                        'q': bool(name_col),
                        'clase': bool(clase_col),
                        'subtipo': bool(subtipo_col),
                        'clases': clases,
                        'subtipos': subs,
                        'total_all': total_all,
                    }
        except Exception:
            return None
        return None

    # Intentar tabla legada plural (única permitida)
    got = fetch_from_table('restaurant_ingredientes')
    if got:
        columns, total, rows, supports = got
        source = 'legacy'
    else:
        # Intentar comidasPreviu mediante ORM
        try:
            cols = ['id', 'ingredientes', 'tipo', 'subtipo', 'clase_alimenticia', 'detalle', 'platos', 'origen', 'fuente']
            from .models import ComidasPreviu as CP
            qs = CP.objects.all()
            if q:
                qs = qs.filter(ingredientes__icontains=q)
            if clase_f:
                qs = qs.filter(clase_alimenticia__iexact=clase_f)
            if subtipo_f:
                qs = qs.filter(subtipo__iexact=subtipo_f)
            total = qs.count()
            if total > 0:
                columns = cols
                rows = list(qs.values(*cols)[offset:offset+page_size])
                source = 'previu'
                supports = {
                    'q': True,
                    'clase': True,
                    'subtipo': True,
                    'clases': list(CP.objects.exclude(clase_alimenticia__isnull=True).exclude(clase_alimenticia='').values_list('clase_alimenticia', flat=True).distinct()[:200]),
                    'subtipos': list(CP.objects.exclude(subtipo__isnull=True).exclude(subtipo='').values_list('subtipo', flat=True).distinct()[:200]),
                }
        except Exception:
            pass
        # Fallback final a mock
        if total == 0:
            try:
                cols = ['id', 'ingredientes', 'tipo', 'subtipo', 'clase_alimenticia', 'detalle', 'platos', 'origen', 'fuente']
                from .views import MOCK_INGREDIENTES_COMIDAS_PREVIA as MK
            except Exception:
                cols = []
                MK = []
            if MK:
                # Filtrar mock según parámetros
                def keep(item):
                    if q and not (item.get('ingredientes') or '').lower().__contains__(q.lower()):
                        return False
                    if clase_f and (item.get('clase_alimenticia') or '') != clase_f:
                        return False
                    if subtipo_f and (item.get('subtipo') or '') != subtipo_f:
                        return False
                    return True
                filtered = [i for i in MK if keep(i)]
                columns = cols
                total = len(filtered)
                slice_ = filtered[offset:offset+page_size]
                rows = [
                    {
                        'id': item.get('id'),
                        'ingredientes': item.get('ingredientes'),
                        'tipo': item.get('tipo'),
                        'subtipo': item.get('subtipo'),
                        'clase_alimenticia': item.get('clase_alimenticia'),
                        'detalle': item.get('detalle'),
                        'platos': item.get('platos'),
                        'origen': item.get('origen'),
                        'fuente': item.get('fuente'),
                    }
                    for item in slice_
                ]
                source = 'mock'
                supports = {
                    'q': True,
                    'clase': True,
                    'subtipo': True,
                    'clases': sorted(list(set([i.get('clase_alimenticia') for i in MK if i.get('clase_alimenticia')])))[:200],
                    'subtipos': sorted(list(set([i.get('subtipo') for i in MK if i.get('subtipo')])))[:200],
                }

    if source == 'orm':
        # Definir columnas comunes del modelo nuevo
        columns = ['id', 'nombre', 'unidad', 'subtipo', 'activo', 'creado']
        try:
            qs = Ingrediente.objects.all()
            if q:
                qs = qs.filter(nombre__icontains=q)
            # No existe clase en el modelo nuevo; se ignora filtro de clase
            if subtipo_f:
                qs = qs.filter(subtipo=subtipo_f)
            total = qs.count()
            rows = list(qs.values(*columns)[offset:offset+page_size])
            supports = {
                'q': True,
                'clase': False,
                'subtipo': True,
                'clases': [],
                'subtipos': [s[0] for s in Ingrediente.SUBTIPOS],
            }
        except Exception:
            columns = []
            rows = []
            total = 0
            supports = {'q': True, 'clase': False, 'subtipo': False, 'clases': [], 'subtipos': []}

    return JsonResponse({
        'source': source,
        'columns': columns,
        'rows': rows,
        'total': total,
        'page': page,
        'page_size': page_size,
        'pages': (total + page_size - 1) // page_size if page_size else 1,
        'supports': supports if 'supports' in locals() else {'q': True, 'clase': False, 'subtipo': False, 'clases': [], 'subtipos': []},
    })

def ingredientes_list_view(request):
    """Lista de ingredientes.
    - Prioriza leer de la tabla legada `restaurant_ingredientes` si existe y tiene datos.
    - Si no, usa el modelo ORM `Ingrediente`.
    """
    legacy_rows = []
    legacy_columns = []
    legacy_total = 0
    orm_qs = Ingrediente.objects.all().order_by('nombre')
    source = 'orm'
    # Intentar leer de tabla legacy
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info('restaurant_ingredientes')")
            cols_info = cursor.fetchall()
            if cols_info:
                legacy_columns = [c[1] for c in cols_info]
                cursor.execute('SELECT COUNT(*) FROM restaurant_ingredientes')
                legacy_total = cursor.fetchone()[0] or 0
                if legacy_total > 0:
                    cursor.execute('SELECT * FROM restaurant_ingredientes ORDER BY 1 LIMIT 1000')
                    data = cursor.fetchall()
                    legacy_rows = [dict(zip(legacy_columns, row)) for row in data]
                    source = 'legacy'
    except Exception:
        pass

    # Paginación
    page = request.GET.get('page', 1)
    if source == 'legacy':
        paginator = Paginator(legacy_rows, 25)
        page_obj = paginator.get_page(page)
        context = {
            'source': source,
            'columns': legacy_columns,
            'page_obj': page_obj,
            'total': legacy_total,
        }
    else:
        paginator = Paginator(list(orm_qs.values('id', 'nombre', 'unidad', 'subtipo', 'activo', 'creado')), 25)
        page_obj = paginator.get_page(page)
        context = {
            'source': source,
            'columns': ['id', 'nombre', 'unidad', 'subtipo', 'activo', 'creado'],
            'page_obj': page_obj,
            'total': orm_qs.count(),
        }

    return render(request, 'restaurant/ingredients_list.html', context)

 

# AJAX Views para Gestión
@csrf_exempt
@require_POST
def create_menu(request):
    """Crear nuevo menú"""
    try:
        data = json.loads(request.body)
        restaurante = Restaurante.objects.get(id=data['restaurante_id'])
        
        menu = Menu.objects.create(
            nombre=data['nombre'],
            tipo=data['tipo'],
            descripcion=data.get('descripcion', ''),
            restaurante=restaurante
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Menú creado exitosamente',
            'menu': {
                'id': menu.id,
                'nombre': menu.nombre,
                'tipo': menu.get_tipo_display(),
                'restaurante': menu.restaurante.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def create_platillo(request):
    """Crear nuevo platillo"""
    try:
        data = json.loads(request.body)
        menu = Menu.objects.get(id=data['menu_id'])

        # Crear el platillo
        platillo = Platillo.objects.create(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            precio=float(data['precio']),
            menu=menu
        )

        # Asignar restaurantes al platillo
        if 'restaurantes' in data and data['restaurantes']:
            restaurantes_ids = data['restaurantes']
            if isinstance(restaurantes_ids, list):
                restaurantes = Restaurante.objects.filter(id__in=restaurantes_ids)
                platillo.restaurantes.set(restaurantes)
            else:
                # Si es un solo restaurante (compatibilidad con versiones anteriores)
                restaurante = Restaurante.objects.get(id=restaurantes_ids)
                platillo.restaurantes.add(restaurante)

        # Agregar ingredientes al platillo
        if 'ingredientes' in data and data['ingredientes']:
            ingredientes = data['ingredientes']
            cantidades = data.get('cantidades', [])
            unidades = data.get('unidades', [])

            for i, ingrediente_id in enumerate(ingredientes):
                try:
                    ingrediente = Ingrediente.objects.get(id=ingrediente_id)
                    cantidad = float(cantidades[i]) if i < len(cantidades) else 0
                    unidad = unidades[i] if i < len(unidades) else 'unidad'

                    IngredientePlatillo.objects.create(
                        platillo=platillo,
                        ingrediente=ingrediente,
                        cantidad=cantidad,
                        unidad=unidad
                    )
                except Ingrediente.DoesNotExist:
                    continue  # Si el ingrediente no existe, continuar con el siguiente

        # Actualizar precio total del menú
        menu.calcular_precio_total()

        return JsonResponse({
            'success': True,
            'message': 'Platillo creado exitosamente',
            'platillo': {
                'id': platillo.id,
                'nombre': platillo.nombre,
                'precio': float(platillo.precio),
                'menu': platillo.menu.nombre,
                'restaurantes': [r.name for r in platillo.restaurantes.all()],
                'num_ingredientes': platillo.ingredientes.count()
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def create_ingrediente(request):
    """Crear nuevo ingrediente"""
    try:
        data = json.loads(request.body)
        
        ingrediente = Ingrediente.objects.create(
            nombre=data['nombre'],
            precio=float(data['precio']),
            unidad=data['unidad'],
            descripcion=data.get('descripcion', ''),
            stock_disponible=float(data.get('stock_disponible', 0)),
            stock_minimo=float(data.get('stock_minimo', 0))
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Ingrediente creado exitosamente',
            'ingrediente': {
                'id': ingrediente.id,
                'nombre': ingrediente.nombre,
                'precio': float(ingrediente.precio),
                'unidad': ingrediente.get_unidad_display(),
                'stock_disponible': float(ingrediente.stock_disponible)
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def create_restaurante(request):
    """Crear nuevo restaurante"""
    try:
        data = json.loads(request.body)
        crucero = Crucero.objects.get(id=data['crucero_id'])
        
        restaurante = Restaurante.objects.create(
            name=data['nombre'],
            type=data['tipo'],
            crucero=crucero,
            capacity=int(data['capacity']),
            area_total=float(data['area_total']) if data.get('area_total') else None,
            largo=float(data.get('largo', 0)) if data.get('largo') else None,
            ancho=float(data.get('ancho', 0)) if data.get('ancho') else None,
            ubicacion=data.get('ubicacion', ''),
            descripcion=data.get('descripcion', ''),
            horario_apertura=data.get('horario_apertura') if data.get('horario_apertura') else None,
            horario_cierre=data.get('horario_cierre') if data.get('horario_cierre') else None
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Restaurante creado exitosamente',
            'restaurante': {
                'id': restaurante.id,
                'nombre': restaurante.name,
                'tipo': restaurante.get_type_display(),
                'capacidad': restaurante.capacity,
                'area_total': float(restaurante.area_total) if restaurante.area_total else None
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def add_ingrediente_to_platillo(request):
    """Agregar ingrediente a un platillo - soporta tanto ComidasPreviu como Ingrediente"""
    try:
        data = json.loads(request.body)
        platillo = Platillo.objects.get(id=data['platillo_id'])

        # Intentar obtener el ingrediente de ComidasPreviu primero
        try:
            ingrediente_prev = ComidasPreviu.objects.get(id=data['ingrediente_id'])
            # Crear un ingrediente temporal en la tabla Ingrediente para mantener consistencia
            ingrediente, created = Ingrediente.objects.get_or_create(
                nombre=ingrediente_prev.nombre,
                defaults={
                    'precio': ingrediente_prev.precio or 0,
                    'unidad': ingrediente_prev.unidad or 'unidad',
                    'descripcion': ingrediente_prev.descripcion or '',
                    'stock_disponible': ingrediente_prev.stock_disponible or 0,
                    'stock_minimo': ingrediente_prev.stock_minimo or 0
                }
            )
        except ComidasPreviu.DoesNotExist:
            # Si no está en ComidasPreviu, buscar en Ingrediente
            ingrediente = Ingrediente.objects.get(id=data['ingrediente_id'])

        ingrediente_platillo, created = IngredientePlatillo.objects.get_or_create(
            platillo=platillo,
            ingrediente=ingrediente,
            defaults={
                'cantidad': float(data['cantidad']),
                'unidad': data['unidad']
            }
        )

        if not created:
            ingrediente_platillo.cantidad = float(data['cantidad'])
            ingrediente_platillo.unidad = data['unidad']
            ingrediente_platillo.save()

        return JsonResponse({
            'success': True,
            'message': 'Ingrediente agregado al platillo exitosamente',
            'ingrediente_platillo': {
                'id': ingrediente_platillo.id,
                'ingrediente': ingrediente_platillo.ingrediente.nombre,
                'cantidad': float(ingrediente_platillo.cantidad),
                'unidad': ingrediente_platillo.get_unidad_display()
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def get_menus(request):
    """Obtener menús por restaurante"""
    restaurante_id = request.GET.get('restaurante_id')
    if restaurante_id:
        menus = Menu.objects.filter(restaurante_id=restaurante_id, activo=True)
        menus_data = [
            {
                'id': menu.id,
                'nombre': menu.nombre,
                'tipo': menu.get_tipo_display(),
                'precio_total': float(menu.precio_total)
            }
            for menu in menus
        ]
        return JsonResponse({'menus': menus_data})
    return JsonResponse({'menus': []})

def get_platillos(request):
    """Obtener platillos por menú"""
    menu_id = request.GET.get('menu_id')
    if menu_id:
        platillos = Platillo.objects.filter(menu_id=menu_id, activo=True)
        platillos_data = [
            {
                'id': platillo.id,
                'nombre': platillo.nombre,
                'precio': float(platillo.precio)
            }
            for platillo in platillos
        ]
        return JsonResponse({'platillos': platillos_data})
    return JsonResponse({'platillos': []})

def get_ingredientes(request):
    """Obtener todos los ingredientes - usa ComidasPreviu para pruebas futuras"""
    try:
        # Verificar si la tabla ComidasPreviu existe y tiene datos
        try:
            # Intentar hacer una consulta simple para verificar si la tabla existe
            ComidasPreviu.objects.count()
            # Si llega aquí, la tabla existe
            if ComidasPreviu.objects.exists():
                ingredientes = ComidasPreviu.objects.all()
                ingredientes_data = []
                for ingrediente in ingredientes:
                    # Adaptar los campos según la estructura real de comidasPreviu
                    data = {
                        'id': ingrediente.id,
                        'nombre': ingrediente.ingredientes or f"Ingrediente {ingrediente.pk}",
                        'tipo': ingrediente.tipo or '',
                        'subtipo': ingrediente.subtipo or '',
                        'clase_alimenticia': ingrediente.clase_alimenticia or '',
                        'descripcion': ingrediente.detalle or '',
                        'platos': ingrediente.platos or '',
                        'origen': ingrediente.origen or '',
                        'fuente': ingrediente.fuente or '',
                        # Campos compatibles
                        'precio': 0.0,
                        'unidad': 'unidad',
                        'stock_disponible': 0.0
                    }
                    ingredientes_data.append(data)
                return JsonResponse({'ingredientes': ingredientes_data})
            else:
                # Tabla existe pero está vacía
                print("Tabla ComidasPreviu existe pero está vacía")
        except Exception as table_error:
            # Tabla no existe o hay error de conexión
            print(f"Tabla ComidasPreviu no disponible: {table_error}")

        # Usar datos mockeados como fallback
        print("Usando datos mockeados de ComidasPreviu")
        ingredientes_data = [
            {
                'id': item['id'],
                'nombre': item['ingredientes'],
                'tipo': item['tipo'],
                'subtipo': item['subtipo'],
                'clase_alimenticia': item['clase_alimenticia'],
                'descripcion': item['detalle'],
                'platos': item['platos'],
                'origen': item['origen'],
                'fuente': item['fuente'],
                # Campos compatibles
                'precio': 0.0,
                'unidad': 'unidad',
                'stock_disponible': 0.0
            }
            for item in MOCK_INGREDIENTES_COMIDAS_PREVIA
        ]

    except Exception as e:
        # Fallback final a datos mockeados si hay cualquier error
        print(f"Error general en get_ingredientes: {e}")
        ingredientes_data = [
            {
                'id': item['id'],
                'nombre': item['ingredientes'],
                'tipo': item['tipo'],
                'subtipo': item['subtipo'],
                'clase_alimenticia': item['clase_alimenticia'],
                'descripcion': item['detalle'],
                'platos': item['platos'],
                'origen': item['origen'],
                'fuente': item['fuente'],
                'precio': 0.0,
                'unidad': 'unidad',
                'stock_disponible': 0.0
            }
            for item in MOCK_INGREDIENTES_COMIDAS_PREVIA
        ]

    return JsonResponse({'ingredientes': ingredientes_data})

def get_ingredientes_previa(request):
    """Obtener ingredientes específicamente de la tabla comidasPreviu para pruebas"""
    try:
        # Verificar si la tabla ComidasPreviu existe y tiene datos
        try:
            # Intentar hacer una consulta simple para verificar si la tabla existe
            ComidasPreviu.objects.count()
            # Si llega aquí, la tabla existe
            if ComidasPreviu.objects.exists():
                ingredientes = ComidasPreviu.objects.all()
                ingredientes_data = []

                for ingrediente in ingredientes:
                    data = {
                        'id': ingrediente.id,
                        'nombre': ingrediente.ingredientes or f"Ingrediente {ingrediente.pk}",
                        'tipo': ingrediente.tipo or '',
                        'subtipo': ingrediente.subtipo or '',
                        'clase_alimenticia': ingrediente.clase_alimenticia or '',
                        'descripcion': ingrediente.detalle or '',
                        'platos': ingrediente.platos or '',
                        'origen': ingrediente.origen or '',
                        'fuente': ingrediente.fuente or '',
                        # Campos compatibles para el frontend
                        'precio': 0.0,  # No tenemos precio en la estructura actual
                        'unidad': 'unidad',  # Default
                        'stock_disponible': 0.0  # No tenemos stock en la estructura actual
                    }
                    ingredientes_data.append(data)

                return JsonResponse({
                    'success': True,
                    'ingredientes': ingredientes_data,
                    'total': len(ingredientes_data),
                    'fuente': 'comidasPreviu_real'
                })
            else:
                # Tabla existe pero está vacía
                print("Tabla ComidasPreviu existe pero está vacía")
        except Exception as table_error:
            # Tabla no existe o hay error de conexión
            print(f"Tabla ComidasPreviu no disponible: {table_error}")

        # Usar datos mockeados como fallback
        print("Usando datos mockeados de ComidasPreviu")
        return JsonResponse({
            'success': True,
            'ingredientes': MOCK_INGREDIENTES_COMIDAS_PREVIA,
            'total': len(MOCK_INGREDIENTES_COMIDAS_PREVIA),
            'fuente': 'comidasPreviu_mock'
        })

    except Exception as e:
        # Fallback a datos mockeados
        print(f"Error general en get_ingredientes_previa: {e}")
        return JsonResponse({
            'success': True,
            'ingredientes': MOCK_INGREDIENTES_COMIDAS_PREVIA,
            'total': len(MOCK_INGREDIENTES_COMIDAS_PREVIA),
            'fuente': 'comidasPreviu_mock_fallback',
            'error_original': str(e)
        })

def diagnostico_ingredientes(request):
    """Endpoint simple para diagnosticar el estado de los ingredientes"""
    diagnostico = {
        'timestamp': '2025-09-10',
        'sistema': 'Restaurante - Ingredientes',
        'estado_django': 'OK',
        'modelos': {},
        'tablas': {},
        'recomendaciones': []
    }

    try:
        from restaurant.models import ComidasPreviu, Ingrediente
        diagnostico['modelos']['ComidasPreviu'] = 'OK'
        diagnostico['modelos']['Ingrediente'] = 'OK'
    except Exception as e:
        diagnostico['modelos']['error'] = str(e)

    # Verificar tablas
    try:
        count_previa = ComidasPreviu.objects.count()
        diagnostico['tablas']['comidasPreviu'] = {
            'registros': count_previa,
            'estado': 'OK' if count_previa >= 0 else 'ERROR'
        }
        if count_previa > 0:
            primer = ComidasPreviu.objects.first()
            diagnostico['tablas']['comidasPreviu']['primer_ingrediente'] = primer.ingredientes
    except Exception as e:
        diagnostico['tablas']['comidasPreviu'] = {
            'estado': 'ERROR',
            'error': str(e)
        }

    try:
        count_ing = Ingrediente.objects.count()
        diagnostico['tablas']['ingrediente'] = {
            'registros': count_ing,
            'estado': 'OK'
        }
    except Exception as e:
        diagnostico['tablas']['ingrediente'] = {
            'estado': 'ERROR',
            'error': str(e)
        }

    # Recomendaciones
    if diagnostico['tablas'].get('comidasPreviu', {}).get('registros', 0) == 0:
        diagnostico['recomendaciones'].append("Tabla comidasPreviu vacía - usando datos mockeados")
    else:
        diagnostico['recomendaciones'].append("Sistema funcionando con datos reales")

    diagnostico['recomendaciones'].append("Prueba: http://127.0.0.1:8000/restaurant/test-ingredientes-previa/")

    return JsonResponse(diagnostico)

def test_ingredientes_previa(request):
    """Vista de prueba para mostrar ingredientes de comidasPreviu"""
    try:
        # Verificar si la tabla ComidasPreviu existe y tiene datos
        try:
            # Intentar hacer una consulta simple para verificar si la tabla existe
            ComidasPreviu.objects.count()
            # Si llega aquí, la tabla existe
            if ComidasPreviu.objects.exists():
                ingredientes = ComidasPreviu.objects.all()[:20]  # Limitar a 20 para pruebas
                total_ingredientes = ComidasPreviu.objects.count()
                fuente = 'comidasPreviu_real'
                mensaje = f'Encontrados {total_ingredientes} ingredientes en comidasPreviu (base de datos)'
            else:
                # Tabla existe pero está vacía
                print("Tabla ComidasPreviu existe pero está vacía")
                fuente = 'comidasPreviu_vacia'
                mensaje = 'Tabla comidasPreviu existe pero está vacía'
                raise Exception("Tabla vacía")
        except Exception as table_error:
            # Tabla no existe o hay error de conexión
            print(f"Tabla ComidasPreviu no disponible: {table_error}")

            # Usar datos mockeados
            mock_data = MOCK_INGREDIENTES_COMIDAS_PREVIA

            # Convertir a objetos similares para el template
            class MockIngrediente:
                def __init__(self, data):
                    self.id = data['id']
                    self.ingredientes = data['ingredientes']
                    self.tipo = data['tipo']
                    self.subtipo = data['subtipo']
                    self.clase_alimenticia = data['clase_alimenticia']
                    self.detalle = data['detalle']
                    self.platos = data['platos']
                    self.origen = data['origen']
                    self.fuente = data['fuente']

            ingredientes = [MockIngrediente(item) for item in mock_data]
            total_ingredientes = len(mock_data)
            fuente = 'comidasPreviu_mock'
            mensaje = f'Mostrando {len(ingredientes)} ingredientes mockeados (datos de prueba)'

        context = {
            'ingredientes': ingredientes,
            'total_ingredientes': total_ingredientes,
            'fuente': fuente,
            'mensaje': mensaje
        }
        return render(request, 'restaurant/test_ingredientes.html', context)

    except Exception as e:
        # Fallback completo a datos mockeados
        print(f"Error general en test_ingredientes_previa: {e}")
        mock_data = MOCK_INGREDIENTES_COMIDAS_PREVIA

        class MockIngrediente:
            def __init__(self, data):
                self.id = data['id']
                self.ingredientes = data['ingredientes']
                self.tipo = data['tipo']
                self.subtipo = data['subtipo']
                self.clase_alimenticia = data['clase_alimenticia']
                self.detalle = data['detalle']
                self.platos = data['platos']
                self.origen = data['origen']
                self.fuente = data['fuente']

        ingredientes = [MockIngrediente(item) for item in mock_data]

        context = {
            'ingredientes': ingredientes,
            'total_ingredientes': len(mock_data),
            'fuente': 'comidasPreviu_mock_fallback',
            'mensaje': f'Datos mockeados (Error original: {str(e)})',
            'error': str(e)
        }
        return render(request, 'restaurant/test_ingredientes.html', context)