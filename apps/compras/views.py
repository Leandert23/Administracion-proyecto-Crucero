from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import CompraLote
from ..cruceros.models import Crucero
from django.dispatch import Signal

# Vista para ver detalles de una compra por lote
def detalle_compra_lote_view(request, crucero_id, compra_id):
    compra = get_object_or_404(CompraLote, id=compra_id, crucero_id=crucero_id)

    from_param = request.GET.get('from', '')

    # Manejo de acciones POST
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aceptar':
            compra.estado = 'Esperando por revision'
            lote_signal = Signal()
            lote_signal.send(sender=None, compra_lote=compra)
            compra.save()
        elif accion == 'rechazar':
            mensaje = request.POST.get('mensaje', '')
            compra.estado = 'cancelada'
            solicitud = compra.solicitud
            if solicitud and solicitud.procesada:
                compra.notas_compra = mensaje
                solicitud.procesada = False
                solicitud.save()
            compra.save()
        # elif accion == 'finalizar':
        #     compra.estado = 'exitosa'
        #     compra.save()
        # Redirigir a la misma página para ver el cambio reflejado
        from django.shortcuts import redirect
        return redirect('detalle_compra_lote', crucero_id=crucero_id, compra_id=compra.id)

    return render(request, 'detalle_compra_lote.html', {'compra': compra, 'from_param': from_param, 'crucero_id': crucero_id})


# Vista para listar compras por lote registradas
def compras_lote_registradas_view(request, crucero_id):
    from .models import CompraLote
    crucero = Crucero.objects.get(pk=crucero_id)
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
                        procesada=False,
                        crucero = crucero
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
    compras = CompraLote.objects.filter(crucero_id=crucero_id).exclude(estado='exitosa').order_by('-fecha')
    return render(request, 'compras_lote_registradas.html', {'compras': compras, 'crucero_id': crucero_id})

# Vista para historial de compras por lote
def historial_compras_lote_view(request, crucero_id):
    from .models import CompraLote
    compras = CompraLote.objects.filter(crucero_id=crucero_id, estado__in=['exitosa', 'defectuosa']).order_by('-fecha')
    return render(request, 'historial_compras_lote.html', {'compras': compras, 'crucero_id': crucero_id})
from django.views.decorators.csrf import csrf_protect

# Vista para procesar materiales de una solicitud específica
@csrf_protect
def procesar_materiales_solicitud_view(request, crucero_id, solicitud_id):
    from .models import SolicitudSubtipo, SolicitudSubtipoItem, Proveedores, CompraLote, CompraLoteItem
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    materiales = solicitud.items.all()
    proveedores = Proveedores.objects.filter(tipo=solicitud.tipo, subtipo=solicitud.subtipo)
    crucero = Crucero.objects.get(pk=crucero_id)

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
            crucero = crucero
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
    # Importar la señal compartida para que el receiver en almacen.signals.py la reciba
        # from ..almacen.signals import lote_signal
        # lote_signal.send(sender=None, compra_lote=compra_lote)

        compra_lote.estado = 'registrada'

        solicitud.procesada = True
        solicitud.save()
        compra_lote.save()
        return redirect('lista_solicitudes', crucero_id=crucero_id)
    return render(request, 'procesar_materiales_solicitud.html', {
        'solicitud': solicitud,
        'materiales': materiales,
        'proveedores': proveedores,
        'puertos_disponibles': puertos_disponibles,
        'proveedor_id': proveedor_id,
        'crucero_id': crucero_id,
    })
# Importar los nuevos modelos de solicitud
from .models import SolicitudSubtipo, SolicitudSubtipoItem
from django.http import HttpResponseRedirect
from django.urls import reverse

# View para mostrar detalles de una solicitud agrupada por subtipo
def detalle_solicitud_view(request, crucero_id, solicitud_id):
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    return render(request, 'detalle_solicitud.html', {
        'solicitud': solicitud,
        'tipo': solicitud.tipo,
        'subtipo': solicitud.subtipo,
        'items': solicitud.items.all(),
        'crucero_id': crucero_id,
    })


# View para procesar una solicitud agrupada por subtipo
def procesar_solicitud_view(request, crucero_id, solicitud_id):
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    if request.method == 'POST':
        solicitud.procesada = True
        solicitud.save()
        return HttpResponseRedirect(reverse('lista_solicitudes', args=[crucero_id]))
    return HttpResponseRedirect(reverse('lista_solicitudes', args=[crucero_id]))
# Vista para mostrar compras registradas


from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from .models import Proveedores
from .forms import ProveedorForm

# View para registrar una solicitud agrupada por subtipo
@csrf_protect
def registrar_solicitud_compra_view(request, crucero_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body.decode('utf-8'))
        tipo = data.get('tipo')
        subtipo = data.get('subtipo')
        productos = data.get('productos', [])
        crucero = Crucero.objects.get(pk=crucero_id)
        solicitud = SolicitudSubtipo.objects.create(tipo=tipo, subtipo=subtipo, crucero = crucero)
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
        return redirect('lista_solicitudes', crucero_id=crucero_id)
    return render(request, 'solicitud_compra_form.html', {'crucero_id': crucero_id})


# View para listar solicitudes agrupadas por subtipo
def lista_solicitudes_view(request, crucero_id):
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
    solicitudes = SolicitudSubtipo.objects.filter(procesada=False, crucero_id=crucero_id).order_by('-id')
    #### Revisar estados
    compras_lote = CompraLote.objects.filter(crucero_id=crucero_id).exclude(estado__in=['exitosa', 'defectuosa', 'cancelada']).order_by('-fecha')
    return render(request, 'lista_solicitudes.html', {'solicitudes': solicitudes, 'compras_lote': compras_lote, 'crucero_id': crucero_id})


@csrf_protect
def dashboard_view(request, crucero_id):
    crucero = Crucero.objects.get(pk=crucero_id)
    return render(request, 'index.html', {'crucero': crucero, "crucero_id":crucero_id})

@csrf_protect
def proveedores_view(request, crucero_id):
    import json
    from .models import Paises, CompraLote
    SUBTIPOS_POR_TIPO = {
        "ALIMENTOS_FRESCOS": {"FRUTA","VERDURA","CARNE","PESCADO","MARISCO","LACTEOS","PANIFICADOS","CHARCUTERIA"},
        "ALIMENTOS_SECOS": {"CEREAL","PASTA","LEGUMINOSAS","ENLATADOS","SNACKS","CONDIMENTOS","AZUCAR_SAL"},
        "BEBIDAS": {"AGUA","REFRESCO","JUGO","ENERGETICA","CAFE_TEA","CERVEZA","VINO","DESTILADO","COCTEL_PREMEZCLA"},
        "INSUMOS_COCINA": {"DESCARTABLES","ENVASES","UTENSILIOS","GAS_COCINA","HIELO"},
        "LIMPIEZA": {"DETERGENTES","DESINFECTANTES","UTENSILIOS_LIMPIEZA","PAPEL_SANITARIO","AMBIENTADORES"},
        "SUMINISTROS_MEDICOS": {"MEDICAMENTO","CURACION","EQUIPO_DIAGNOSTICO","EPP","INSTRUMENTAL","SOLUCION_IV"},
        "MANTENIMIENTO": {"PINTURA","LUBRICANTE","SELLADOR","ADHESIVO","ABRASIVO","FILTRO","ACEITE"},
        "REPUESTOS_TECNICOS": {"MOTOR","ELECTRICO","HVAC","NAVEGACION","ILUMINACION","BOMBAS","VALVULAS"},
        "EQUIPOS": {"ELECTRODOMESTICO","AUDIO_VIDEO","INFORMATICO","GIMNASIO","COCINA_INDUSTRIAL"},
        "TEXTILES": {"ROPA_CAMA","TOALLA","UNIFORME","CORTINA","TAPICERIA"},
        "OFICINA": {"PAPELERIA","IMPRESION","ESCRITORIO","CONSUMIBLE_IT"},
        "ENTRETENIMIENTO": {"JUEGO_MESA","JUEGO_VIDEO","LIBRO_REVISTA","EVENTO","SONIDO_LUZ"},
        "SPA_GYM": {"COSMETICO","ACEITE_MASAJE","SUPLEMENTO","ACC_FITNESS"},
        "SEGURIDAD": {"CHALECO_SALVAVIDAS","EXTINTOR","SENALIZACION","ARNES","BOTIQUIN","DETECTOR"},
        "MERCHANDISING": {"RECUERDO","PRENDA_LOGO","ACCESORIO_LOGO","BEBIDA_PREMIUM","DULCE_GOURMET"},
        "TECNOLOGIA": {"ROUTER","SWITCH","CABLEADO","CAMARA_SEGURIDAD","SENSOR","DISPOSITIVO_PORTATIL"},
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
                return redirect('proveedores', crucero_id=crucero_id)
    else:
        form = ProveedorForm()
    proveedores = Proveedores.objects.all()
    # IDs de proveedores bloqueados (asignados a cualquier CompraLote)
    proveedores_bloqueados = set(CompraLote.objects.filter(crucero_id=crucero_id).values_list('proveedor_id', flat=True))
    return render(request, 'proveedores.html', {
        'form': form,
        'proveedores': proveedores,
        'SUBTIPOS_POR_TIPO': SUBTIPOS_POR_TIPO,
        'tipo_seleccionado': tipo_seleccionado,
        'proveedores_bloqueados': proveedores_bloqueados,
        'crucero_id': crucero_id,
    })

@csrf_protect
def eliminar_proveedor(request, crucero_id):
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
    return redirect('proveedores', crucero_id=crucero_id)

def historial_compras_view(request, crucero_id):
    from .models import CompraLote
    crucero = Crucero.objects.get(pk=crucero_id)
    compras_lote = CompraLote.objects.filter(estado__in=['exitosa', 'defectuosa', 'cancelada'], crucero=crucero).order_by('-fecha')
    return render(request, 'historial_compras.html', {'compras_lote': compras_lote, "crucero_id":crucero_id})