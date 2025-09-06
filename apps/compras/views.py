from django.shortcuts import get_object_or_404
# Vista para ver detalles de una compra por lote
def detalle_compra_lote_view(request, compra_id):
    from .models import CompraLote
    compra = get_object_or_404(CompraLote, id=compra_id)
    from_param = request.GET.get('from', '')
    return render(request, 'detalle_compra_lote.html', {'compra': compra, 'from_param': from_param})
# Vista para listar compras por lote registradas
def compras_lote_registradas_view(request):
    from .models import CompraLote
    if request.method == 'POST':
        compralote_id = request.POST.get('compralote_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        if compralote_id and nuevo_estado:
            try:
                compra = CompraLote.objects.get(id=compralote_id)
                compra.estado = nuevo_estado
                compra.save()
                if nuevo_estado == 'cancelada':
                    print('DEBUG: Entrando a cancelación de compra lote', compra.id)
                    from .models import SolicitudSubtipo, SolicitudSubtipoItem
                    nueva_solicitud = SolicitudSubtipo.objects.create(
                        tipo=compra.proveedor.tipo,
                        subtipo=compra.proveedor.subtipo,
                        procesada=False
                    )
                    print('DEBUG: Solicitud creada', nueva_solicitud.id)
                    for item in compra.items.all():
                        SolicitudSubtipoItem.objects.create(
                            solicitud=nueva_solicitud,
                            producto_id=item.producto_id,
                            nombre=item.nombre,
                            cantidad_a_comprar=item.cantidad,
                            medida=item.medida,
                            tipo=compra.proveedor.tipo,
                            subtipo=compra.proveedor.subtipo
                        )
                        print('DEBUG: Item añadido', item.nombre)
                    compra.delete()
                    print('DEBUG: Compra lote eliminada')
                    from django.shortcuts import redirect
                    return redirect('lista_solicitudes')
                elif nuevo_estado in ['exitosa', 'defectuosa']:
                    from django.shortcuts import redirect
                    return redirect('historial_compras_lote')
            except CompraLote.DoesNotExist:
                pass
    # Excluir las exitosas del listado de registradas
    compras = CompraLote.objects.exclude(estado='exitosa').order_by('-fecha')
    return render(request, 'compras_lote_registradas.html', {'compras': compras})

# Vista para historial de compras por lote
def historial_compras_lote_view(request):
    from .models import CompraLote
    compras = CompraLote.objects.filter(estado__in=['exitosa', 'defectuosa']).order_by('-fecha')
    return render(request, 'historial_compras_lote.html', {'compras': compras})
from django.views.decorators.csrf import csrf_protect

# Vista para procesar materiales de una solicitud específica
@csrf_protect
def procesar_materiales_solicitud_view(request, solicitud_id):
    from .models import SolicitudSubtipo, SolicitudSubtipoItem, Proveedores, CompraLote, CompraLoteItem
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    materiales = solicitud.items.all()
    proveedores = Proveedores.objects.filter(tipo=solicitud.tipo, subtipo=solicitud.subtipo)

    # Puertos y países asociados
    PUERTOS_POR_PAIS = {
        'Panamá': ['Colón, Panamá'],
        'Colombia': ['Cartagena, Colombia'],
        'Aruba': ['Oranjestad, Aruba'],
        'Bonaire': ['Kralendijk, Bonaire'],
        'Curazao': ['Willemstad, Curazao'],
    }

    puertos_disponibles = []
    proveedor_paises = []
    proveedor_id = request.POST.get('proveedor_id') or request.GET.get('proveedor_id')
    proveedor_seleccionado = None
    if proveedor_id:
        try:
            proveedor_seleccionado = Proveedores.objects.get(id=proveedor_id)
            proveedor_paises = [p.nombre for p in proveedor_seleccionado.countries.all()]
            for pais in proveedor_paises:
                puertos_disponibles.extend(PUERTOS_POR_PAIS.get(pais, []))
        except Proveedores.DoesNotExist:
            pass
    if not puertos_disponibles:
        # Si no hay proveedor seleccionado, mostrar todos los puertos
        for lista in PUERTOS_POR_PAIS.values():
            puertos_disponibles.extend(lista)

    if request.method == 'POST' and proveedor_seleccionado:
        presupuesto_lote = request.POST.get('presupuesto_lote') or 0
        compra_lote = CompraLote.objects.create(
            empresa_nombre=request.POST.get('empresa_nombre', ''),
            empresa_contacto=request.POST.get('empresa_contacto', ''),
            empresa_ubicacion=request.POST.get('empresa_ubicacion', ''),
            proveedor=proveedor_seleccionado,
            puerto_entrega=request.POST.get('puerto_entrega', ''),
            notas_compra=request.POST.get('notas_compra', ''),
            presupuesto_lote=presupuesto_lote,
            estado='registrada',
            solicitud=solicitud,
        )
        for item in materiales:
            cantidad = request.POST.get(f'cantidad_{item.id}')
            CompraLoteItem.objects.create(
                compra_lote=compra_lote,
                producto_id=item.producto_id,
                nombre=item.nombre,
                medida=item.medida,
                cantidad=cantidad or 0
            )
        # Enviar signal a administración, descomentar
        # solicitud_compra_administracion(id=solicitud.id, monto=presupuesto_lote)
        from django.dispatch import Signal
        compra_lote.estado = 'En espera por revisión'
        lote_signal = Signal()
        lote_signal.send(sender=None, compra_lote=compra_lote)
        solicitud.procesada = True
        solicitud.save()
        return redirect('lista_solicitudes')
    return render(request, 'procesar_materiales_solicitud.html', {
        'solicitud': solicitud,
        'materiales': materiales,
        'proveedores': proveedores,
        'puertos_disponibles': puertos_disponibles,
        'proveedor_id': proveedor_id,
    })
# Importar los nuevos modelos de solicitud
from .models import SolicitudSubtipo, SolicitudSubtipoItem
from django.http import HttpResponseRedirect
from django.urls import reverse

# View para mostrar detalles de una solicitud agrupada por subtipo
def detalle_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    return render(request, 'detalle_solicitud.html', {
        'solicitud': solicitud,
        'tipo': solicitud.tipo,
        'subtipo': solicitud.subtipo,
        'items': solicitud.items.all()
    })


# View para procesar una solicitud agrupada por subtipo
def procesar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    if request.method == 'POST':
        solicitud.procesada = True
        solicitud.save()
        return HttpResponseRedirect(reverse('lista_solicitudes'))
    return HttpResponseRedirect(reverse('lista_solicitudes'))
# Vista para mostrar compras registradas

def compras_registradas_view(request):
    from .models import Compra
    if request.method == 'POST':
        compra_id = request.POST.get('compra_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        if compra_id and nuevo_estado:
            try:
                compra = Compra.objects.get(id=compra_id)
                compra.estado = nuevo_estado
                compra.save()
            except Compra.DoesNotExist:
                pass
    compras = Compra.objects.exclude(estado__in=['exitosa', 'cancelada']).order_by('-fecha')
    return render(request, 'compras_registradas.html', {'compras': compras})
import json
from .models import Compra, CompraPorProveedor, ProveedorMaterial
# Vista para registrar una compra

def registrar_compra_view(request):
    from .models import Proveedores, Material
    proveedores = Proveedores.objects.all()
    # Construir diccionario de materiales por proveedor para JS
    proveedor_materiales = {}
    proveedor_paises = {}
    for proveedor in proveedores:
        mats = ProveedorMaterial.objects.filter(proveedor=proveedor)
        proveedor_materiales[proveedor.id] = [
            {'id': m.material.id, 'nombre': m.material.nombre, 'costo': float(m.costo_unidad)} for m in mats
        ]
        proveedor_paises[proveedor.id] = [
            {'id': pais.id, 'nombre': pais.nombre} for pais in proveedor.countries.all()
        ]
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        pais_id = request.POST.get('pais_entrega')
        sitio_llegada = request.POST.get('sitio_llegada')
        proveedor = Proveedores.objects.get(id=proveedor_id)
        pais = None
        if pais_id:
            from .models import Paises
            pais = Paises.objects.get(id=pais_id)
        # Crear la compra principal
        compra = Compra.objects.create(
            pais_entrega=pais,
            sitio_llegada=sitio_llegada
        )
        # Crear el registro de compra por proveedor
        descripcion = request.POST.get('descripcion', '')
        compra_proveedor = CompraPorProveedor.objects.create(
            compra=compra,
            proveedor=proveedor,
            descripcion=descripcion
        )
        # Procesar materiales dinámicos
        materiales_data = []
        for key in request.POST:
            if key.startswith('material_'):
                idx = key.split('_')[1]
                try:
                    material_id = request.POST.get(f'material_{idx}')
                    unidad = request.POST.get(f'unidad_{idx}')
                    cantidad = float(request.POST.get(f'cantidad_{idx}', '0'))
                    precio_unitario = float(request.POST.get(f'precio_unitario_{idx}', '0'))
                    total = cantidad * precio_unitario
                    materiales_data.append({
                        'material_id': material_id,
                        'unidad': unidad,
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario,
                        'total': total
                    })
                except Exception:
                    continue
        from .models import Material, CompraPorProveedorMaterial
        for mat in materiales_data:
            material = Material.objects.get(id=mat['material_id'])
            CompraPorProveedorMaterial.objects.create(
                compra_por_proveedor=compra_proveedor,
                material=material,
                unidad=mat['unidad'],
                cantidad=mat['cantidad'],
                precio_unitario=mat['precio_unitario'],
                total=mat['total']
            )
        return redirect('dashboard')
    return render(request, 'registrar_compra.html', {
        'proveedores': proveedores,
        'proveedor_materiales_json': json.dumps(proveedor_materiales),
        'proveedor_paises_json': json.dumps(proveedor_paises)
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from .models import Proveedores, Paises, Material
from .forms import ProveedorForm



# View para registrar una solicitud agrupada por subtipo
@csrf_protect
def registrar_solicitud_compra_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body.decode('utf-8'))
        tipo = data.get('tipo')
        subtipo = data.get('subtipo')
        productos = data.get('productos', [])
        solicitud = SolicitudSubtipo.objects.create(tipo=tipo, subtipo=subtipo)
        for prod in productos:
            SolicitudSubtipoItem.objects.create(
                solicitud=solicitud,
                producto_id=prod['id'],
                nombre=prod['nombre'],
                cantidad_a_comprar=prod['cantidad_ideal'] - prod['cantidad'],
                medida=prod['medida'],
                tipo=tipo,
                subtipo=subtipo
            )
        return redirect('lista_solicitudes')
    return render(request, 'solicitud_compra_form.html')


# View para listar solicitudes agrupadas por subtipo
def lista_solicitudes_view(request):
    from .models import CompraLote
    if request.method == 'POST':
        compralote_id = request.POST.get('compralote_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        if compralote_id and nuevo_estado:
            try:
                from .models import CompraLote
                compra = CompraLote.objects.get(id=compralote_id)
                compra.estado = nuevo_estado
                compra.save()
            except CompraLote.DoesNotExist:
                pass
    solicitudes = SolicitudSubtipo.objects.filter(procesada=False).order_by('-id')
    #### Revisar estados
    compras_lote = CompraLote.objects.exclude(estado__in=['exitosa', 'defectuosa', 'cancelada']).order_by('-fecha')
    return render(request, 'lista_solicitudes.html', {'solicitudes': solicitudes, 'compras_lote': compras_lote})


@csrf_protect
def dashboard_view(request):
    return render(request, 'index.html')

@csrf_protect
def proveedores_view(request):
    import json
    from .models import ProveedorMaterial, Material, Paises, CompraLote
    SUBTIPOS_POR_TIPO = {
        'COMIDA': [
            ('CADUCABLE', 'Caducable'),
            ('NO_CADUCABLE', 'No caducable'),
            ('REFRIGERADO', 'Refrigerado'),
            ('NO_REFRIGERADO', 'No refrigerado'),
            ('BEBIDA', 'Bebida'),
            ('LICOR', 'Licor'),
        ],
        'BIENES': [
            ('REPUESTOS', 'Repuestos'),
            ('LIMPIEZA', 'Materiales de limpieza'),
            ('MEDICOS', 'Materiales médicos'),
            ('ACTIVOS', 'Bienes activos'),
        ]
    }
    tipo_seleccionado = None
    if request.method == 'POST':
        tipo_seleccionado = request.POST.get('tipo', None)
        form = ProveedorForm(request.POST)
        paises_json = request.POST.get('paises_json', '[]')
        if paises_json.strip() == '':
            paises_nombres = []
        else:
            paises_nombres = json.loads(paises_json)
        # Solo guardar si el submit fue por el botón Registrar
        if request.POST.get('action') == 'Registrar':
            if form.is_valid():
                proveedor = form.save(commit=False)
                proveedor.save()
                # Guardar países
                paises_objs = [Paises.objects.get_or_create(nombre=nombre)[0] for nombre in paises_nombres]
                proveedor.countries.set(paises_objs)
                return redirect('proveedores')
    else:
        form = ProveedorForm()
    proveedores = Proveedores.objects.all()
    # IDs de proveedores bloqueados (asignados a cualquier CompraLote)
    proveedores_bloqueados = set(CompraLote.objects.values_list('proveedor_id', flat=True))
    return render(request, 'proveedores.html', {
        'form': form,
        'proveedores': proveedores,
        'SUBTIPOS_POR_TIPO': SUBTIPOS_POR_TIPO,
        'tipo_seleccionado': tipo_seleccionado,
        'proveedores_bloqueados': proveedores_bloqueados,
    })

@csrf_protect
def eliminar_proveedor(request):
    from .models import CompraLote
    from django.contrib import messages
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        if not proveedor_id:
            return redirect('proveedores')
        proveedor = get_object_or_404(Proveedores, id=proveedor_id)
        # Validar si el proveedor está asignado a una compra lote activa
        compras_lote = CompraLote.objects.filter(proveedor=proveedor, estado__in=['registrada', 'espera_revision'])
        if compras_lote.exists():
            messages.error(request, 'No se puede eliminar el proveedor porque está asignado a una compra registrada o en espera por revisión.')
            return redirect('proveedores')
        proveedor.countries.clear()
        proveedor.delete()
    return redirect('proveedores')
def historial_compras_view(request):
    from .models import Compra, CompraLote
    compras = Compra.objects.filter(estado__in=['exitosa', 'cancelada']).order_by('-fecha')
    compras_lote = CompraLote.objects.filter(estado__in=['exitosa', 'defectuosa', 'cancelada']).order_by('-fecha')
    return render(request, 'historial_compras.html', {'compras': compras, 'compras_lote': compras_lote})