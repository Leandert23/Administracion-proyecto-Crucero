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
    restaurants = Restaurante.objects.all()
    
    # Filtros
    selected_cruise = request.GET.get('cruise', '')
    selected_restaurant = request.GET.get('restaurant', '')
    
    menu_items = MenuItem.objects.all()
    if selected_cruise:
        menu_items = menu_items.filter(restaurant__crucero_id=selected_cruise)
    if selected_restaurant:
        menu_items = menu_items.filter(restaurant_id=selected_restaurant)
    
    context = {
        'cruceros': cruceros,
        'restaurants': restaurants,
        'menu_items': menu_items,
        'selected_cruise': selected_cruise,
        'selected_restaurant': selected_restaurant,
    }
    return render(request, 'restaurant/stock.html', context)

def employees_view(request):
    """Vista para gestión de empleados"""
    employees = Employee.objects.filter(active=True).select_related('restaurant')
    restaurants = Restaurante.objects.all()
    
    context = {
        'employees': employees,
        'restaurants': restaurants,
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
    
    context = {
        'cruceros': cruceros,
        'restaurants': restaurants,
    }
    return render(request, 'restaurant/consumption.html', context)

def records_view(request):
    """Vista para registros de consumo"""
    selected_cruise = request.GET.get('cruise', '')
    
    consumption_records = ConsumptionRecord.objects.all().select_related('menu_item__restaurant')
    if selected_cruise:
        consumption_records = consumption_records.filter(menu_item__restaurant__crucero_id=selected_cruise)
    
    cruceros = Crucero.objects.all()
    
    context = {
        'consumption_records': consumption_records,
        'cruceros': cruceros,
        'selected_cruise': selected_cruise,
    }
    return render(request, 'restaurant/records.html', context)

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