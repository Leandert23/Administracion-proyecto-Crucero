from django.contrib import admin
from .models import (
	CompraLote,
	CompraLoteItem,
	SolicitudSubtipo,
	SolicitudSubtipoItem,
	Material,
	ProveedorMaterial,
	Paises,
	Proveedores,
)

admin.site.register(CompraLote)
admin.site.register(CompraLoteItem)
admin.site.register(SolicitudSubtipo)
admin.site.register(SolicitudSubtipoItem)
admin.site.register(Material)
admin.site.register(ProveedorMaterial)
admin.site.register(Paises)
admin.site.register(Proveedores)
