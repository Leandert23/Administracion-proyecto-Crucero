from .models import (
    Crucero, Restaurante, MenuItem, Employee, MaintenanceItem, ConsumptionRecord,
    ServiceInvoice, ServiceInvoiceItem, BuffetBulkRecord,
    RestaurantIngredientes, RestaurantMenuDia1, RestaurantMenuDia2, RestaurantMenuDia3,
    RestaurantMenuDia4, RestaurantMenuDia5, RestaurantMenuDia6, RestaurantMenuDia7,
    RestaurantItaliano, RestaurantArabe, RestaurantVinos, RestaurantCartaEspecial,
    RestaurantMenuFijo, RestaurantBuffet, RestaurantProducts,
)
from django.contrib import admin

@admin.register(Crucero)
class CruceroAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'crucero', 'capacity', 'created_at']
    list_filter = ['type', 'crucero']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'quantity', 'price', 'included', 'low_stock']
    list_filter = ['restaurant', 'included', 'restaurant__crucero']
    search_fields = ['name', 'description']
    
    def low_stock(self, obj):
        return obj.quantity < 10
    low_stock.boolean = True
    low_stock.short_description = 'Stock Bajo'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'shift', 'restaurant', 'active', 'hire_date']
    list_filter = ['position', 'shift', 'restaurant', 'active']
    search_fields = ['name', 'email']
    date_hierarchy = 'hire_date'

@admin.register(MaintenanceItem)
class MaintenanceItemAdmin(admin.ModelAdmin):
    list_display = ['area', 'priority', 'status', 'restaurant', 'reported_by', 'created_at']
    list_filter = ['area', 'priority', 'status', 'restaurant']
    search_fields = ['description', 'reported_by']
    date_hierarchy = 'created_at'

@admin.register(ConsumptionRecord)
class ConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'cruise_day', 'quantity', 'total_price', 'is_included', 'created_at']
    list_filter = ['cruise_day', 'is_included', 'menu_item__restaurant']
    search_fields = ['menu_item__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['unit_price', 'total_price', 'is_included']

class ServiceInvoiceItemInline(admin.TabularInline):
    model = ServiceInvoiceItem
    extra = 1
    readonly_fields = ['line_total']

@admin.register(ServiceInvoice)
class ServiceInvoiceAdmin(admin.ModelAdmin):
    list_display = ['code', 'restaurant', 'room_number', 'date', 'total_amount']
    search_fields = ['code', 'room_number']
    list_filter = ['restaurant', 'date']
    date_hierarchy = 'date'
    inlines = [ServiceInvoiceItemInline]
    readonly_fields = ['code', 'total_amount', 'created_at']

@admin.register(BuffetBulkRecord)
class BuffetBulkRecordAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'date', 'platillo', 'quantity']
    list_filter = ['restaurant', 'date']
    search_fields = ['platillo__nombre']
    date_hierarchy = 'date'

# Registros simples para las tablas importadas de la BD
@admin.register(RestaurantIngredientes)
class RestaurantIngredientesAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingredientes', 'tipo', 'subtipo', 'clase_alimenticia']
    search_fields = ['ingredientes', 'tipo', 'subtipo', 'clase_alimenticia']

for model in [
    RestaurantMenuDia1, RestaurantMenuDia2, RestaurantMenuDia3, RestaurantMenuDia4,
    RestaurantMenuDia5, RestaurantMenuDia6, RestaurantMenuDia7, RestaurantItaliano,
    RestaurantArabe, RestaurantVinos, RestaurantCartaEspecial, RestaurantMenuFijo,
    RestaurantBuffet, RestaurantProducts
]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass