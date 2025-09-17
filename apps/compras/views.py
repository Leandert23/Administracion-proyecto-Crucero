from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import CompraLote
from ..creador_embarcaciones.models import Embarcacion
from django.dispatch import Signal

# Vista para ver detalles de una compra por lote
def detalle_compra_lote_view(request, embarcacion_id, compra_id):
    compra = get_object_or_404(CompraLote, id=compra_id, embarcacion_id=embarcacion_id)

    from_param = request.GET.get('from', '')

    # Manejo de acciones POST
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aceptar':
            compra.estado = 'Esperando por revision'
            from ..almacen.signals import lote_signal
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
        elif accion == 'aceptar_defectuosa':
            monto_a_devolver = request.POST.get('monto_a_devolver')
            if monto_a_devolver:
                compra.estado = 'Esperando por revision'
                from ..almacen.signals import lote_signal
                lote_signal.send(sender=None, compra_lote=compra)
                from .signals import manejar_compra_defectuosa
                manejar_compra_defectuosa(id=compra.id, monto=monto_a_devolver, mensaje='')
                compra.save()
        elif accion == 'rechazar_defectuosa':
            mensaje = request.POST.get('mensaje')
            if mensaje:
                compra.estado = 'cancelada'
                solicitud = compra.solicitud
                if solicitud and solicitud.procesada:
                    compra.notas_compra = mensaje
                    solicitud.procesada = False
                    solicitud.save()
                from .signals import manejar_compra_defectuosa
                manejar_compra_defectuosa(id=compra.id, monto=compra.presupuesto_lote, mensaje=mensaje)
                compra.save()
        # elif accion == 'finalizar':
        #     compra.estado = 'exitosa'
        #     compra.save()
        # Redirigir a la misma página para ver el cambio reflejado
        return redirect('compras:detalle_compra_lote', embarcacion_id=embarcacion_id, compra_id=compra.id)

    return render(request, 'detalle_compra_lote.html', {'compra': compra, 'from_param': from_param, 'embarcacion_id': embarcacion_id})


# Vista para listar compras por lote registradas
def compras_lote_registradas_view(request, embarcacion_id):
    from .models import CompraLote
    embarcacion = Embarcacion.objects.get(pk=embarcacion_id)
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
                        embarcacion = embarcacion
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
                    return redirect('compras:lista_solicitudes')
                elif nuevo_estado in ['exitosa', 'defectuosa']:
                    from django.shortcuts import redirect
                    return redirect('compras:historial_compras_lote')
            except CompraLote.DoesNotExist:
                pass
    # Excluir las exitosas del listado de registradas
    compras = CompraLote.objects.filter(embarcacion_id=embarcacion_id).exclude(estado='exitosa').order_by('-fecha')
    return render(request, 'compras_lote_registradas.html', {'compras': compras, 'embarcacion_id': embarcacion_id})

# Vista para historial de compras por lote
def historial_compras_lote_view(request, embarcacion_id):
    from .models import CompraLote
    compras = CompraLote.objects.filter(embarcacion_id=embarcacion_id, estado__in=['exitosa', 'defectuosa']).order_by('-fecha')
    return render(request, 'historial_compras_lote.html', {'compras': compras, 'embarcacion_id': embarcacion_id})
from django.views.decorators.csrf import csrf_protect

# Vista para procesar materiales de una solicitud específica
@csrf_protect
def procesar_materiales_solicitud_view(request, embarcacion_id, solicitud_id):
    from .models import SolicitudSubtipo, SolicitudSubtipoItem, Proveedores, CompraLote, CompraLoteItem
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    materiales = solicitud.items.all()
    proveedores = Proveedores.objects.filter(tipo=solicitud.tipo, subtipo=solicitud.subtipo)
    embarcacion = Embarcacion.objects.get(pk=embarcacion_id)

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
            embarcacion = embarcacion
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

        # Enviar signal a almacen para que el receiver en almacen.signals.py la reciba
        from ..almacen.signals import lote_signal
        lote_signal.send(sender=None, compra_lote=compra_lote)

        compra_lote.estado = 'registrada'

        solicitud.procesada = True
        solicitud.save()
        compra_lote.save()
        return redirect('compras:lista_solicitudes', embarcacion_id=embarcacion_id)
    return render(request, 'procesar_materiales_solicitud.html', {
        'solicitud': solicitud,
        'materiales': materiales,
        'proveedores': proveedores,
        'puertos_disponibles': puertos_disponibles,
        'proveedor_id': proveedor_id,
        'embarcacion_id': embarcacion_id,
    })
# Importar los nuevos modelos de solicitud
from .models import SolicitudSubtipo, SolicitudSubtipoItem
from django.http import HttpResponseRedirect
from django.urls import reverse

# View para mostrar detalles de una solicitud agrupada por subtipo
def detalle_solicitud_view(request, embarcacion_id, solicitud_id):
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    return render(request, 'detalle_solicitud.html', {
        'solicitud': solicitud,
        'tipo': solicitud.tipo,
        'subtipo': solicitud.subtipo,
        'items': solicitud.items.all(),
        'embarcacion_id': embarcacion_id,
    })


# View para procesar una solicitud agrupada por subtipo
def procesar_solicitud_view(request, embarcacion_id, solicitud_id):
    solicitud = get_object_or_404(SolicitudSubtipo, id=solicitud_id)
    if request.method == 'POST':
        solicitud.procesada = True
        solicitud.save()
        return HttpResponseRedirect(reverse('lista_solicitudes', args=[embarcacion_id]))
    return HttpResponseRedirect(reverse('lista_solicitudes', args=[embarcacion_id]))
# Vista para mostrar compras registradas


from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from .models import Proveedores
from .forms import ProveedorForm

# View para registrar una solicitud agrupada por subtipo
@csrf_protect
def registrar_solicitud_compra_view(request, embarcacion_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body.decode('utf-8'))
        tipo = data.get('tipo')
        subtipo = data.get('subtipo')
        productos = data.get('productos', [])
        embarcacion = Embarcacion.objects.get(pk=embarcacion_id)
        solicitud = SolicitudSubtipo.objects.create(tipo=tipo, subtipo=subtipo, embarcacion = embarcacion)
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
        return redirect('compras:lista_solicitudes', embarcacion_id=embarcacion_id)
    return render(request, 'solicitud_compra_form.html', {'embarcacion_id': embarcacion_id})


# View para listar solicitudes agrupadas por subtipo
def lista_solicitudes_view(request, embarcacion_id):
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
    solicitudes = SolicitudSubtipo.objects.filter(procesada=False, embarcacion_id=embarcacion_id).order_by('-id')
    #### Revisar estados
    compras_lote = CompraLote.objects.filter(embarcacion_id=embarcacion_id).exclude(estado__in=['exitosa', 'defectuosa', 'cancelada']).order_by('-fecha')
    return render(request, 'lista_solicitudes.html', {'solicitudes': solicitudes, 'compras_lote': compras_lote, 'embarcacion_id': embarcacion_id})


@csrf_protect
def dashboard_view(request, embarcacion_id):
    embarcacion = Embarcacion.objects.get(pk=embarcacion_id)
    return render(request, 'compras.html', {'embarcacion': embarcacion, "embarcacion_id":embarcacion_id})

@csrf_protect
def proveedores_view(request, embarcacion_id):
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
                return redirect('compras:proveedores', embarcacion_id=embarcacion_id)
    else:
        form = ProveedorForm()
    proveedores = Proveedores.objects.all()
    # IDs de proveedores bloqueados (asignados a cualquier CompraLote)
    proveedores_bloqueados = set(CompraLote.objects.filter(embarcacion_id=embarcacion_id).values_list('proveedor_id', flat=True))
    return render(request, 'proveedores.html', {
        'form': form,
        'proveedores': proveedores,
        'SUBTIPOS_POR_TIPO': SUBTIPOS_POR_TIPO,
        'tipo_seleccionado': tipo_seleccionado,
        'proveedores_bloqueados': proveedores_bloqueados,
        'embarcacion_id': embarcacion_id,
    })

@csrf_protect
def eliminar_proveedor(request, embarcacion_id):
    from .models import CompraLote
    from django.contrib import messages
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        if not proveedor_id:
            return redirect('compras:proveedores')
        proveedor = get_object_or_404(Proveedores, id=proveedor_id)
        # Validar si el proveedor está asignado a una compra lote activa
        compras_lote = CompraLote.objects.filter(proveedor=proveedor, estado__in=['Registrada', 'Espera_revision'])
        if compras_lote.exists():
            messages.error(request, 'No se puede eliminar el proveedor porque está asignado a una compra registrada o en espera por revisión.')
            return redirect('compras:proveedores')
        proveedor.countries.clear()
        proveedor.delete()
    return redirect('compras:proveedores', embarcacion_id=embarcacion_id)

def historial_compras_view(request, embarcacion_id):
    from .models import CompraLote
    embarcacion = Embarcacion.objects.get(pk=embarcacion_id)
    compras_lote = CompraLote.objects.filter(estado__in=['Exitosa', 'Defectuosa', 'Cancelada'], embarcacion=embarcacion).order_by('-fecha')
    return render(request, 'historial_compras.html', {'compras_lote': compras_lote, "embarcacion_id":embarcacion_id})

def revision_problemas_view(request, embarcacion_id):
    from .models import CompraLote
    embarcacion = Embarcacion.objects.get(pk=embarcacion_id)
    compras_lote = CompraLote.objects.filter(estado='Defectuosa', embarcacion=embarcacion).order_by('-fecha')
    return render(request, 'revision_problemas.html', {'compras_lote': compras_lote, "embarcacion_id":embarcacion_id})