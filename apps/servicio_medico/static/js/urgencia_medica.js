/**
 * Sistema de Urgencias Médicas - Componente Reutilizable
 * 
 * Uso:
 * 1. Incluir este archivo en el template
 * 2. Agregar el botón HTML donde se necesite
 * 3. Configurar con configurarUrgenciaMedica()
 */

// Configuración global
let configuracionUrgencia = {
    modulo: 'Módulo Desconocido',
    solicitante: 'Usuario',
    ubicacion: 'Ubicación no especificada'
};

/**
 * Configura el sistema de urgencias para un módulo específico
 */
function configurarUrgenciaMedica(modulo, solicitante, ubicacion) {
    configuracionUrgencia.modulo = modulo;
    configuracionUrgencia.solicitante = solicitante;
    configuracionUrgencia.ubicacion = ubicacion;
}

/**
 * Muestra el modal de urgencia médica
 */
function mostrarModalUrgencia() {
    // Crear el modal
    const modalHTML = `
        <div id="modalUrgencia" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                border: 3px solid #dc3545;
            ">
                <div style="
                    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                    color: white;
                    padding: 20px;
                    margin: -30px -30px 20px -30px;
                    border-radius: 9px 9px 0 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; font-size: 1.3em;">
                        Solicitar Asistencia Médica
                    </h3>
                    <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 0.9em;">
                        Use solo en casos de emergencias médicas reales
                    </p>
                </div>
                
                <form id="formUrgencia">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Solicitante:</label>
                        <input type="text" id="solicitante" value="${configuracionUrgencia.solicitante}" 
                               style="width: 100%; padding: 10px; border: 2px solid #e9ecef; border-radius: 6px;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Ubicación:</label>
                        <input type="text" id="ubicacion" value="${configuracionUrgencia.ubicacion}" 
                               style="width: 100%; padding: 10px; border: 2px solid #e9ecef; border-radius: 6px;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Tipo de Urgencia:</label>
                        <select id="tipoUrgencia" style="width: 100%; padding: 10px; border: 2px solid #e9ecef; border-radius: 6px;">
                            <option value="Accidente"> Accidente</option>
                            <option value="Caída"> Caída</option>
                            <option value="Desmayo"> Desmayo</option>
                            <option value="Lesión"> Lesión</option>
                            <option value="Dolor de Pecho"> Dolor de Pecho</option>
                            <option value="Dificultad Respiratoria"> Dificultad Respiratoria</option>
                            <option value="Otros"> Otros</option>
                        </select>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Descripción:</label>
                        <textarea id="descripcion" rows="3" placeholder="Describa la situación..." 
                                  style="width: 100%; padding: 10px; border: 2px solid #e9ecef; border-radius: 6px;"></textarea>
                    </div>
                    
                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button type="button" onclick="cerrarModalUrgencia()" 
                                style="padding: 10px 20px; border: 2px solid #6c757d; background: white; color: #6c757d; border-radius: 6px; cursor: pointer;">
                            Cancelar
                        </button>
                        <button type="button" onclick="enviarUrgencia()" 
                                style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer;">
                            Enviar Urgencia
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Cerrar modal al hacer clic fuera
    document.getElementById('modalUrgencia').addEventListener('click', function(e) {
        if (e.target === this) {
            cerrarModalUrgencia();
        }
    });
}

/**
 * Cierra el modal de urgencia
 */
function cerrarModalUrgencia() {
    const modal = document.getElementById('modalUrgencia');
    if (modal) {
        modal.remove();
    }
}

/**
 * Envía la notificación de urgencia
 */
function enviarUrgencia() {
    const solicitante = document.getElementById('solicitante').value;
    const ubicacion = document.getElementById('ubicacion').value;
    const tipoUrgencia = document.getElementById('tipoUrgencia').value;
    const descripcion = document.getElementById('descripcion').value;
    
    // Validar campos requeridos
    if (!solicitante || !ubicacion || !tipoUrgencia ) {
        alert('Por favor complete todos los campos requeridos.');
        return;
    }
    
    // Enviar datos al servidor
    const datos = {
        modulo_origen: configuracionUrgencia.modulo,
        solicitante: solicitante,
        ubicacion: ubicacion,
        tipo_urgencia: tipoUrgencia,
        descripcion: descripcion
    };
    
    fetch('/servicio-medico/api/urgencias/enviar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito
            alert('¡Urgencia médica enviada correctamente!\\n\\nEl servicio médico ha sido notificado.');
            cerrarModalUrgencia();
        } else {
            alert('Error al enviar la urgencia: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error de conexión. Verifique su conexión a internet.');
    });
}

/**
 * Obtiene el token CSRF
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Auto-inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Buscar botones de urgencia y agregar funcionalidad
    document.querySelectorAll('.btn-urgencia-medica').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarModalUrgencia();
        });
    });
});
