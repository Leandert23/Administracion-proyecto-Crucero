from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ModuloSistema, Rol, Empleado


class EmpleadoAdmin(BaseUserAdmin):
	model = Empleado
	list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'crucero', 'is_staff', 'is_active')
	list_filter = ('is_staff', 'is_superuser', 'is_active', 'rol', 'crucero')
	search_fields = ('username', 'email', 'first_name', 'last_name')
	ordering = ('username',)

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
	('Personal info', {'fields': ('first_name', 'last_name', 'email', 'telefono', 'fecha_contratacion', 'crucero')}),
	('Role & permissions', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'fecha_ultimo_acceso', 'date_joined')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'first_name', 'last_name', 'rol', 'crucero', 'password1', 'password2', 'is_active', 'is_staff'),
		}),
	)



class RolAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'activo')
	search_fields = ('nombre',)
	list_filter = ('activo',)
	# Mostrar modulos por su codigo legible
	filter_horizontal = ('modulos_acceso',)


class ModuloSistemaAdmin(admin.ModelAdmin):
	list_display = ('codigo', 'activo')
	search_fields = ('codigo',)
	list_filter = ('activo',)


admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(ModuloSistema, ModuloSistemaAdmin)
