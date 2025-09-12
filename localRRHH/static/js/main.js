document.addEventListener('DOMContentLoaded', function () {
    const puestosPorCategoria = {
        'Culinario': ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender', 'Chef Ejecutivo', 'Chef de Partie', 'Auxiliares de cocina', 'Maitre d’', 'Jefe de meseros', 'Mesero'],
        'Administrativo': ['Gerente', 'Cajero'],
        'Medico': ['Enfermero', 'Medico General', 'Medico en Jefe', 'Paramedico'],
        'Entretenimiento': ['Animadores', "DJ's", 'Musicos', 'Bailarines', 'Guias Turisticos'],
        'Mantenimiento': ['Plomero', 'Ingeniero', 'Conserje', 'Tecnico'],
        'Personal Extra': ['No Ocupado']
    };


    
    const categoriaSelect = document.getElementById('categoria');
    const puestoSelect = document.getElementById('puesto');
    function actualizarPuestos() {
        const categoria = categoriaSelect.value;
        puestoSelect.innerHTML = '';
        if (categoria && puestosPorCategoria[categoria]) {
            puestosPorCategoria[categoria].forEach(puesto => {
                const option = document.createElement('option');
                option.value = puesto;
                option.text = puesto;
                puestoSelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = '';
            option.text = 'Seleccione categoría primero';
            puestoSelect.appendChild(option);
        }
    }

    if (categoriaSelect) {
        categoriaSelect.addEventListener('change', actualizarPuestos);
        actualizarPuestos();
    }

    // Registrar listener de acciones en la tabla solo si existe; pero NO terminar la ejecución
    // para que los botones del header (Generar/Vaciar/Actualizar) se registren aun con tabla vacía.
    const tabla = document.querySelector('table');
    if (tabla) {
        tabla.addEventListener('click', function(event) {
            const btn = event.target;
            if (btn.classList.contains('btn-editar')) {
                activarEdicionFila(btn.closest('tr'));
            } else if (btn.classList.contains('btn-guardar')) {
                guardarEdicion(btn.closest('tr'));
            } else if (btn.classList.contains('btn-eliminar')) {
                eliminarFila(btn.closest('tr'));
            } else if (btn.classList.contains('btn-cancelar')) {
                cancelarEdicion(btn.closest('tr'));
            }
        });
    }

    function activarEdicionFila(tr) {
        const btnEditar = tr.querySelector('.btn-editar');
        const btnEliminar = tr.querySelector('.btn-eliminar');

        if (!btnEditar || !btnEliminar) {
            alert('Error: No se encontraron los botones necesarios');
            return;
        }

        btnEditar.textContent = 'Guardar';
        btnEditar.classList.replace('btn-editar', 'btn-guardar');

        btnEliminar.textContent = 'Cancelar';
        btnEliminar.classList.replace('btn-eliminar', 'btn-cancelar');

        [...tr.querySelectorAll('td')].forEach((td, idx) => {
            if ([3,6,7,8,9,10].includes(idx)) {
                if (idx === 6) { 
                    const currentCat = td.textContent.trim();
                    td.innerHTML = '';
                    const selectCat = document.createElement('select');
                    selectCat.classList.add('edit-categoria');
                    for (const cat of Object.keys(puestosPorCategoria)) {
                        const opt = document.createElement('option');
                        opt.value = cat;
                        opt.textContent = cat;
                        if (cat === currentCat) opt.selected = true;
                        selectCat.appendChild(opt);
                    }
                    td.appendChild(selectCat);
                    selectCat.addEventListener('change', () => actualizarPuestosFila(tr));
                } else if (idx === 7) { 
                    const currentPuesto = td.textContent.trim();
                    td.innerHTML = '';
                    const selectPuesto = document.createElement('select');
                    selectPuesto.classList.add('edit-puesto');
                    td.appendChild(selectPuesto);
                    const catSelect = tr.querySelector('.edit-categoria');
                    if (catSelect) {
                        actualizarPuestosFila(tr, currentPuesto);
                    }
                } else if (idx === 8) { 
                    const currentStatus = td.textContent.trim();
                    td.innerHTML = '';
                    const selectStatus = document.createElement('select');
                    selectStatus.classList.add('edit-pStatus');
                    [['1', 'Activo'], ['2', 'Inactivo'], ['3', 'De baja']].forEach(([val, text]) => {
                        const opt = document.createElement('option');
                        opt.value = val;
                        opt.text = text;
                        if (text === currentStatus) opt.selected = true;
                        selectStatus.appendChild(opt);
                    });
                    td.appendChild(selectStatus);
                } else if (idx === 9) { 
                    const checked = td.querySelector('input').checked;
                    td.innerHTML = '';
                    const inputChk = document.createElement('input');
                    inputChk.type = 'checkbox';
                    inputChk.classList.add('amonestacion-estado-edit');
                    inputChk.checked = checked;
                    td.appendChild(inputChk);
                    const tdDetalle = tr.cells[10];
                    const detalleInput = tdDetalle.querySelector('input');

                    detalleInput.disabled = !inputChk.checked;

                    inputChk.addEventListener('change', e => {
                        if (e.target.checked) {
                            detalleInput.disabled = false;
                            detalleInput.focus();
                        } else {
                            detalleInput.value = '';
                            detalleInput.disabled = true;
                        }
                    });
                } else if (idx === 10) { 
                    const val = td.querySelector('input').value;
                    td.innerHTML = '';
                    const inputText = document.createElement('input');
                    inputText.type = 'text';
                    inputText.classList.add('amonestacion-detalle-edit');
                    inputText.maxLength = 50;
                    inputText.value = val;
                    td.appendChild(inputText);
                    const chk = tr.cells[9].querySelector('input');
                    inputText.disabled = !chk.checked;
                } else if (idx === 3) {
                    const currentVal = td.textContent.trim().replace('$', '').replace(',', '');
                    td.innerHTML = `<input type="number" min="1" max="99999999" class="edit-input" value="${currentVal}" title="El salario debe ser mayor a 0 y máximo 8 dígitos">`;
                }
            }
        });
    }

    function actualizarPuestosFila(tr, selectedPuesto = '') {
        const catSelect = tr.querySelector('.edit-categoria');
        const puestoCell = tr.cells[7];
        const puestoSelect = puestoCell.querySelector('select');
        if (!catSelect || !puestoSelect) return;
        const cat = catSelect.value;
        const puestos = puestosPorCategoria[cat] || [];
        puestoSelect.innerHTML = '';
        puestos.forEach(puesto => {
            const option = document.createElement('option');
            option.value = puesto;
            option.textContent = puesto;
            if (puesto === selectedPuesto) option.selected = true;
            puestoSelect.appendChild(option);
        });
    }

    function eliminarFila(tr) {
        if (!confirm('¿Está seguro que desea eliminar este registro?')) return;
        const id = tr.dataset.id;
        fetch(`/personal/${id}/delete/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            credentials: 'same-origin'
        })
        .then(resp => {
            if (resp.ok) {
                tr.remove();
                alert('Personal eliminado correctamente');
            } else {
                alert('Error al eliminar');
            }
        })
        .catch(() => alert('Error en la conexión'));
    }

    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Popover de motivo de amonestacion
    const popover = document.getElementById('popoverAmonestacion');
    const motivoInput = document.getElementById('inputMotivoAmonestacion');
    const btnGuardarMotivo = document.getElementById('btnGuardarMotivo');
    const btnCancelarMotivo = document.getElementById('btnCancelarMotivo');

    let trEnEdicionActual = null;
    let dataParaGuardar = null;
    let inputDetalleActual = null;

    function guardarEdicion(tr) {
        trEnEdicionActual = tr;

        const salarioInput = tr.cells[3].querySelector('input');
        const salario = salarioInput.value;
        const categoria = tr.cells[6].querySelector('select').value;
        const puesto = tr.cells[7].querySelector('select').value;
        const pStatus = tr.cells[8].querySelector('select').value;
        const amonestacionEstado = tr.cells[9].querySelector('input').checked;
        inputDetalleActual = tr.cells[10].querySelector('input');
        let amonestacionDetalle = inputDetalleActual.value;

        // Validación del salario
        const salarioNum = parseInt(salario);
        if (!salario || salarioNum <= 0) {
            alert('El salario debe ser mayor a 0.');
            salarioInput.focus();
            return;
        }
        if (salarioNum > 99999999) {
            alert('El salario no puede ser mayor a 99,999,999 (8 dígitos).');
            salarioInput.focus();
            return;
        }

        dataParaGuardar = {
            id: tr.dataset.id,
            salario,
            categoria,
            puesto,
            pStatus,
            amonestacionEstado,
            amonestacionDetalle
        };

        if (amonestacionEstado && (!amonestacionDetalle || amonestacionDetalle.trim() === '')) {
            motivoInput.value = '';
            // Mostrar el popover en posición fija (esquina superior derecha)
            // para evitar que provoque scroll o cambios en el layout.
            if (popover) {
                popover.style.position = 'fixed';
                popover.style.top = '10px';
                popover.style.right = '10px';
                popover.style.left = '';
                popover.style.display = 'block';
            }
            if (motivoInput) motivoInput.focus();
        } else {
            enviarDatosPUT();
        }
    }

    btnGuardarMotivo.onclick = () => {
        const motivo = motivoInput.value.trim();
        if (!motivo) {
            alert('Por favor, indique el motivo de la amonestación');
            motivoInput.focus();
            return;
        }
        dataParaGuardar.amonestacionDetalle = motivo;
        inputDetalleActual.value = motivo;
        popover.style.display = 'none';
        enviarDatosPUT();
    };

    btnCancelarMotivo.onclick = () => {
        popover.style.display = 'none';
        alert('Debe indicar el motivo de la amonestación para guardar');
    };

    function enviarDatosPUT() {
        const tr = trEnEdicionActual;
        const id = dataParaGuardar.id;
        const data = {
            salario: parseInt(dataParaGuardar.salario),
            edad: parseInt(tr.cells[4].textContent.trim()),
            anios_experiencia: parseInt(tr.cells[5].textContent.trim()),
            categoria: dataParaGuardar.categoria,
            puesto: dataParaGuardar.puesto,
            pStatus: parseInt(dataParaGuardar.pStatus),
            amonestacion: {
                estado: dataParaGuardar.amonestacionEstado,
                detalle: dataParaGuardar.amonestacionDetalle
            }
        };
        fetch(`/personal/${id}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                return response.json()
                    .then(errData => {
                        alert("Error al guardar:\n" + JSON.stringify(errData, null, 2));
                        throw new Error('Error en la actualización');
                    })
                    .catch(() => {
                        alert("Error en la actualización, código: " + response.status);
                        throw new Error('Error en la actualización');
                    });
            }
            return response.json();
        })
        .then(updated => {
            refrescarFila(tr, updated);
            alert('Personal actualizado correctamente');
            // Recargar la página para que todo quede sincronizado
            setTimeout(() => location.reload(), 300);
        })
        .catch(error => {
            if (error.message !== 'Error en la actualización') {
                alert('Error de conexión o inesperado: ' + error.message);
            }
            console.error('Error en fetch PUT:', error);
        });
    }

    function cancelarEdicion(tr) {
        location.reload();
    }

    function refrescarFila(tr, data) {
        // Actualizar columnas numéricas/texto
        tr.cells[3].textContent = '$' + data.salario;
        tr.cells[4].textContent = data.edad;
        tr.cells[5].textContent = data.anios_experiencia;
        tr.cells[6].textContent = data.categoria;
        tr.cells[7].textContent = data.puesto;

        const statusText = data.pStatus === 1 ? 'Activo' : (data.pStatus === 2 ? 'Inactivo' : 'De baja');
        const statusCell = tr.cells[8];
        const existingBadge = statusCell.querySelector('.badge-tipo');
        if (existingBadge) {
            existingBadge.textContent = statusText;
        } else {
            statusCell.textContent = statusText;
        }

        // Amonestación: reconstruir inputs sin reemplazar otros elementos
        const amCell = tr.cells[9];
        amCell.innerHTML = '';
        const chk = document.createElement('input');
        chk.type = 'checkbox';
        chk.classList.add('amonestacion-estado');
        chk.disabled = true;
        if (data.amonestacion && data.amonestacion.estado) chk.checked = true;
        amCell.appendChild(chk);

        const detCell = tr.cells[10];
        detCell.innerHTML = '';
        const detInput = document.createElement('input');
        detInput.type = 'text';
        detInput.classList.add('amonestacion-detalle');
        detInput.maxLength = 50;
        detInput.value = (data.amonestacion && data.amonestacion.detalle) ? data.amonestacion.detalle : '';
        detInput.disabled = true;
        detCell.appendChild(detInput);

        const btnGuardar = tr.querySelector('.btn-guardar');
        const btnCancelar = tr.querySelector('.btn-cancelar');

        if (btnGuardar) {
            btnGuardar.textContent = 'Editar';
            btnGuardar.classList.replace('btn-guardar', 'btn-editar');
        }

        if (btnCancelar) {
            btnCancelar.textContent = 'Eliminar';
            btnCancelar.classList.replace('btn-cancelar', 'btn-eliminar');
        }
    }

    // Función para actualizar plantel (botón pequeño)
    function actualizarPlantel() {
        location.reload();
    }

    // Filtrado por categoría en la tabla de personal (control añadido en template)
    const filterCategoria = document.getElementById('filterCategoria');
    function aplicarFiltroCategoria() {
        if (!filterCategoria) return;
        const val = filterCategoria.value;
        const tbody = document.querySelector('table.inst-table tbody');
        if (!tbody) return;
        [...tbody.querySelectorAll('tr')].forEach(tr => {
            const categoriaCell = tr.cells[6];
            const categoriaText = categoriaCell ? categoriaCell.textContent.trim() : '';
            if (!val || val === '') {
                tr.style.display = '';
            } else {
                tr.style.display = (categoriaText === val) ? '' : 'none';
            }
        });
    }

    if (filterCategoria) {
        filterCategoria.addEventListener('change', aplicarFiltroCategoria);
        // aplicar filtro al cargar por si hay un valor por defecto
        aplicarFiltroCategoria();
    }

    // Modal y acciones de Generar/Vaciar plantel
    const btnMostrarGenerar = document.getElementById('btnMostrarGenerar');
    const btnVaciarPlantel = document.getElementById('btnVaciarPlantel');
    const btnActualizar = document.getElementById('btnActualizar');
    const modalGenerar = document.getElementById('modalGenerar');
    const btnGenerarCancelar = document.getElementById('btnGenerarCancelar');
    const btnGenerarConfirmar = document.getElementById('btnGenerarConfirmar');
    const generarFeedback = document.getElementById('generarFeedback');
    const generarSpinner = document.getElementById('generarSpinner');

    let cantidadSeleccionada = null;
    // Normalizar estilo de botones del header para usar color principal del sitio
    [btnMostrarGenerar, btnVaciarPlantel, btnActualizar].forEach(b => {
        if (b) {
            b.classList.add('btn', 'btn-primary');
            // Remover estilos inline que puedan causar colores inconsistentes
            b.style.backgroundColor = '';
            b.style.borderColor = '';
        }
    });

    function abrirModalGenerar() {
        cantidadSeleccionada = null;
        // reset botones
        modalGenerar.style.display = 'flex';
        generarFeedback.style.display = 'none';
        generarSpinner.style.display = 'none';
        document.querySelectorAll('.btn-cantidad').forEach(b => b.classList.remove('selected'));
    }

    function cerrarModalGenerar() {
        modalGenerar.style.display = 'none';
    }

    if (btnMostrarGenerar) btnMostrarGenerar.addEventListener('click', abrirModalGenerar);
    if (btnGenerarCancelar) btnGenerarCancelar.addEventListener('click', cerrarModalGenerar);
    if (btnActualizar) btnActualizar.addEventListener('click', actualizarPlantel);

    document.querySelectorAll('.btn-cantidad').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.btn-cantidad').forEach(b => b.style.borderColor = '#ccc');
            this.style.borderColor = '#06b6d4';
            cantidadSeleccionada = parseInt(this.dataset.cantidad, 10);
        });
    });

    if (btnGenerarConfirmar) btnGenerarConfirmar.addEventListener('click', function () {
        if (!cantidadSeleccionada) {
            alert('Seleccione una cantidad antes de generar.');
            return;
        }
        // Mostrar spinner y deshabilitar
        generarSpinner.style.display = 'block';
        btnGenerarConfirmar.disabled = true;
        fetch('/generar-plantel/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin',
            body: JSON.stringify({ cantidad: cantidadSeleccionada })
        })
        .then(resp => resp.json().then(js => ({ ok: resp.ok, status: resp.status, body: js })))
        .then(res => {
            generarSpinner.style.display = 'none';
            btnGenerarConfirmar.disabled = false;
            if (res.ok) {
                generarFeedback.style.display = 'block';
                generarFeedback.textContent = 'Generados: ' + (res.body.created_count || 0) + '. Recargando...';
                setTimeout(() => location.reload(), 800);
            } else {
                generarFeedback.style.display = 'block';
                generarFeedback.textContent = 'Error: ' + (res.body.error || JSON.stringify(res.body));
            }
        })
        .catch(err => {
            generarSpinner.style.display = 'none';
            btnGenerarConfirmar.disabled = false;
            generarFeedback.style.display = 'block';
            generarFeedback.textContent = 'Error de conexión: ' + err.message;
        });
    });

    // Vaciar plantel con confirmación
    if (btnVaciarPlantel) btnVaciarPlantel.addEventListener('click', function () {
        if (!confirm('¿Seguro que desea eliminar todo el plantel y las amonestaciones? Esta acción no se puede deshacer.')) return;
        btnVaciarPlantel.disabled = true;
        fetch('/vaciar-plantel/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            credentials: 'same-origin'
        })
        .then(resp => resp.json())
        .then(js => {
            alert('Vaciado completado. ' + (js.deleted_personal || 0) + ' personal eliminado. Recargando...');
            location.reload();
        })
        .catch(err => {
            btnVaciarPlantel.disabled = false;
            alert('Error al vaciar: ' + err.message);
        });
    });
});
