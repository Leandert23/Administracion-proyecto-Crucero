from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
import json
import random
from datetime import date, timedelta
from .models import Medico, Paciente, Inventario, Solicitudmedicamento, cuarto, NotificacionUrgencia
from apps.cruceros.models import Crucero
from .forms import MedicoForm, PacienteForm, InventarioForm, SolicitudMedicamentoForm
from django.shortcuts import render, redirect






# Vista para editar un paciente
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('historial_medico')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'editar_paciente.html', {'form': form, 'paciente': paciente})

# Vista para eliminar un paciente (con confirmación por POST)
def eliminar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        paciente.delete()
        return redirect('historial_medico')
    return render(request, 'eliminar_paciente.html', {'paciente': paciente})

def panel_personal_medico(request):
    # Datos de ejemplo, reemplazar por consultas reales
    medico = Medico.objects.first()
    pacientes = Paciente.objects.all()[:5]
    inventario = Inventario.objects.all()[:5]
    context = {
        'medico': medico or {'nombres': 'Nombre', 'apellido': 'Apellido'},
        'pacientes': pacientes,
        'inventario': inventario,
    }
    return render(request, 'personal_medico_v2.html', context)

def panel_servicio_medico(request,):
    # Obtener el crucero activo (por ahora tomamos el primero)
    crucero_activo = Crucero.objects.first()
    
    if crucero_activo:
        # Generar o obtener cuartos para el crucero activo
        cuartos = cuarto.generar_cuartos_por_crucero(crucero_activo)
    else:
        cuartos = []
    
    # Datos de ejemplo, reemplazar por consultas reales
    medico = Medico.objects.first()
    pacientes = Paciente.objects.all()[:5]
    inventario = Inventario.objects.all()[:5]
    
    context = {
        'medico': medico or {'nombres': 'Nombre', 'apellido': 'Apellido'},
        'pacientes': pacientes,
        'inventario': inventario,
        'cuartos': cuartos,
        'crucero_activo': crucero_activo,
    }
    return render(request, 'servicio_medico.html', context)

def panel_inicio(request):
    return render(request, 'index.html')

def panel_inventario(request):
    inventario = Inventario.objects.all()
    context = {
        'inventario': inventario,
    }
    return render(request, 'inventario.html', context)

def agregar_historial(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('historial_medico')
    else:
        form = PacienteForm()
    return render(request, 'agregar_historial.html', {'form': form})

def historial_medico(request):
    from .models import Paciente
    pacientes = Paciente.objects.all()
    return render(request, 'historial_medico.html', {'pacientes': pacientes})

def prueba(request):
    return render(request, 'layouts/basetest.html')

def tu_vista_servicio_medico(request):
    cuartos_disponibles = cuarto.objects.filter(estado='D')
    return render(request, 'servicio_medico.html', {'cuartos_disponibles': cuartos_disponibles})

def comunicacion_mantenimiento(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        tipo_solicitud = request.POST.get('tipo_solicitud')
        prioridad = request.POST.get('prioridad')
        ubicacion = request.POST.get('ubicacion')
        equipo_afectado = request.POST.get('equipo_afectado')
        descripcion = request.POST.get('descripcion')
        solicitante = request.POST.get('solicitante')
        telefono = request.POST.get('telefono')
        
        # Aquí puedes agregar la lógica para guardar en la base de datos
        # Por ejemplo, crear un modelo SolicitudMantenimiento
        
        # Por ahora, solo redirigimos con un mensaje de éxito
        return redirect('panel_personal_medico')
    
    return render(request, 'comunicacion_mantenimiento.html')

def modificar_cuartos(request):
    # Obtener el crucero activo
    crucero_activo = Crucero.objects.first()
    
    if request.method == 'POST':
        cuarto_id = request.POST.get('cuarto_id')
        nuevo_estado = request.POST.get(f'estado_{cuarto_id}')
        paciente_id = request.POST.get(f'paciente_{cuarto_id}')
        
        try:
            cuarto_obj = cuarto.objects.get(id=cuarto_id)
            cuarto_obj.estado = nuevo_estado
            
            if nuevo_estado == 'O':
                if not paciente_id:
                    messages.error(request, "Debe seleccionar un paciente para ocupar el cuarto.")
                    return redirect('modificar_cuarto')
                
                # Verificar si el paciente ya está ocupando otro cuarto
                cuartos_ocupados_por_paciente = cuarto.objects.filter(
                    paciente_id=paciente_id,
                    estado='O'
                ).exclude(id=cuarto_id)
                
                if cuartos_ocupados_por_paciente.exists():
                    cuarto_existente = cuartos_ocupados_por_paciente.first()
                    paciente_nombre = Paciente.objects.get(id=paciente_id)
                    messages.error(request, 
                        f'El paciente {paciente_nombre.nombres} {paciente_nombre.primer_apellido} ya está ocupando el cuarto {cuarto_existente.numero}. '
                        'Un paciente no puede ocupar múltiples cuartos simultáneamente.'
                    )
                    return redirect('modificar_cuarto')
                
                cuarto_obj.paciente_id = paciente_id
            else:
                cuarto_obj.paciente = None
            
            # Intentar guardar con validaciones
            try:
                cuarto_obj.save()
                messages.success(request, f'Cuarto {cuarto_obj.numero} actualizado correctamente.')
            except ValidationError as e:
                # Si hay errores de validación, mostrar el mensaje
                for field, error_list in e.message_dict.items():
                    for error in error_list:
                        messages.error(request, error)
                return redirect('modificar_cuarto')
            
            return redirect('modificar_cuarto')
            
        except cuarto.DoesNotExist:
            messages.error(request, "Cuarto no encontrado.")
            return redirect('modificar_cuarto')
        except Exception as e:
            messages.error(request, f"Error al actualizar el cuarto: {str(e)}")
            return redirect('modificar_cuarto')
    else:
        if crucero_activo:
            # Generar o obtener cuartos para el crucero activo
            cuartos = cuarto.generar_cuartos_por_crucero(crucero_activo)
        else:
            cuartos = []
        
        pacientes = Paciente.objects.all()
        context = {
            'cuartos': cuartos, 
            'pacientes': pacientes,
            'crucero_activo': crucero_activo
        }
        return render(request, 'modificar_cuartos.html', context)
    
# Vista para agregar un elemento al inventario
def agregar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('panel_inventario')
    else:
        form = InventarioForm()
    return render(request, 'agregar_inventario.html', {'form': form})

def editar_inventario(request, inventario_id):
    inventario = get_object_or_404(Inventario, id=inventario_id)
    if request.method == 'POST':
        form = InventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()
            return redirect('panel_inventario')
    else:
        form = InventarioForm(instance=inventario)
    return render(request, 'editar_inventario.html', {'form': form, 'inventario': inventario})

# ========== VISTAS PARA SISTEMA DE URGENCIAS ==========

def panel_urgencias(request):
    """Panel para ver las notificaciones de urgencia"""
    notificaciones_pendientes = NotificacionUrgencia.objects.filter(estado='P').order_by('-fecha_creacion')
    notificaciones_atendidas = NotificacionUrgencia.objects.filter(estado='A').order_by('-fecha_atendida')
    
    context = {
        'notificaciones_pendientes': notificaciones_pendientes,
        'notificaciones_atendidas': notificaciones_atendidas,
    }
    return render(request, 'panel_urgencias_simple.html', context)

@csrf_exempt
def api_enviar_urgencia(request):
    """API para enviar notificaciones de urgencia"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Crear la notificación
            notificacion = NotificacionUrgencia.objects.create(
                modulo_origen=data.get('modulo_origen', 'Módulo Desconocido'),
                solicitante=data.get('solicitante', 'Usuario'),
                ubicacion=data.get('ubicacion', 'Ubicación no especificada'),
                tipo_urgencia=data.get('tipo_urgencia', 'Urgencia'),
                descripcion=data.get('descripcion', 'Sin descripción')
            )
            
            return JsonResponse({
                'success': True,
                'id': notificacion.id,
                'mensaje': 'Notificación enviada correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_marcar_atendida(request, notificacion_id):
    """API para marcar una notificación como atendida"""
    print(f"=== API MARCAR ATENDIDA - ID: {notificacion_id} ===")
    
    if request.method == 'POST':
        try:
            # Buscar la notificación
            notificacion = get_object_or_404(NotificacionUrgencia, id=notificacion_id)
            print(f"Notificación encontrada: {notificacion}")
            
            # Obtener observaciones
            observaciones = ''
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                observaciones = data.get('observaciones', '')
            else:
                observaciones = request.POST.get('observaciones', '')
            
            # Actualizar la notificación
            notificacion.estado = 'A'
            notificacion.fecha_atendida = timezone.now()
            notificacion.observaciones_medicas = observaciones
            notificacion.save()
            
            print(f"✅ Notificación {notificacion_id} marcada como atendida")
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Notificación marcada como atendida correctamente'
            })
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_test_urgencia(request):
    """Vista de prueba para verificar que las APIs funcionan"""
    print("=== VISTA DE PRUEBA LLAMADA ===")
    return JsonResponse({
        'success': True,
        'mensaje': 'API funcionando correctamente',
        'timestamp': timezone.now().isoformat()
    })

# ========== VISTAS PARA GESTIÓN DE HISTORIALES MÉDICOS ==========

@csrf_exempt
def api_generar_historiales_aleatorios(request):
    """API para generar 10 historiales médicos aleatorios"""
    if request.method == 'POST':
        try:
            # Datos aleatorios para generar historiales
            nombres_masculinos = ['Carlos', 'Juan', 'Pedro', 'Luis', 'Miguel', 'Antonio', 'Francisco', 'Manuel', 'David', 'José']
            nombres_femeninos = ['María', 'Ana', 'Carmen', 'Isabel', 'Laura', 'Elena', 'Patricia', 'Sandra', 'Cristina', 'Mónica']
            nombres_otros = ['Alex', 'Sam', 'Jordan', 'Taylor', 'Casey', 'Riley', 'Avery', 'Quinn', 'Morgan', 'Blake']
            apellidos = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Martín']
            
            motivos_consulta = [
                'Dolor de cabeza', 'Fiebre', 'Dolor abdominal', 'Resfriado común', 'Alergia',
                'Dolor de espalda', 'Náuseas', 'Fatiga', 'Insomnio', 'Ansiedad',
                'Dolor de garganta', 'Tos persistente', 'Dolor muscular', 'Mareos', 'Presión alta'
            ]
            
            descripciones = [
                'Paciente presenta síntomas leves, se recomienda reposo y medicación básica.',
                'Síntomas moderados, requiere seguimiento médico en 48 horas.',
                'Condición estable, se prescribe tratamiento conservador.',
                'Paciente responde bien al tratamiento inicial.',
                'Se requiere observación adicional y posible derivación especializada.'
            ]
            
            antecedentes = [
                'Sin antecedentes médicos relevantes.',
                'Hipertensión arterial controlada.',
                'Diabetes tipo 2 en tratamiento.',
                'Asma bronquial leve.',
                'Alergia a penicilina documentada.'
            ]
            
            alergias = [
                'Ninguna alergia conocida.',
                'Alergia a penicilina.',
                'Alergia a mariscos.',
                'Alergia al polen.',
                'Alergia a látex.'
            ]
            
            medicamentos = [
                'No toma medicamentos actualmente.',
                'Metformina 500mg diario.',
                'Losartán 50mg diario.',
                'Omeprazol 20mg diario.',
                'Paracetamol según necesidad.'
            ]
            
            historial_familiar = [
                'Sin antecedentes familiares relevantes.',
                'Padre con diabetes tipo 2.',
                'Madre con hipertensión arterial.',
                'Abuelo materno con enfermedad cardíaca.',
                'Hermano con asma bronquial.'
            ]
            
            direcciones = [
                'Calle Principal 123, Ciudad',
                'Avenida Central 456, Ciudad',
                'Plaza Mayor 789, Ciudad',
                'Calle Secundaria 321, Ciudad',
                'Avenida Norte 654, Ciudad'
            ]
            
            telefonos = ['555-0101', '555-0102', '555-0103', '555-0104', '555-0105']
            
            historiales_creados = []
            
            for i in range(10):
                # Generar datos aleatorios
                sexo = random.choice(['M', 'F', 'O'])
                if sexo == 'M':
                    nombre = random.choice(nombres_masculinos)
                elif sexo == 'F':
                    nombre = random.choice(nombres_femeninos)
                else:  # sexo == 'O'
                    nombre = random.choice(nombres_otros)
                
                primer_apellido = random.choice(apellidos)
                segundo_apellido = random.choice(apellidos)
                
                # Generar documento único
                documento = f"{random.randint(10000000, 99999999)}"
                
                # Generar fecha de nacimiento (entre 18 y 80 años)
                edad = random.randint(18, 80)
                fecha_nacimiento = date.today() - timedelta(days=edad*365 + random.randint(0, 365))
                
                # Generar email único
                email = f"{nombre.lower()}.{primer_apellido.lower()}{i}@email.com"
                
                # Crear paciente
                paciente = Paciente.objects.create(
                    nombres=nombre,
                    primer_apellido=primer_apellido,
                    segundo_apellido=segundo_apellido,
                    documento_identidad=documento,
                    sexo=sexo,
                    fechade_nacimiento=fecha_nacimiento,
                    direccion=random.choice(direcciones),
                    telefono=random.choice(telefonos),
                    correo_electronico=email,
                    motivo_consulta=random.choice(motivos_consulta),
                    descripcion_consulta=random.choice(descripciones),
                    antecedentes_medicos=random.choice(antecedentes),
                    alergias=random.choice(alergias),
                    medicamentos_actuales=random.choice(medicamentos),
                    historial_familiar=random.choice(historial_familiar)
                )
                
                historiales_creados.append({
                    'id': paciente.id,
                    'nombre': f"{paciente.nombres} {paciente.primer_apellido}",
                    'documento': paciente.documento_identidad
                })
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Se generaron {len(historiales_creados)} historiales médicos aleatorios correctamente',
                'historiales_creados': historiales_creados
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al generar historiales: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_borrar_todos_historiales(request):
    """API para borrar todos los historiales médicos"""
    if request.method == 'POST':
        try:
            # Contar historiales antes de borrar
            total_historiales = Paciente.objects.count()
            
            # Borrar todos los historiales
            Paciente.objects.all().delete()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Se eliminaron {total_historiales} historiales médicos correctamente',
                'total_eliminados': total_historiales
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar historiales: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

