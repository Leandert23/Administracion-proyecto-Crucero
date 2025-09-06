// Validaciones JavaScript para el módulo de administración

// Función para mostrar mensajes de éxito/error
function mostrarMensaje(tipo, mensaje) {
    const alertClass = tipo === 'success' ? 'alert-success' :
                      tipo === 'error' ? 'alert-danger' :
                      tipo === 'warning' ? 'alert-warning' : 'alert-info';

    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Insertar el mensaje en el contenedor de mensajes
    const messagesContainer = document.querySelector('.dashboard-content .alert')?.parentElement ||
                             document.querySelector('.dashboard-content');

    if (messagesContainer) {
        messagesContainer.insertAdjacentHTML('afterbegin', alertHtml);

        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            const alert = messagesContainer.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Validación de formularios
function validarFormulario(form) {
    let esValido = true;
    const camposRequeridos = form.querySelectorAll('[required]');

    camposRequeridos.forEach(campo => {
        if (!campo.value.trim()) {
            campo.classList.add('is-invalid');
            esValido = false;

            // Agregar mensaje de error si no existe
            let errorMsg = campo.parentElement.querySelector('.invalid-feedback');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'invalid-feedback';
                errorMsg.textContent = 'Este campo es obligatorio.';
                campo.parentElement.appendChild(errorMsg);
            }
        } else {
            campo.classList.remove('is-invalid');
            campo.classList.add('is-valid');

            // Remover mensaje de error
            const errorMsg = campo.parentElement.querySelector('.invalid-feedback');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });

    return esValido;
}

// Función para mostrar loading en botones
function mostrarLoading(boton, texto = 'Cargando...') {
    boton.classList.add('btn-loading');
    boton.disabled = true;

    if (texto) {
        boton.dataset.originalText = boton.textContent;
        boton.textContent = texto;
    }
}

// Función para ocultar loading en botones
function ocultarLoading(boton) {
    boton.classList.remove('btn-loading');
    boton.disabled = false;

    if (boton.dataset.originalText) {
        boton.textContent = boton.dataset.originalText;
        delete boton.dataset.originalText;
    }
}

// Función para confirmar acciones destructivas
function confirmarAccion(mensaje = '¿Está seguro de que desea realizar esta acción?') {
    return confirm(mensaje);
}

// Función para copiar al portapapeles
function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto).then(() => {
        mostrarMensaje('success', 'Copiado al portapapeles');
    }).catch(err => {
        console.error('Error al copiar:', err);
        mostrarMensaje('error', 'Error al copiar al portapapeles');
    });
}

// Función para formatear fechas
function formatearFecha(fecha) {
    const opciones = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(fecha).toLocaleDateString('es-ES', opciones);
}

// Función para formatear números como moneda
function formatearMoneda(cantidad, moneda = '$') {
    return `${moneda}${parseFloat(cantidad).toLocaleString('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

// Función para validar emails
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Función para validar contraseñas
function validarContrasena(contrasena) {
    // Mínimo 8 caracteres, al menos una mayúscula, una minúscula y un número
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return regex.test(contrasena);
}

// Función para mostrar/ocultar contraseñas
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        input.type = 'password';
        button.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Función para inicializar tooltips
function inicializarTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Función para manejar errores de AJAX
function manejarErrorAjax(xhr, status, error) {
    console.error('Error AJAX:', error);
    let mensaje = 'Ha ocurrido un error inesperado.';

    if (xhr.responseJSON && xhr.responseJSON.message) {
        mensaje = xhr.responseJSON.message;
    } else if (xhr.status === 403) {
        mensaje = 'No tienes permisos para realizar esta acción.';
    } else if (xhr.status === 404) {
        mensaje = 'El recurso solicitado no fue encontrado.';
    } else if (xhr.status === 500) {
        mensaje = 'Error interno del servidor.';
    }

    mostrarMensaje('error', mensaje);
}

// Función para actualizar contadores en tiempo real
function actualizarContadores() {
    // Esta función se puede usar para actualizar estadísticas en tiempo real
    fetch('/api/dashboard/stats/')
        .then(response => response.json())
        .then(data => {
            // Actualizar los contadores en la UI
            Object.keys(data).forEach(key => {
                const elemento = document.getElementById(`contador-${key}`);
                if (elemento) {
                    elemento.textContent = data[key];
                }
            });
        })
        .catch(error => console.error('Error actualizando contadores:', error));
}

// Función para filtrar tablas
function filtrarTabla(inputId, tablaId) {
    const input = document.getElementById(inputId);
    const tabla = document.getElementById(tablaId);
    const filas = tabla.querySelectorAll('tbody tr');

    input.addEventListener('keyup', function() {
        const filtro = this.value.toLowerCase();

        filas.forEach(fila => {
            const texto = fila.textContent.toLowerCase();
            fila.style.display = texto.includes(filtro) ? '' : 'none';
        });
    });
}

// Función para ordenar tablas
function ordenarTabla(columna, tablaId, tipo = 'string') {
    const tabla = document.getElementById(tablaId);
    const tbody = tabla.querySelector('tbody');
    const filas = Array.from(tbody.querySelectorAll('tr'));

    filas.sort((a, b) => {
        const aVal = a.cells[columna].textContent.trim();
        const bVal = b.cells[columna].textContent.trim();

        if (tipo === 'number') {
            return parseFloat(aVal.replace(/[^\d.-]/g, '')) - parseFloat(bVal.replace(/[^\d.-]/g, ''));
        } else if (tipo === 'date') {
            return new Date(aVal) - new Date(bVal);
        } else {
            return aVal.localeCompare(bVal);
        }
    });

    filas.forEach(fila => tbody.appendChild(fila));
}

// Función para exportar tablas a CSV
function exportarTablaACSV(tablaId, nombreArchivo = 'export.csv') {
    const tabla = document.getElementById(tablaId);
    let csv = [];

    // Obtener headers
    const headers = tabla.querySelectorAll('thead th');
    const headerRow = [];
    headers.forEach(header => {
        headerRow.push(header.textContent.trim());
    });
    csv.push(headerRow.join(','));

    // Obtener filas de datos
    const filas = tabla.querySelectorAll('tbody tr');
    filas.forEach(fila => {
        const filaData = [];
        const celdas = fila.querySelectorAll('td');
        celdas.forEach(celda => {
            filaData.push(celda.textContent.trim());
        });
        csv.push(filaData.join(','));
    });

    // Crear y descargar archivo
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', nombreArchivo);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Inicializar funcionalidades cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    inicializarTooltips();

    // Validar formularios al enviar
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (!validarFormulario(form)) {
            e.preventDefault();
            mostrarMensaje('error', 'Por favor, complete todos los campos requeridos.');
        }
    });

    // Limpiar validaciones al escribir
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('is-invalid')) {
            e.target.classList.remove('is-invalid');
            const errorMsg = e.target.parentElement.querySelector('.invalid-feedback');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });

    // Manejar clicks en botones de acción
    document.addEventListener('click', function(e) {
        // Copiar al portapapeles
        if (e.target.closest('[data-action="copy"]')) {
            const elemento = e.target.closest('[data-action="copy"]');
            const texto = elemento.dataset.text || elemento.textContent;
            copiarAlPortapapeles(texto);
        }

        // Confirmar acciones destructivas
        if (e.target.closest('[data-confirm]')) {
            const elemento = e.target.closest('[data-confirm]');
            const mensaje = elemento.dataset.confirm || '¿Está seguro?';
            if (!confirmarAccion(mensaje)) {
                e.preventDefault();
            }
        }

        // Mostrar/ocultar contraseñas
        if (e.target.closest('[data-toggle="password"]')) {
            const elemento = e.target.closest('[data-toggle="password"]');
            const inputId = elemento.dataset.target;
            togglePasswordVisibility(inputId, elemento);
        }
    });

    // Actualizar contadores cada 5 minutos
    setInterval(actualizarContadores, 300000);
});
