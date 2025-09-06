from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Crucero, Restaurante, MenuItem, Employee, MaintenanceItem, ConsumptionRecord

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
    """Vista para gestión de empleados"""
    # Filtrar por crucero activo desde sesión
    current_cruise_id = request.session.get('current_cruise_id') or request.GET.get('cruise')
    employees = Employee.objects.filter(active=True).select_related('restaurant')
    if current_cruise_id:
        employees = employees.filter(restaurant__crucero_id=current_cruise_id)
    restaurants = Restaurante.objects.all()
    current_cruise = None
    if current_cruise_id:
        try:
            current_cruise = Crucero.objects.get(id=current_cruise_id)
        except Crucero.DoesNotExist:
            current_cruise = None
    
    context = {
        'employees': employees,
        'restaurants': restaurants,
        'current_cruise_id': current_cruise_id,
        'current_cruise': current_cruise,
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

    # Lista auxiliar para plantillas (evitar lookup por clave variable)
    days_list = [
        {'day': d, 'items': days[d]['items'], 'total': days[d]['total']}
        for d in days_range
    ]

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
    restaurants = Restaurante.objects.all().values('id', 'name', 'type')
    # Mapear display de type
    items = []
    for r in restaurants:
        obj = Restaurante(id=r['id'], name=r['name'], type=r['type'])
        items.append({
            'id': r['id'],
            'name': r['name'],
            'type_display': obj.get_type_display()
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