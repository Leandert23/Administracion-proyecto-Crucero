(function() {
    const GestorHistorial = {
        paginaActual: 1,
        controladorPeticion: null,
        tiempoEsperaBusqueda: null,
        textoBusquedaAnterior: '',
        filtrosActivos: {},
        urlEndpoint: 'inventario/movimientos/',

        iniciar() {
            this.obtenerElementos();
            if (!this.contenedor) return;
            
            this.configurarBusqueda();
            this.configurarFiltros();
            this.configurarPaginacion();
            this.cargarPagina(1);
        },

        obtenerElementos() {
            this.contenedor = document.querySelector('#modalHistorialMovimientos .table-container');
            this.piePagina = document.querySelector('#modalHistorialMovimientos .table-footer');
            this.campoBusqueda = document.getElementById('historial-buscar');
            this.contenedorFiltros = document.getElementById('historial-filtros');
            this.textoFiltro = document.getElementById('historial-filter-text');
        },

        construirParametros(pagina) {
            const raiz = document.getElementById('almacen-root');
            const idCrucero = raiz ? raiz.dataset.cruceroId : '';
            const parametros = new URLSearchParams({ 
                page: pagina, 
                crucero_id: idCrucero 
            });
            
            const texto = this.campoBusqueda?.value.trim() || '';
            if (texto.length >= 2) parametros.append('busqueda', texto);
            
            if (this.filtrosActivos.tipo) parametros.append('tipo', this.filtrosActivos.tipo);
            if (this.filtrosActivos.rango) parametros.append('rango', this.filtrosActivos.rango);
            
            return parametros;
        },

        cargarPagina(pagina) {
            this.paginaActual = pagina;
            this.mostrarCargando();
            
            if (this.controladorPeticion) {
                this.controladorPeticion.abort();
            }
            
            this.controladorPeticion = new AbortController();
            const parametros = this.construirParametros(pagina);
            
            fetch(`${this.urlEndpoint}?${parametros.toString()}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                signal: this.controladorPeticion.signal
            })
            .then(respuesta => respuesta.json())
            .then(datos => this.procesarRespuesta(datos))
            .catch(error => {
                if (error.name !== 'AbortError') {
                    this.mostrarError('Error al cargar el historial');
                }
            });
        },

        procesarRespuesta(datos) {
            if (!datos?.success) {
                this.mostrarError('No se pudo obtener el historial');
                return;
            }
            
            if (this.contenedor) {
                this.contenedor.innerHTML = datos.tabla_html || '<div class="vacio">Sin datos</div>';
            }
            
            if (this.piePagina && datos.footer_html) {
                this.piePagina.innerHTML = datos.footer_html;
            }
            
            this.configurarBotonesDetalle();
        },

        configurarBusqueda() {
            if (!this.campoBusqueda) return;
            
            this.campoBusqueda.addEventListener('input', () => {
                const texto = this.campoBusqueda.value.trim();
                if (texto === this.textoBusquedaAnterior) return;
                
                clearTimeout(this.tiempoEsperaBusqueda);
                
                if (texto && texto.length < 2) return;
                
                this.tiempoEsperaBusqueda = setTimeout(() => {
                    this.textoBusquedaAnterior = texto;
                    this.cargarPagina(1);
                }, 400);
            });
        },

        configurarFiltros() {
            if (!this.contenedorFiltros) return;
            
            this.contenedorFiltros.addEventListener('click', evento => {
                const boton = evento.target.closest('.filter-btn');
                if (!boton) return;
                
                this.contenedorFiltros.querySelectorAll('.filter-btn').forEach(b => {
                    b.classList.remove('active');
                });
                
                boton.classList.add('active');
                const filtro = boton.dataset.filter;
                this.filtrosActivos = {};
                
                switch (filtro) {
                    case 'entrada': this.filtrosActivos.tipo = 'IN'; break;
                    case 'salida': this.filtrosActivos.tipo = 'OUT'; break;
                    case 'today': this.filtrosActivos.rango = 'today'; break;
                    case 'week': this.filtrosActivos.rango = 'week'; break;
                }
                
                this.actualizarTextoFiltro();
                this.cargarPagina(1);
            });
        },

        actualizarTextoFiltro() {
            if (!this.textoFiltro) return;
            
            let texto = 'Mostrando todos los movimientos';
            
            if (this.filtrosActivos.tipo === 'IN') {
                texto = 'Mostrando entradas';
            } else if (this.filtrosActivos.tipo === 'OUT') {
                texto = 'Mostrando salidas';
            } else if (this.filtrosActivos.rango === 'today') {
                texto = 'Movimientos de hoy';
            } else if (this.filtrosActivos.rango === 'week') {
                texto = 'Movimientos de esta semana';
            }
            
            this.textoFiltro.textContent = texto;
        },

        configurarPaginacion() {
            if (!this.contenedor) return;
            
            const manejarClicPaginacion = (evento) => {
                const boton = evento.target.closest('.pagination-btn[data-page]');
                if (!boton || boton.disabled) return;
                
                const pagina = parseInt(boton.dataset.page, 10);
                if (!isNaN(pagina)) {
                    this.cargarPagina(pagina);
                }
            };
            
            this.contenedor.addEventListener('click', manejarClicPaginacion);
            
            if (this.piePagina) {
                this.piePagina.addEventListener('click', manejarClicPaginacion);
            }
        },

        mostrarCargando() {
            if (!this.contenedor) return;
            
            this.contenedor.innerHTML = `
                <div class="cargando-historial">
                    <span class="spinner-cargando"></span>
                    Cargando movimientos...
                </div>
            `;
            
            if (this.piePagina) {
                this.piePagina.innerHTML = '';
            }
        },

        mostrarError(mensaje) {
            if (!this.contenedor) return;
            
            this.contenedor.innerHTML = `
                <div class="error-historial">
                    <i class="icono-advertencia"></i> ${mensaje}
                    <div class="contenedor-reintentar">
                        <button type="button" class="boton-reintentar" id="reintentarHistorial">
                            Reintentar
                        </button>
                    </div>
                </div>
            `;
            
            const botonReintentar = this.contenedor.querySelector('#reintentarHistorial');
            if (botonReintentar) {
                botonReintentar.addEventListener('click', () => this.cargarPagina(this.paginaActual));
            }
        },

        configurarBotonesDetalle() {
            if (!this.contenedor) return;
            
            const botones = this.contenedor.querySelectorAll('.action-view[data-mov-id]');
            botones.forEach(boton => {
                if (boton.dataset.detalleConfigurado) return;
                
                boton.dataset.detalleConfigurado = 'true';
                boton.addEventListener('click', () => this.abrirDetalle(boton));
            });
        },

        abrirDetalle(boton) {
            const modal = document.getElementById('modalDetalleMovimiento');
            if (!modal) return;
            
            const mapeoDatos = {
                '#mov-detalle-tipo': this.formatearTipo(boton.dataset.tipo),
                '#mov-detalle-producto': boton.dataset.producto || '-',
                '#mov-detalle-lote': boton.dataset.lote || '-',
                '#mov-detalle-cantidad': this.formatearCantidad(boton.dataset),
                '#mov-detalle-fecha': boton.dataset.fecha || '-',
                '#mov-detalle-modulo': boton.dataset.modulo || '-'
            };
            
            Object.entries(mapeoDatos).forEach(([selector, valor]) => {
                const elemento = modal.querySelector(selector);
                if (elemento) elemento.innerHTML = valor;
            });
            
            const descripcion = modal.querySelector('#mov-detalle-descripcion');
            if (descripcion) descripcion.textContent = boton.dataset.descripcion || '-';
            
            modal.style.display = 'flex';
            modal.setAttribute('aria-hidden', 'false');
            
            this.configurarModalDetalle();
        },

        formatearTipo(tipo) {
            if (!tipo) return '-';
            
            let etiqueta = '';
            switch (tipo) {
                case 'IN': etiqueta = 'Entrada'; break;
                case 'OUT': etiqueta = 'Salida'; break;
                case 'NEW': etiqueta = 'Creación'; break;
                default: etiqueta = tipo;
            }
            
            return `${etiqueta} <span class="badge-tipo badge-${tipo}">${tipo}</span>`;
        },

        formatearCantidad(datos) {
            if (!datos || datos.cantidad === undefined || datos.cantidad === '' || datos.cantidad === 'N/A') {
                return 'N/A';
            }
            const unidad = datos.unidad || '';
            return `${datos.cantidad} ${unidad}`.trim();
        },

        configurarModalDetalle() {
            if (this.modalDetalleConfigurado) return;
            
            this.modalDetalleConfigurado = true;
            const modal = document.getElementById('modalDetalleMovimiento');
            if (!modal) return;
            
            modal.addEventListener('click', evento => {
                if (evento.target.dataset.detalleCerrar === 'true') {
                    this.cerrarDetalle();
                }
            });
            
            document.addEventListener('keydown', evento => {
                if (evento.key === 'Escape') {
                    this.cerrarDetalle();
                }
            });
            
            modal.querySelectorAll('[data-detalle-cerrar="true"]').forEach(boton => {
                boton.addEventListener('click', () => this.cerrarDetalle());
            });
        },

        cerrarDetalle() {
            const modal = document.getElementById('modalDetalleMovimiento');
            if (!modal) return;
            
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
    };

    window.GestorHistorial = GestorHistorial;
    
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('modalHistorialMovimientos')) {
            GestorHistorial.iniciar();
        }
    });
})();