(function() {
    const ProductFormManager = {
        formulario: null,
        selectTipo: null,
        selectSubtipo: null,

        OPCIONES_SUBTIPO: {
            COMIDA: ['CADUCABLE', 'NO_CADUCABLE', 'REFRIGERADO', 'NO_REFRIGERADO', 'BEBIDA', 'LICOR'],
            BIENES: ['REPUESTOS', 'LIMPIEZA', 'MEDICOS', 'ACTIVOS']
        },

    init() {
            this.formulario = document.getElementById('form-crear-producto');
            if (!this.formulario) return;

            this.selectTipo = this.formulario.querySelector('#id_tipo');
            this.selectSubtipo = this.formulario.querySelector('#id_subtipo');

            this.configurarEventos();
            this.poblarSubtipos();
        },

        configurarEventos() {
            if (this.selectTipo) {
                this.selectTipo.addEventListener('change', () => this.poblarSubtipos());
            }

            this.formulario.querySelectorAll('.form-field input, .form-field select, .form-field textarea').forEach(control => {
                control.addEventListener('focus', () => control.closest('.form-field').classList.add('focused'));
                control.addEventListener('blur', () => control.closest('.form-field').classList.remove('focused'));
            });

            this.formulario.addEventListener('submit', evento => this.enviarFormulario(evento));
        },

        enviarFormulario(evento) {
            evento.preventDefault();
            this.limpiarErrores();

            const datos = new FormData(this.formulario);
            const editingId = this.formulario.dataset.editingId || '';
            if(editingId){ datos.append('producto_id', editingId); }
            const url = editingId ? this.formulario.dataset.updateUrl : this.formulario.action;
            fetch(url, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: datos
            })
            .then(respuesta => respuesta.json().then(json => ({ ok: respuesta.ok, status: respuesta.status, json })))
            .then(resultado => this.procesarRespuesta(resultado))
            .catch(error => console.error('Error al crear producto', error));
        },

        poblarSubtipos() {
            if (!this.selectTipo || !this.selectSubtipo) return;

            const tipoSeleccionado = this.selectTipo.value || null;
            this.selectSubtipo.innerHTML = '<option value="" hidden>Opcional...</option>';

            if (!tipoSeleccionado || !this.OPCIONES_SUBTIPO[tipoSeleccionado]) return;

            this.OPCIONES_SUBTIPO[tipoSeleccionado].forEach(subtipo => {
                const opcion = document.createElement('option');
                opcion.value = subtipo;
                opcion.textContent = subtipo.replace('_', ' ');
                this.selectSubtipo.appendChild(opcion);
            });
        },

        limpiarErrores() {
            this.formulario.querySelectorAll('.error-text').forEach(elemento => {
                elemento.textContent = '';
                elemento.hidden = true;
            });
        },

        procesarRespuesta(respuesta) {
            if (!respuesta.ok) {
                const errores = respuesta.json.errors || {};
                Object.entries(errores).forEach(([campo, mensaje]) => {
                    if (campo === '__all__') return;

                    const contenedorError = this.formulario.querySelector(`.form-field[data-field="${campo}"] .error-text`);
                    if (contenedorError) {
                        contenedorError.textContent = mensaje;
                        contenedorError.hidden = false;
                    }
                });
                return;
            }

            this.formulario.reset();
            this.poblarSubtipos();
            this.formulario.dataset.editingId='';
            const hiddenId = document.getElementById('id_producto_edit');
            if(hiddenId) hiddenId.value='';

            const botonCancelar = document.getElementById('btn-cancelar-producto');
            if (botonCancelar) botonCancelar.click();

            try {
                if (window.GestorModales && GestorModales.isOpen && GestorModales.isOpen('inventario') && window.InventarioManager) {
                    const page = InventarioManager.currentPage || 1;
                    InventarioManager.loadInventoryPage(page);
                }
            } catch (error) { console.warn('No se pudo recargar inventario tras crear producto', error); }
        }
    };
    window.ProductFormManager = ProductFormManager;
})();