document.addEventListener('DOMContentLoaded', function () {
    const puestosPorCategoria = {
        'Culinario': ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender', 'Chef Ejecutivo', 'Chef de Partie', 'Auxiliares de cocina', 'Maitre d’', 'Jefe de meseros', 'Mesero', 'Sous chef', 'Sommelier', 'Jefe de Alimentos'],
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

    // Función para generar opciones horario en 24 horas, cada 30 min
    function generarOpcionesHoras() {
        let opciones = '';
        for(let h = 0; h < 24; h++) {
            for(let m = 0; m < 60; m += 30) {
                let horaStr = (h < 10 ? '0' : '') + h;
                let minStr = (m === 0) ? '00' : m;
                opciones += `<option value="${horaStr}:${minStr}">${horaStr}:${minStr}</option>`;
            }
        }
        return opciones;
    }

    // Función para generar opciones días de la semana
    function generarOpcionesDias() {
        const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
        return dias.map(dia => `<option value="${dia}">${dia}</option>`).join('');
    }

    // Insertar opciones a nuevos selects
    ['horario_entrada', 'horario_salida'].forEach(id => {
        const select = document.getElementById(id);
        if (select) select.innerHTML = generarOpcionesHoras();
    });

    ['dia_inicio', 'dia_fin'].forEach(id => {
        const select = document.getElementById(id);
        if (select) select.innerHTML = generarOpcionesDias();
    });

    // --- Validaciones existentes y resto del JS (sin cambios) ---
    // Aquí continúa todo el código de validaciones y lógica que ya tenías,
    // agregando, si quieres, validaciones para horario y día:

    const formRegistro = document.querySelector('form[method="POST"]');
    if (formRegistro) {
        formRegistro.addEventListener('submit', function (e) {
            // Validación ejemplo para horarios
            const entrada = document.getElementById('horario_entrada').value;
            const salida = document.getElementById('horario_salida').value;

            // Convertir HH:MM a minutos
            function aMinutos(hora) {
                let partes = hora.split(':');
                return parseInt(partes[0]) * 60 + parseInt(partes[1]);
            }

            if (aMinutos(salida) <= aMinutos(entrada)) {
                e.preventDefault();
                alert('La hora de salida debe ser posterior a la hora de entrada.');
                return;
            }

            // Validar días (opcional)
            const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
            const diaInicioVal = document.getElementById('dia_inicio').value;
            const diaFinVal = document.getElementById('dia_fin').value;

            if (dias.indexOf(diaFinVal) < dias.indexOf(diaInicioVal)) {
                e.preventDefault();
                alert('El día de fin debe ser igual o posterior al día de inicio.');
                return;
            }
        });
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
        // Índices de las columnas editables según el orden especificado:
        // por ejemplo: nombre(1), apellido(2), salario(3), edad(4), años experiencia(5),
        // categoría(6), puesto(7), hora entrada(8), hora salida(9), día inicio(10), día fin(11),
        // estado(12), amonestación(13)
        if ([1,2,3,4,5,6,7,8,9,10,11,12,13].includes(idx)) {
            if (idx === 1 || idx === 2) {
                // Nombre o apellido: input texto
                const currentVal = td.textContent.trim();
                td.innerHTML = `<input type="text" maxlength="10" class="edit-input" value="${currentVal}" required>`;
            } else if (idx === 3) {
                // Salario: input number
                const currentVal = td.textContent.trim().replace('$','').replace(',','');
                td.innerHTML = `<input type="number" min="1" max="99999999" class="edit-input" value="${currentVal}" required>`;
            } else if (idx === 4 || idx === 5) {
                // Edad o años de experiencia: input number con validación más tarde
                const currentVal = td.textContent.trim();
                td.innerHTML = `<input type="number" min="0" class="edit-input" value="${currentVal}" required>`;
            } else if (idx === 6) {
                // Categoría
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
                // Puesto
                const currentPuesto = td.textContent.trim();
                td.innerHTML = '';
                const selectPuesto = document.createElement('select');
                selectPuesto.classList.add('edit-puesto');
                td.appendChild(selectPuesto);
                const catSelect = tr.querySelector('.edit-categoria');
                if (catSelect) {
                    actualizarPuestosFila(tr, currentPuesto);
                }
            } else if (idx === 8 || idx === 9) {
                // Hora entrada o salida
                const val = td.textContent.trim();
                td.innerHTML = '';
                const selectHora = document.createElement('select');
                selectHora.classList.add(idx === 8 ? 'edit-horario-entrada' : 'edit-horario-salida');
                for(let h=0; h<24; h++) {
                    for(let m=0; m<60; m+=30) {
                        let horaStr = (h<10?'0':'')+h;
                        let minStr = (m===0?'00':m);
                        const option = document.createElement('option');
                        option.value = horaStr + ':' + minStr;
                        option.textContent = option.value;
                        if(option.value === val) option.selected = true;
                        selectHora.appendChild(option);
                    }
                }
                td.appendChild(selectHora);
            } else if (idx === 10 || idx === 11) {
                // Día inicio o día fin
                const val = td.textContent.trim();
                td.innerHTML = '';
                const selectDia = document.createElement('select');
                selectDia.classList.add(idx === 10 ? 'edit-dia-inicio' : 'edit-dia-fin');
                const diasSemana = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'];
                diasSemana.forEach(dia => {
                    const option = document.createElement('option');
                    option.value = dia;
                    option.textContent = dia;
                    if(dia === val) option.selected = true;
                    selectDia.appendChild(option);
                });
                td.appendChild(selectDia);
            } else if (idx === 12) {
                // Estado
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
            } else if (idx === 13) {
                // Amonestacion checkbox
                const existingChk = td.querySelector('input');
                const checked = existingChk ? (existingChk.checked || existingChk.value === 'True' || existingChk.value === 'true' || existingChk.value === '1') : false;
                td.innerHTML = '';
                const inputChk = document.createElement('input');
                inputChk.type = 'checkbox';
                inputChk.classList.add('amonestacion-estado-edit');
                if (checked) inputChk.checked = true;
                td.appendChild(inputChk);

                // El campo detalle sigue siendo input texto deshabilitado en siguiente columna
                const tdDetalle = tr.cells[14]; 
                const detalleInput = tdDetalle ? tdDetalle.querySelector('input') : null;
                if (detalleInput) {
                    if (typeof detalleInput.value === 'string') {
                        const low = detalleInput.value.trim();
                        if (['None', 'null', 'NULL'].includes(low)) {
                            detalleInput.value = '';
                        }
                    }
                    detalleInput.disabled = true;
                }
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
                // Recargar la página después de eliminar para sincronizar y regenerar índices/paginación
                alert('Personal eliminado correctamente. La página se recargará.');
                setTimeout(() => location.reload(), 200);
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

    const nombre = tr.cells[1].querySelector('input').value.trim();
    const apellido = tr.cells[2].querySelector('input').value.trim();
    const salario = tr.cells[3].querySelector('input').value.trim();
    const edad = tr.cells[4].querySelector('input').value.trim();
    const aniosExperiencia = tr.cells[5].querySelector('input').value.trim();
    const categoria = tr.cells[6].querySelector('select').value;
    const puesto = tr.cells[7].querySelector('select').value;
    const horarioEntrada = tr.cells[8].querySelector('select').value;
    const horarioSalida = tr.cells[9].querySelector('select').value;
    const diaInicio = tr.cells[10].querySelector('select').value;
    const diaFin = tr.cells[11].querySelector('select').value;
    const pStatus = tr.cells[12].querySelector('select').value;
    const amonestacionEstado = tr.cells[13].querySelector('input').checked;
    inputDetalleActual = tr.cells[14].querySelector('input');
    let amonestacionDetalle = inputDetalleActual ? inputDetalleActual.value.trim() : '';

    // Validaciones básicas
    if (!nombre || !apellido) {
        alert('Nombre y apellido no pueden estar vacíos.');
        return;
    }
    if (!salario || parseInt(salario) <= 0) {
        alert('Salario debe ser un número mayor a 0.');
        return;
    }
    if (!edad || parseInt(edad) < 21) {
        alert('Edad debe ser al menos 21.');
        return;
    }
    if (!aniosExperiencia || parseInt(aniosExperiencia) < 0) {
        alert('Años de experiencia inválidos.');
        return;
    }
    // Validar horario
    function aMinutos(hora) {
        let partes = hora.split(':');
        return parseInt(partes[0])*60 + parseInt(partes[1]);
    }
    if (aMinutos(horarioSalida) <= aMinutos(horarioEntrada)) {
        alert('La hora de salida debe ser posterior a la de entrada.');
        return;
    }
    // Validar días
    const diasOrden = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'];
    if (diasOrden.indexOf(diaFin) < diasOrden.indexOf(diaInicio)) {
        alert('El día de fin debe ser igual o posterior al día de inicio.');
        return;
    }
    

    dataParaGuardar = {
        id: tr.dataset.id,
        nombre,
        apellido,
        salario,
        edad,
        anios_experiencia: aniosExperiencia,
        categoria,
        puesto,
        horario_entrada: horarioEntrada,
        horario_salida: horarioSalida,
        dia_inicio: diaInicio,
        dia_fin: diaFin,
        pStatus,
        amonestacionEstado,
        amonestacionDetalle
    };

    // Mostrar popover si falta motivo amonestacion, o enviar directo
    if (amonestacionEstado && !amonestacionDetalle) {
        motivoInput.value = '';
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
            horario_entrada: dataParaGuardar.horario_entrada,
            horario_salida: dataParaGuardar.horario_salida,
            dia_inicio: dataParaGuardar.dia_inicio,
            dia_fin: dataParaGuardar.dia_fin,
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
        // Actualizar columnas existentes
        tr.cells[3].textContent = '$' + data.salario;
        tr.cells[4].textContent = data.edad;
        tr.cells[5].textContent = data.anios_experiencia;
        tr.cells[6].textContent = data.categoria;
        tr.cells[7].textContent = data.puesto;

        const statusText = data.pStatus === 1 ? 'Activo' : (data.pStatus === 2 ? 'Inactivo' : 'De baja');
        tr.cells[8].textContent = statusText;

        // Actualizar amonestación (checkbox y detalle)
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

        // NUEVO: Actualizar las columnas de horario y días (indices 11 a 14)
        tr.cells[11].textContent = data.horario_entrada || '';
        tr.cells[12].textContent = data.horario_salida || '';
        tr.cells[13].textContent = data.dia_inicio || '';
        tr.cells[14].textContent = data.dia_fin || '';

        // Restaurar botones al estado inicial
        const btnGuardar = tr.querySelector('.btn-guardar');
        if (btnGuardar) {
            btnGuardar.textContent = 'Editar';
            btnGuardar.classList.replace('btn-guardar', 'btn-editar');
        }
        const btnCancelar = tr.querySelector('.btn-cancelar');
        if (btnCancelar) {
            btnCancelar.textContent = 'Eliminar';
            btnCancelar.classList.replace('btn-cancelar', 'btn-eliminar');
        }
    }


    // Función para actualizar plantel (botón pequeño)
    function actualizarPlantel() {
        location.reload();
    }

    // Conectar el botón actualizar (se conectará más adelante con las otras variables)

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

    // Nuevo: filtro por nombre combinado con filtro de categoría + paginación cliente
    const filterNombre = document.getElementById('filterNombre');
    const tbody = document.querySelector('table.inst-table tbody');
    let allRows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];
    const PAGE_SIZE = 20;
    let currentPage = 1;

    function applyCombinedFiltersAndPaginate() {
        const catVal = filterCategoria ? filterCategoria.value : '';
        const nameVal = filterNombre ? filterNombre.value.trim().toLowerCase() : '';

        // Filtrar filas según categoría y nombre
        const filtered = allRows.filter(tr => {
            const categoriaText = (tr.cells[6] ? tr.cells[6].textContent.trim() : '').toString();
            const nombreText = (tr.cells[1] ? tr.cells[1].textContent.trim().toLowerCase() : '').toString();
            const catMatch = !catVal || catVal === '' || categoriaText === catVal;
            const nameMatch = !nameVal || nombreText.indexOf(nameVal) !== -1;
            return catMatch && nameMatch;
        });

        // Paginación
        const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
        if (currentPage > totalPages) currentPage = totalPages;
        const start = (currentPage - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        const visibleSet = filtered.slice(start, end);

        // Ocultar todas y mostrar solo visibles
        allRows.forEach(r => r.style.display = 'none');
        visibleSet.forEach(r => r.style.display = '');

        renderPageNumbers(totalPages);
    }

    // Mostrar hasta 10 botones centrados en la página actual (si es posible)
    function renderPageNumbers(totalPages) {
        const pageNumbers = document.getElementById('pageNumbers');
        pageNumbers.innerHTML = '';

        const MAX_VISIBLE = 10;
        let start = 1;
        let end = totalPages;

        if (totalPages > MAX_VISIBLE) {
            // Centrar la ventana alrededor de currentPage
            const half = Math.floor(MAX_VISIBLE / 2);
            start = Math.max(1, currentPage - half);
            end = start + MAX_VISIBLE - 1;
            if (end > totalPages) {
                end = totalPages;
                start = end - MAX_VISIBLE + 1;
            }
        }

        for (let i = start; i <= end; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            btn.classList.add('btn');
            btn.style.padding = '6px 10px';
            btn.style.minWidth = '36px';
            if (i === currentPage) {
                btn.style.fontWeight = '700';
                btn.style.background = '#e2e8f0';
            }
            btn.addEventListener('click', () => {
                currentPage = i;
                applyCombinedFiltersAndPaginate();
            });
            pageNumbers.appendChild(btn);
        }

        // Si hay más páginas fuera del rango visible, mostrar indicador de continuidad
        const pageNumbersContainer = document.getElementById('pageNumbersContainer');
        if (pageNumbersContainer) {
            // Asegurar que el contenedor no provoque overflow en el body
            pageNumbersContainer.style.overflow = 'hidden';
        }
    }

    // Prev/Next
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    if (prevPageBtn) prevPageBtn.addEventListener('click', () => { if (currentPage > 1) { currentPage--; applyCombinedFiltersAndPaginate(); } });
    if (nextPageBtn) nextPageBtn.addEventListener('click', () => { currentPage++; applyCombinedFiltersAndPaginate(); });

    // Manejo de 'Ir a página'
    const gotoInput = document.getElementById('gotoPage');
    const gotoBtn = document.getElementById('btnGotoPage');
    function gotoPageRequested() {
        if (!gotoInput) return;
        const val = parseInt(gotoInput.value, 10);
        if (isNaN(val) || val < 1) {
            alert('Por favor indique un número de página válido (>=1).');
            return;
        }
        // Determinar totalPages según el último filtrado
        const catVal = filterCategoria ? filterCategoria.value : '';
        const nameVal = filterNombre ? filterNombre.value.trim().toLowerCase() : '';
        const filteredCount = allRows.filter(tr => {
            const categoriaText = (tr.cells[6] ? tr.cells[6].textContent.trim() : '').toString();
            const nombreText = (tr.cells[1] ? tr.cells[1].textContent.trim().toLowerCase() : '').toString();
            const catMatch = !catVal || catVal === '' || categoriaText === catVal;
            const nameMatch = !nameVal || nombreText.indexOf(nameVal) !== -1;
            return catMatch && nameMatch;
        }).length;
        const totalPages = Math.max(1, Math.ceil(filteredCount / PAGE_SIZE));
        if (val > totalPages) {
            alert('La página indicada no existe. Páginas disponibles: ' + totalPages);
            return;
        }
        currentPage = val;
        applyCombinedFiltersAndPaginate();
    }
    if (gotoBtn) gotoBtn.addEventListener('click', gotoPageRequested);
    if (gotoInput) gotoInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); gotoPageRequested(); } });

    // Inputs de filtro actualizan y reset la paginación a 1
    if (filterCategoria) filterCategoria.addEventListener('change', () => { currentPage = 1; applyCombinedFiltersAndPaginate(); });
    if (filterNombre) filterNombre.addEventListener('input', () => { currentPage = 1; applyCombinedFiltersAndPaginate(); });

    // Inicializar
    applyCombinedFiltersAndPaginate();

    // Modal y acciones de Generar/Vaciar plantel
    const btnMostrarGenerar = document.getElementById('btnMostrarGenerar');
    const btnVaciarPlantel = document.getElementById('btnVaciarPlantel');
    const btnActualizar = document.getElementById('btnActualizar');
    const modalGenerar = document.getElementById('modalGenerar');
    const btnGenerarCancelar = document.getElementById('btnGenerarCancelar');
    const btnGenerarConfirmar = document.getElementById('btnGenerarConfirmar');
    const generarFeedback = document.getElementById('generarFeedback');
    const generarSpinner = document.getElementById('generarSpinner');
    const inputCantidadGenerar = document.getElementById('inputCantidadGenerar');

    // DEBUG: Verificar que todos los elementos existen
    console.log('DEBUG - Elementos del modal:');
    console.log('btnMostrarGenerar:', btnMostrarGenerar);
    console.log('modalGenerar:', modalGenerar);
    console.log('btnGenerarConfirmar:', btnGenerarConfirmar);
    console.log('inputCantidadGenerar:', inputCantidadGenerar);

    // Conectar el botón actualizar
    if (btnActualizar) {
        btnActualizar.addEventListener('click', actualizarPlantel);
    }

    function abrirModalGenerar() {
        console.log('DEBUG - Abriendo modal generar plantel');
        if (modalGenerar) {
            modalGenerar.style.display = 'flex';
            console.log('DEBUG - Modal mostrado');
        } else {
            console.error('DEBUG - ERROR: modalGenerar no encontrado');
        }
        if (generarFeedback) generarFeedback.style.display = 'none';
        if (generarSpinner) generarSpinner.style.display = 'none';
        if (inputCantidadGenerar) inputCantidadGenerar.value = '';
    }

    function cerrarModalGenerar() {
        modalGenerar.style.display = 'none';
    }

    if (btnMostrarGenerar) {
        console.log('DEBUG - Event listener agregado a btnMostrarGenerar');
        btnMostrarGenerar.addEventListener('click', abrirModalGenerar);
    } else {
        console.error('DEBUG - ERROR: btnMostrarGenerar no encontrado');
    }
    if (btnGenerarCancelar) btnGenerarCancelar.addEventListener('click', cerrarModalGenerar);

    if (btnGenerarConfirmar) {
        console.log('DEBUG - Event listener agregado a btnGenerarConfirmar');
        btnGenerarConfirmar.addEventListener('click', function () {
            console.log('DEBUG - Botón generar confirmar clickeado');
            let cantidadSeleccionada = parseInt(inputCantidadGenerar.value, 10);
            console.log('DEBUG - Cantidad seleccionada:', cantidadSeleccionada);
            if (!cantidadSeleccionada || cantidadSeleccionada <= 0) {
                alert('Por favor, introduzca una cantidad válida mayor que cero.');
                return;
            }
            console.log('DEBUG - Iniciando generación de plantel...');
            if (generarSpinner) generarSpinner.style.display = 'block';
            btnGenerarConfirmar.disabled = true;

            fetch('/generar-plantel/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({ cantidad: cantidadSeleccionada })
            }).then(resp => {
                console.log('DEBUG - Respuesta del servidor:', resp.status);
                return resp.json().then(js => ({ ok: resp.ok, status: resp.status, body: js }));
            })
            .then(res => {
                console.log('DEBUG - Respuesta procesada:', res);
                if (generarSpinner) generarSpinner.style.display = 'none';
                btnGenerarConfirmar.disabled = false;
                if (res.ok) {
                    if (generarFeedback) {
                        generarFeedback.style.display = 'block';
                        generarFeedback.textContent = 'Generados: ' + (res.body.created_count || 0) + '. Recargando...';
                    }
                    setTimeout(() => location.reload(), 800);
                } else {
                    if (generarFeedback) {
                        generarFeedback.style.display = 'block';
                        generarFeedback.textContent = 'Error: ' + (res.body.error || JSON.stringify(res.body));
                    }
                }
            })
            .catch(err => {
                console.error('DEBUG - Error en fetch:', err);
                if (generarSpinner) generarSpinner.style.display = 'none';
                btnGenerarConfirmar.disabled = false;
                if (generarFeedback) {
                    generarFeedback.style.display = 'block';
                    generarFeedback.textContent = 'Error de conexión: ' + err.message;
                }
            });
        });
    } else {
        console.error('DEBUG - ERROR: btnGenerarConfirmar no encontrado');
    }


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
