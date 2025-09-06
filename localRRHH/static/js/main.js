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

    const tabla = document.querySelector('table');
    if (!tabla) return;

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

    function activarEdicionFila(tr) {
        const btnEditar = tr.querySelector('.btn-editar');
        const btnEliminar = tr.querySelector('.btn-eliminar');

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
                    const currentVal = td.textContent.trim();
                    td.innerHTML = `<input type="number" min="0" class="edit-input" value="${currentVal}">`;
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
        fetch(`/api/personal/${id}/`, {
            method: 'DELETE',
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

        const salario = tr.cells[3].querySelector('input').value;
        const categoria = tr.cells[6].querySelector('select').value;
        const puesto = tr.cells[7].querySelector('select').value;
        const pStatus = tr.cells[8].querySelector('select').value;
        const amonestacionEstado = tr.cells[9].querySelector('input').checked;
        inputDetalleActual = tr.cells[10].querySelector('input');
        let amonestacionDetalle = inputDetalleActual.value;

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
            // Posiciona el popover cerca del input detalle
            const rect = inputDetalleActual.getBoundingClientRect();
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

            popover.style.top = (rect.top + scrollTop + rect.height + 5) + 'px';
            popover.style.left = (rect.left + scrollLeft) + 'px';
            popover.style.display = 'block';
            motivoInput.focus();

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
        fetch(`/api/personal/${id}/`, {
            method: 'PUT',
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
        tr.cells[3].textContent = data.salario;
        tr.cells[4].textContent = data.edad;
        tr.cells[5].textContent = data.anios_experiencia;
        tr.cells[6].textContent = data.categoria;
        tr.cells[7].textContent = data.puesto;
        tr.cells[8].textContent = data.pStatus === 1 ? 'Activo' : (data.pStatus === 2 ? 'Inactivo' : 'De baja');

        tr.cells[9].innerHTML = `<input type="checkbox" class="amonestacion-estado" ${data.amonestacion?.estado ? 'checked' : ''} disabled />`;
        tr.cells[10].innerHTML = `<input type="text" class="amonestacion-detalle" maxlength="50" value="${data.amonestacion?.detalle || ''}" disabled />`;

        const btnGuardar = tr.querySelector('.btn-guardar');
        const btnCancelar = tr.querySelector('.btn-cancelar');

        btnGuardar.textContent = 'Editar';
        btnGuardar.classList.replace('btn-guardar', 'btn-editar');

        btnCancelar.textContent = 'Eliminar';
        btnCancelar.classList.replace('btn-cancelar', 'btn-eliminar');
    }
});
