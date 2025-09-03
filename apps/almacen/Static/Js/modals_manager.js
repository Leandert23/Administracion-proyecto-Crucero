(function() {
    const TIPO_DISPARADOR_TITULO = 'quick-card-title';
    
    const configuracionesModales = {
        inventario: {
            id: 'modalInventario',
            disparadores: [{ tipo: TIPO_DISPARADOR_TITULO, valor: 'inventario' }],
            display: 'block',
            selectoresCierre: ['.inventario-overlay', '[data-close="true"]'],
            alAbrir: function() {
                if (window.InventarioManager && typeof InventarioManager.loadInventoryPage === 'function') {
                    InventarioManager.loadInventoryPage(1);
                }
            }
        },
        producto: {
            id: 'modalCrearProducto',
            disparadores: ['#btnAgregarProducto', '#btnAgregarProductoHeader'],
            display: 'flex',
            selectoresCierre: ['[data-close="true"]', '#btn-cancelar-producto'],
            alAbrir: function() {}
        },
        lote: {
            id: 'modalCrearLote',
            disparadores: [{ tipo: TIPO_DISPARADOR_TITULO, valor: 'entrada de lote' }],
            display: 'flex',
            selectoresCierre: ['[data-close="true"]', '#btn-cancelar-lote'],
            alAbrir: function() {
                if (window.LotFormManager) {
                    const funcionInicializacion = LotFormManager.init || LotFormManager.initialize;
                    if (typeof funcionInicializacion === 'function') {
                        funcionInicializacion.call(LotFormManager);
                    }
                }
            }
        },
        salida: {
            id: 'modalCrearSalida',
            disparadores: [{ tipo: TIPO_DISPARADOR_TITULO, valor: 'salida de producto' }],
            display: 'flex',
            selectoresCierre: ['[data-close="true"]', '#btn-cancelar-salida'],
            alAbrir: function() {
                const inputBusqueda = document.getElementById('buscar_producto_salida');
                if (inputBusqueda) {
                    setTimeout(() => inputBusqueda.focus(), 60);
                }
            }
        },
        merma: {
            id: 'modalCrearMerma',
            disparadores: ['#reportes-card', { tipo: TIPO_DISPARADOR_TITULO, valor: 'reportes de mermas' }],
            display: 'flex',
            selectoresCierre: ['[data-close="true"]', '#btn-cancelar-merma'],
            alAbrir: function() {
                const inputBusqueda = document.getElementById('buscar_producto_merma');
                if (inputBusqueda) {
                    setTimeout(() => inputBusqueda.focus(), 60);
                }
            }
        },
        historial: {
            id: 'modalHistorialMovimientos',
            disparadores: [{ tipo: TIPO_DISPARADOR_TITULO, valor: 'historial de movimientos' }],
            display: 'block',
            selectoresCierre: ['.inventario-overlay', '[data-close="true"]'],
            alAbrir: function() {
                if (window.HistorialManager && typeof HistorialManager.load === 'function') {
                    HistorialManager.load();
                }
            }
        }
    };

    const GestorModales = {
        configuraciones: configuracionesModales,
        inicializado: false,
        
        inicializar: function() {
            if (this.inicializado) return;
            this.inicializado = true;
            
            Object.entries(this.configuraciones).forEach(([clave, configuracion]) => {
                this.prepararModal(clave, configuracion);
            });
            
            this.configurarCierreConTeclaEscape();
        },
        
        prepararModal: function(clave, configuracion) {
            configuracion.elemento = document.getElementById(configuracion.id);
            if (!configuracion.elemento) return;
            
            configuracion.disparadores.forEach(disparador => {
                this.vincularDisparador(clave, configuracion, disparador);
            });
            
            configuracion.elemento.addEventListener('click', evento => {
                if (this.debeCerrarModal(configuracion, evento.target)) {
                    this.cerrar(clave);
                }
            });
        },
        
        vincularDisparador: function(clave, configuracion, disparador) {
            if (typeof disparador === 'string') {
                document.querySelectorAll(disparador).forEach(elemento => {
                    if (!elemento.dataset.modalVinculado) {
                        elemento.dataset.modalVinculado = 'true';
                        elemento.addEventListener('click', evento => {
                            evento.preventDefault();
                            this.abrir(clave);
                        });
                    }
                });
            } else if (disparador.tipo === TIPO_DISPARADOR_TITULO) {
                document.querySelectorAll('.quick-card').forEach(tarjeta => {
                    const titulo = tarjeta.querySelector('.quick-card__title');
                    if (titulo && titulo.textContent.trim().toLowerCase() === disparador.valor) {
                        if (!tarjeta.dataset.modalVinculado) {
                            tarjeta.dataset.modalVinculado = 'true';
                            tarjeta.addEventListener('click', evento => {
                                evento.preventDefault();
                                this.abrir(clave);
                            });
                        }
                    }
                });
            }
        },
        
        debeCerrarModal: function(configuracion, elementoObjetivo) {
            if (!elementoObjetivo) return false;
            
            if (elementoObjetivo.dataset && elementoObjetivo.dataset.close === 'true') return true;
            if (elementoObjetivo.classList && elementoObjetivo.classList.contains('inventario-overlay')) return true;
            
            return configuracion.selectoresCierre.some(selector => {
                return elementoObjetivo.matches && elementoObjetivo.matches(selector);
            });
        },
        
        abrir: function(clave) {
            const configuracion = this.configuraciones[clave];
            if (!configuracion || !configuracion.elemento) return;
            configuracion.elemento.style.display = configuracion.display;
            configuracion.elemento.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
            if (configuracion.alAbrir) {
                configuracion.alAbrir();
            }
        },
        
        cerrar: function(clave) {
            const configuracion = this.configuraciones[clave];
            if (!configuracion || !configuracion.elemento) return;
            
            configuracion.elemento.style.display = 'none';
            configuracion.elemento.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        },
        
        configurarCierreConTeclaEscape: function() {
            document.addEventListener('keydown', evento => {
                if (evento.key === 'Escape') {
                    Object.entries(this.configuraciones).forEach(([clave, configuracion]) => {
                        if (configuracion.elemento && configuracion.elemento.getAttribute('aria-hidden') === 'false') {
                            this.cerrar(clave);
                        }
                    });
                }
            });
        },
        
        estaAbierto: function(clave) {
            const configuracion = this.configuraciones[clave];
            return !!(configuracion && configuracion.elemento && configuracion.elemento.getAttribute('aria-hidden') === 'false');
        }
    };

    window.GestorModales = GestorModales;
})();