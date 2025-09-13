from django.contrib import admin
from .models import ProductoBar, Menu, Categoria, Bar, Pedidos, DetallePedido, IngredienteReceta


@admin.register(ProductoBar)
class ProductoBarAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "plan", "precio_vta", "categoria", "tipo_almacen", "subtipo_almacen", "creado_en")
	list_filter = ("plan", "categoria", "tipo_almacen", "subtipo_almacen")
	search_fields = ("nombre", "categoria")
	fields = ("nombre", "plan", "precio_vta", "categoria", "tipo_almacen", "subtipo_almacen", "receta")


class IngredienteRecetaInline(admin.TabularInline):
	model = IngredienteReceta
	extra = 1
	autocomplete_fields = ('ingrediente',)


@admin.register(IngredienteReceta)
class IngredienteRecetaAdmin(admin.ModelAdmin):
	list_display = ("producto_bar", "ingrediente", "cantidad", "unidad")
	search_fields = ("producto_bar__nombre", "ingrediente__nombre")


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "precio_vta", "categoria")
	search_fields = ("nombre",)
	list_filter = ("categoria",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "descripcion")
	search_fields = ("nombre",)


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
	list_display = ("id", "nombre", "ubicacion", "hora_aper", "hora_cierre")
	search_fields = ("nombre",)
	list_filter = ("ubicacion",)


@admin.register(Pedidos)
class PedidosAdmin(admin.ModelAdmin):
	list_display = ("id", "empleado", "cliente", "estado", "fecha_hora", "lugarentrega")
	list_filter = ("estado", "lugarentrega")
	search_fields = ("id",)


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
	list_display = ("id", "pedido", "producto", "cantidad")
	list_filter = ("producto",)
