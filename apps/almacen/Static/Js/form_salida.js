 (function() {
    const GestorFormularioSalida = {
        formulario: null,
        campoIdProducto: null,
        campoCantidad: null,
        campoModulo: null,
        modalParcheado: false,

        inicializar() {
            this.obtenerElementos();
            if (!this.formulario) return;
            this.vincularEventoEnvio();
            this.vincularEventosReinicio();
            this.vincularCapturaEscape();
            this.parchearCierreModal();
        },

        obtenerElementos() {
            this.formulario = document.getElementById('form-crear-salida');
            this.campoIdProducto = document.getElementById('id_producto_salida');
            this.campoCantidad = document.getElementById('id_cantidad_productos_salida');
            this.campoModulo = document.getElementById('id_modulo_entrega');
        },

        vincularEventoEnvio() { 
            if (this.formulario) this.formulario.addEventListener('submit', e => { e.preventDefault(); this.enviarFormulario(); }); 
        },

        validarCamposPrevios() {
            let valido = true;
            if (!this.campoIdProducto || !this.campoIdProducto.value) { 
                this.mostrarErrorProducto(); 
                valido = false; 
            }
            if (this.campoCantidad && (!this.campoCantidad.value || parseInt(this.campoCantidad.value, 10) <= 0)) {
                this.mostrarErrorCampo('cantidad_productos', 'Ingresa una cantidad válida (>0)');
                valido = false;
            }
            if (this.campoModulo && !this.campoModulo.value.trim()) {
                this.mostrarErrorCampo('modulo_entrega', 'Indica el módulo de entrega');
                valido = false;
            }
            return valido;
        },

        enviarFormulario() {
            this.limpiarErrores();
            if (!this.validarCamposPrevios()) return;
            const datos = new FormData(this.formulario);
            fetch('registrar-salida/', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: datos
            })
            .then(r => r.json().then(d => ({ ok: r.ok, estado: r.status, datos: d })))
            .then(res => this.procesarRespuestaEnvio(res))
            .catch(err => console.error('Error creando salida', err));
        },

        mostrarErrorProducto() { 
            this.mostrarErrorCampo('producto', 'Selecciona un producto de la lista'); 
        },

        mostrarErrorCampo(campo, mensaje) {
            const el = this.formulario.querySelector(`.form-field[data-field="${campo}"] .error-text`);
            if (el) { 
                el.textContent = mensaje; 
                el.hidden = false; 
            }
        },

        procesarRespuestaEnvio(respuesta) {
            const { ok, datos } = respuesta;
            if (ok && datos && datos.success) {
                this.reiniciarFormulario();
                this.cerrarModal();
                this.recargarInventario();
                return;
            }

            if (datos && datos.error) {
                this.manejarErrorCodigo(datos);
            } else if (datos && datos.errores) {
                this.manejarErroresCampos(datos.errores);
            } else {
                this.mostrarErrorGeneral('Error desconocido al registrar la salida');
            }
        },

        manejarErrorCodigo(info) {
            const codigo = info.error || '';
            const mensaje = info.mensaje || 'Error al procesar la salida';
            const detalle = info.detalle ? ` (${info.detalle})` : '';
            
            const mapaCampo = {
                'producto_requerido': 'producto',
                'producto_no_encontrado': 'producto',
                'cantidad_invalida': 'cantidad_productos',
                'cantidad_no_valida': 'cantidad_productos',
                'stock_insuficiente': 'cantidad_productos',
                'operacion_invalida': 'cantidad_productos'
            };
            
            const campo = mapaCampo[codigo];
            if (campo) {
                this.mostrarErrorCampo(campo, mensaje + detalle);
            } else {
                this.mostrarErrorGeneral(mensaje + detalle);
            }
        },

        manejarErroresCampos(errores) {
            Object.entries(errores).forEach(([campo, mensaje]) => {
                if (campo === '__all__') {
                    this.mostrarErrorGeneral(mensaje);
                } else {
                    this.mostrarErrorCampo(campo, mensaje);
                }
            });
        },

        mostrarErrorGeneral(mensaje) {
            let cont = this.formulario.querySelector('.form-error-general');
            if (!cont) {
                cont = document.createElement('div');
                cont.className = 'form-error-general';
                cont.style.color = '#b3261e';
                cont.style.marginBottom = '8px';
                this.formulario.prepend(cont);
            }
            cont.textContent = mensaje;
        },

        vincularEventosReinicio() { 
            this.vincularBotonCancelar(); 
            this.vincularBotonCerrar(); 
            this.vincularTeclaEscape(); 
        },

        vincularBotonCancelar() { 
            const b = document.getElementById('btn-cancelar-salida'); 
            if (b) b.addEventListener('click', () => this.reiniciarFormulario()); 
        },

        vincularBotonCerrar() {
            const btn = document.querySelector('#modalCrearSalida [data-close="true"]');
            if (btn) btn.addEventListener('click', () => this.reiniciarFormulario());
        },

        vincularTeclaEscape() {
            document.addEventListener('keydown', e => {
                if (e.key !== 'Escape') return;
                const modal = document.getElementById('modalCrearSalida');
                if (!modal) return;
                const visible = modal.getAttribute('aria-hidden') === 'false' || modal.style.display !== 'none';
                if (visible) this.reiniciarFormulario();
            });
        },

        vincularCapturaEscape() {
            document.addEventListener('keydown', e => {
                if (e.key !== 'Escape') return;
                if (!window.GestorModales || !GestorModales.isOpen || !GestorModales.isOpen('salida')) return;
                this.reiniciarFormulario();
            }, true);
        },

        parchearCierreModal() {
            if (!window.GestorModales || this.modalParcheado) return;
            const cerrarOriginal = window.GestorModales.close ? window.GestorModales.close.bind(window.GestorModales) : null;
            if (!cerrarOriginal) return;
            window.GestorModales.close = clave => {
                if (clave === 'salida') this.reiniciarFormulario();
                return cerrarOriginal(clave);
            };
            this.modalParcheado = true;
        },

        reiniciarFormulario() {
            if (!this.formulario) return;
            this.formulario.reset();
            if (this.campoIdProducto) this.campoIdProducto.value = '';
            this.limpiarErrores();
        },

        limpiarErrores() {
            this.formulario.querySelectorAll('.error-text').forEach(el => { 
                el.textContent = ''; 
                el.hidden = true; 
            });
        },

        cerrarModal() {
            const botonCancelar = document.getElementById('btn-cancelar-salida');
            if (botonCancelar) botonCancelar.click();
        },

        recargarInventario() {
            try {
                if (!window.GestorModales || !GestorModales.isOpen || !GestorModales.isOpen('inventario')) return;
                if (!window.InventarioManager) return;
                const pagina = InventarioManager.currentPage || 1;
                if (typeof InventarioManager.loadInventoryPage === 'function') {
                    InventarioManager.loadInventoryPage(pagina);
                } else if (typeof InventarioManager.cargarPaginaInventario === 'function') {
                    InventarioManager.cargarPaginaInventario(pagina);
                }
            } catch (e) { 
                console.warn('No se pudo recargar inventario', e); 
            }
        },

    mostrarErrorBusqueda() {}
    };

    window.GestorFormularioSalida = GestorFormularioSalida;
    document.addEventListener('DOMContentLoaded', () => GestorFormularioSalida.inicializar());
})();