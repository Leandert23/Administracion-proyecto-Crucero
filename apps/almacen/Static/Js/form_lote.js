 (function() {
    const GestorFormularioLote = {
        formulario: null,
        campoIdProducto: null,
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
            this.formulario = document.getElementById('form-crear-lote');
            this.campoIdProducto = document.getElementById('id_producto');
        },
        
        vincularEventoEnvio() {
            if (!this.formulario) return;
            this.formulario.addEventListener('submit', e => { e.preventDefault(); this.enviarFormulario(); });
        },
        
        enviarFormulario() {
            this.limpiarErrores();
            
            if (!this.campoIdProducto.value) {
                this.mostrarErrorProducto();
                return;
            }
            
            const datos = new FormData(this.formulario);
            
            fetch('registrar-lote/', {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                body: datos
            })
            .then(respuesta => respuesta.json().then(datos => ({
                ok: respuesta.ok,
                estado: respuesta.status,
                datos
            })))
            .then(resultado => this.procesarRespuestaEnvio(resultado))
            .catch(error => console.error('Error creando lote', error));
        },
        
        mostrarErrorProducto() {
            const elementoError = this.formulario.querySelector('[data-field="producto"] .error-text');
            if (elementoError) {
                elementoError.textContent = 'Selecciona un producto de la lista';
                elementoError.hidden = false;
            }
        },
        
        procesarRespuestaEnvio(respuesta) {
            if (!respuesta.ok) {
                this.manejarErroresEnvio(respuesta.datos.errores || {});
                return;
            }
            
            this.reiniciarFormulario();
            this.cerrarModal();
            this.recargarInventario();
        },
        
        manejarErroresEnvio(errores) {
            Object.entries(errores).forEach(([campo, mensaje]) => {
                if (campo === '__all__') return;
                
                const elemento = this.formulario.querySelector(`.form-field[data-field="${campo}"] .error-text`);
                if (elemento) {
                    elemento.textContent = mensaje;
                    elemento.hidden = false;
                }
            });
        },
        
        vincularEventosReinicio() {
            this.vincularBotonCancelar();
            this.vincularBotonCerrar();
            this.vincularTeclaEscape();
        },
        
        vincularBotonCancelar() {
            const botonCancelar = document.getElementById('btn-cancelar-lote');
            if (botonCancelar) {
                botonCancelar.addEventListener('click', () => this.reiniciarFormulario());
            }
        },
        
        vincularBotonCerrar() {
            const botonCerrar = document.querySelector('#modalCrearLote [data-close="true"]');
            if (botonCerrar) {
                botonCerrar.addEventListener('click', () => this.reiniciarFormulario());
            }
        },
        
        vincularTeclaEscape() {
            document.addEventListener('keydown', evento => {
                if (evento.key !== 'Escape') return;
                
                const modal = document.getElementById('modalCrearLote');
                if (!modal) return;
                
                const visible = modal.getAttribute('aria-hidden') === 'false' || modal.style.display !== 'none';
                if (visible) this.reiniciarFormulario();
            });
        },
        
        vincularCapturaEscape() {
            document.addEventListener('keydown', evento => {
                if (evento.key !== 'Escape') return;
                if (!window.GestorModales || !GestorModales.isOpen || !GestorModales.isOpen('lote')) return;
                
                this.reiniciarFormulario();
            }, true);
        },
        
        parchearCierreModal() {
            if (!window.GestorModales || this.modalParcheado) return;
            const cerrarOriginal = window.GestorModales.close ? window.GestorModales.close.bind(window.GestorModales) : null;
            if(!cerrarOriginal) return;
            window.GestorModales.close = clave => {
                if (clave === 'lote') this.reiniciarFormulario();
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
            this.formulario.querySelectorAll('.error-text').forEach(el => { el.textContent=''; el.hidden = true; });
        },
        
        cerrarModal() {
            const botonCancelar = document.getElementById('btn-cancelar-lote');
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
                    // fallback si en algún momento se localiza también InventarioManager
                    InventarioManager.cargarPaginaInventario(pagina);
                }
            } catch (error) {
                console.warn('No se pudo recargar inventario', error);
            }
        }
    };
    
    window.GestorFormularioLote = GestorFormularioLote;
    document.addEventListener('DOMContentLoaded', () => GestorFormularioLote.inicializar());
})();