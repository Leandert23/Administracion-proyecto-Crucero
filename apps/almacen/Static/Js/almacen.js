// ==================================================
// MÓDULO DE SIDEBAR
// ==================================================

const SidebarManager = {
    sidebar: document.querySelector('.sidebar'),
    overlay: document.querySelector('.sidebar-overlay'),
    mobileToggle: document.querySelector('.mobile-menu-toggle'),

    alternarSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('collapsed');
        }
    },

    alternarSidebarMovil() {
        if (!this.sidebar || !this.overlay || !this.mobileToggle) return;
        
        this.sidebar.classList.toggle('open');
        this.overlay.classList.toggle('active');
        this.mobileToggle.classList.toggle('active');
    },

    cerrarSidebarMovil() {
        if (!this.sidebar || !this.overlay || !this.mobileToggle) return;
        
        this.sidebar.classList.remove('open');
        this.overlay.classList.remove('active');
        this.mobileToggle.classList.remove('active');
    }
};

// ==================================================
// MÓDULO DE MODAL DE INVENTARIO
// ==================================================

const ModalInventarioManager = {
    modal: document.getElementById('modalInventario'),
    tarjetasAccesoRapido: document.querySelectorAll('.quick-card'),

    inicializar() {
        if (!this.modal) return;
        
        this.configurarEventosApertura();
    this.configurarEventosCierre();
    },

    configurarEventosApertura() {
        this.tarjetasAccesoRapido.forEach(tarjeta => {
            const titulo = tarjeta.querySelector('.quick-card__title');
            if (titulo && titulo.textContent.trim().toLowerCase() === 'inventario') {
                tarjeta.addEventListener('click', evento => {
                    evento.preventDefault();
                    this.abrirModal();
                });
            }
        });
    },

    configurarEventosCierre() {
        this.modal.addEventListener('click', evento => {
            if (evento.target.dataset.close === 'true' || evento.target.classList.contains('inventario-overlay')) {
                this.cerrarModal();
            }
        });

        document.addEventListener('keydown', evento => {
            if (evento.key === 'Escape' && this.modal.getAttribute('aria-hidden') === 'false') {
                this.cerrarModal();
            }
        });
    },

    abrirModal() {
        this.modal.style.display = 'block';
        this.modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        
        if (typeof cargarPaginaInventario === 'function') {
            cargarPaginaInventario(1);
        }
    },

    cerrarModal() {
        this.modal.style.display = 'none';
        this.modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
};

// ==================================================
// MÓDULO DE MODAL CREAR PRODUCTO
// ==================================================

const ModalCrearProductoManager = {
    modal: document.getElementById('modalCrearProducto'),
    botonAbrir: document.getElementById('btnAgregarProducto'),
    botonAbrirHeader: document.getElementById('btnAgregarProductoHeader'),
    botonCancelar: null,

    inicializar() {
        if (!this.modal) return;
        // Al menos uno de los botones debe existir
        if (!this.botonAbrir && !this.botonAbrirHeader) return;
        this.configurarEventosApertura();
        this.configurarEventosCierre();
        this.configurarObservadorBotones();
    },

    configurarEventosApertura() {
        const triggers = [this.botonAbrir, this.botonAbrirHeader].filter(Boolean);
        triggers.forEach(btn => {
            if (!btn.dataset._crearBind) {
                btn.dataset._crearBind = '1';
                btn.addEventListener('click', evento => {
                    evento.preventDefault();
                    this.abrirModal();
                });
            }
        });
    },

    configurarEventosCierre() {
        this.modal.addEventListener('click', evento => {
            if (evento.target === this.modal || evento.target.dataset.close === 'true') {
                this.cerrarModal();
            }
        });

        document.addEventListener('keydown', evento => {
            if (evento.key === 'Escape' && this.modal.getAttribute('aria-hidden') === 'false') {
                this.cerrarModal();
            }
        });
    },

    configurarObservadorBotones() {
        const observador = new MutationObserver(() => {
            const nuevoBotonCancelar = this.modal.querySelector('#btn-cancelar-producto');
            if (nuevoBotonCancelar && !nuevoBotonCancelar.dataset._modalBind) {
                nuevoBotonCancelar.dataset._modalBind = '1';
                nuevoBotonCancelar.addEventListener('click', evento => {
                    evento.preventDefault();
                    this.cerrarModal();
                });
            }
        });

        observador.observe(this.modal, { subtree: true, childList: true });
    },

    abrirModal() {
        this.modal.style.display = 'flex';
        this.modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    },

    cerrarModal() {
        this.modal.style.display = 'none';
        this.modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
};

// ==================================================
// MÓDULO DE GESTIÓN DE INVENTARIO
// ==================================================

const InventarioManager = {
    paginaActual: 1,
    filtrosActuales: {},
    _abortCtrl: null,
    _debounceId: null,
    _ultimoTexto: '',

    cargarPaginaInventario(pagina) {
        this.paginaActual = pagina;
        this.mostrarCargando(true);
        
        const busqueda = this.obtenerTextoBusqueda();
    // Conservar tipo previamente seleccionado (si existe)
    const tipoPrevio = this.filtrosActuales && this.filtrosActuales.tipo ? this.filtrosActuales.tipo : undefined;
    this.filtrosActuales = { busqueda };
    if (tipoPrevio) this.filtrosActuales.tipo = tipoPrevio;
        
        const parametros = this.construirParametros(pagina, busqueda);
        // Abortar petición previa si existe
        if (this._abortCtrl) {
            try { this._abortCtrl.abort(); } catch(_) {}
        }
        this._abortCtrl = new AbortController();

        fetch(`inventario/modal-ajax/?${parametros.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            signal: this._abortCtrl.signal
        })
        .then(respuesta => respuesta.json())
        .then(datos => this.procesarRespuesta(datos))
        .catch(error => this.manejarError(error))
        .finally(() => this.mostrarCargando(false));
    },

    obtenerTextoBusqueda() {
        const inputBusqueda = document.getElementById('inventario-buscar');
        return inputBusqueda ? inputBusqueda.value : '';
    },

    construirParametros(pagina, busqueda) {
        const raiz = document.getElementById('almacen-root');
        const cruceroId = raiz ? raiz.dataset.cruceroId : '';
        
        const parametros = new URLSearchParams({
            page: pagina,
            crucero_id: cruceroId
        });
        
        if (busqueda) {
            parametros.append('busqueda', busqueda);
        }
        if (this.filtrosActuales && this.filtrosActuales.tipo) {
            parametros.append('tipo', this.filtrosActuales.tipo);
        }
        
        return parametros;
    },

    procesarRespuesta(datos) {
        if (datos.success) {
            this.actualizarInterfaz(datos);
        } else {
            this.mostrarError('Error al cargar los datos');
        }
    },

    actualizarInterfaz(datos) {
        const contenedorTabla = document.getElementById('table-container');
        const pieTabla = document.getElementById('table-footer');
        
        if (contenedorTabla) contenedorTabla.innerHTML = datos.tabla_html;
        if (pieTabla) pieTabla.innerHTML = datos.paginacion_html;
    },

    manejarError(error) {
        console.error('Error:', error);
        this.mostrarError('Error de conexión');
    },

    aplicarFiltros() {
        this.cargarPaginaInventario(1);
    },

    limpiarFiltros() {
        const inputBusqueda = document.getElementById('inputBusqueda') || document.getElementById('inventario-buscar');
        if (inputBusqueda) inputBusqueda.value = '';
        this.aplicarFiltros();
    },

    mostrarCargando(mostrar) {
        const contenedorTabla = document.getElementById('table-container');
        const pieTabla = document.getElementById('table-footer');
        
        if (mostrar) {
            if (contenedorTabla) {
                contenedorTabla.innerHTML = `
                    <div class="text-center py-5">
                        <div class="spinner-border text-primary"></div>
                        <p class="mt-2">Cargando productos...</p>
                    </div>
                `;
            }
            if (pieTabla) pieTabla.innerHTML = '';
        }
    },

    mostrarError(mensaje) {
        const contenedorTabla = document.getElementById('table-container');
        if (!contenedorTabla) return;
        
        contenedorTabla.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="bi bi-exclamation-triangle"></i>
                <p class="mt-2">${mensaje}</p>
                <button class="btn btn-sm btn-outline-danger" onclick="InventarioManager.cargarPaginaInventario(${this.paginaActual})">
                    Reintentar
                </button>
            </div>
        `;
    },
    inicializarBusquedaEnVivo() {
        const input = document.getElementById('inventario-buscar');
        if (!input) return;
        input.addEventListener('input', () => {
            const valor = input.value.trim();
            if (valor === this._ultimoTexto) return; // no cambió
            if (this._debounceId) clearTimeout(this._debounceId);
            // Reglas: si hay texto y es menor a 2 chars, no buscar aún
            if (valor.length > 0 && valor.length < 2) return;
            this._debounceId = setTimeout(() => {
                this._ultimoTexto = valor;
                this.cargarPaginaInventario(1);
            }, 400);
        });
    },
    inicializarFiltrosTipo() {
        const contenedor = document.getElementById('inventario-filtros');
        if (!contenedor) return;
        contenedor.addEventListener('click', (e) => {
            const btn = e.target.closest('.filter-btn');
            if (!btn) return;
            const filtro = btn.dataset.filter;
            if (!filtro) return;
            // Actualizar clases activas
            contenedor.querySelectorAll('.filter-btn').forEach(b=> b.classList.remove('active'));
            btn.classList.add('active');
            // Mapear filtros a tipo
            let tipo = '';
            if (filtro === 'low') tipo = 'COMIDA';
            else if (filtro === 'elec') tipo = 'BIENES';
            // Guardar en filtrosActuales
            const busqueda = this.obtenerTextoBusqueda();
            this.filtrosActuales = { busqueda };
            if (tipo) {
                this.filtrosActuales.tipo = tipo;
            }
            // Actualizar texto informativo
            const info = document.getElementById('filter-active-text');
            if (info) {
                let texto = 'Mostrando todos los productos';
                if (tipo === 'COMIDA') texto = 'Mostrando productos de Comida';
                else if (tipo === 'BIENES') texto = 'Mostrando productos de Bienes';
                info.textContent = texto;
            }
            this.cargarPaginaInventario(1);
        });
    }
};

// ==================================================
// AÑADIDO: gestor formulario crear producto
// ==================================================

const ProductFormManager = {
    form: null,
    tipoSelect: null,
    subtipoSelect: null,
    SUBTIPOS: {
        COMIDA: ['CADUCABLE','NO_CADUCABLE','REFRIGERADO','NO_REFRIGERADO','BEBIDA','LICOR'],
        BIENES: ['REPUESTOS','LIMPIEZA','MEDICOS','ACTIVOS']
    },
    init(){
        this.form = document.getElementById('form-crear-producto');
        if(!this.form) return; // modal aún no cargado
        this.tipoSelect = this.form.querySelector('#id_tipo');
        this.subtipoSelect = this.form.querySelector('#id_subtipo');
        this.bindEvents();
        this.poblarSubtipos();
    },
    bindEvents(){
        if(this.tipoSelect){
            this.tipoSelect.addEventListener('change', ()=> this.poblarSubtipos());
        }
        // focus styling
        this.form.querySelectorAll('.form-field input, .form-field select, .form-field textarea').forEach(ctrl => {
            ctrl.addEventListener('focus', () => ctrl.closest('.form-field').classList.add('focused'));
            ctrl.addEventListener('blur', () => ctrl.closest('.form-field').classList.remove('focused'));
        });
        // submit
        this.form.addEventListener('submit', e => {
            e.preventDefault();
            this.limpiarErrores();
            const fd = new FormData(this.form);
            fetch(this.form.action, { method:'POST', headers:{'X-Requested-With':'XMLHttpRequest'}, body: fd })
                .then(r=>r.json().then(j=>({ok:r.ok,status:r.status,json:j})))
                .then(resp=> this.procesarRespuesta(resp))
                .catch(err=> console.error('Error creando producto', err));
        });
    },
    poblarSubtipos(){
        if(!this.tipoSelect || !this.subtipoSelect) return;
        const tipo = this.tipoSelect.value || null;
        this.subtipoSelect.innerHTML = '<option value="" hidden>Opcional...</option>';
        if(!tipo || !this.SUBTIPOS[tipo]) return;
        this.SUBTIPOS[tipo].forEach(st => {
            const opt = document.createElement('option');
            opt.value = st; opt.textContent = st.replace('_',' ');
            this.subtipoSelect.appendChild(opt);
        });
    },
    limpiarErrores(){
        this.form.querySelectorAll('.error-text').forEach(span=>{ span.textContent=''; span.hidden=true; });
    },
    procesarRespuesta(resp){
        if(!resp.ok){
            const errs = resp.json.errors || {};
            Object.entries(errs).forEach(([field,msg])=>{
                if(field==='__all__') return;
                const container = this.form.querySelector(`.form-field[data-field="${field}"] .error-text`);
                if(container){ container.textContent = msg; container.hidden=false; }
            });
            return;
        }
        this.form.reset();
        this.poblarSubtipos();
        const cancelar = document.getElementById('btn-cancelar-producto');
        if(cancelar) cancelar.click();
        // Recargar inventario en la misma página si el modal de inventario está abierto
        try {
            if (ModalInventarioManager.modal && ModalInventarioManager.modal.getAttribute('aria-hidden') === 'false') {
                const pagina = (typeof InventarioManager !== 'undefined' && InventarioManager.paginaActual) ? InventarioManager.paginaActual : 1;
                InventarioManager.cargarPaginaInventario(pagina);
            }
        } catch(err) { console.warn('No se pudo recargar inventario tras crear producto', err); }
    }
};

// ==================================================
// INICIALIZACIÓN
// ==================================================

function inicializarAplicacion() {
    ModalInventarioManager.inicializar();
    ModalCrearProductoManager.inicializar();
    ProductFormManager.init();
    InventarioManager.inicializarBusquedaEnVivo();
    InventarioManager.inicializarFiltrosTipo();
    // Asignar funciones globales si es necesario
    window.cargarPaginaInventario = (pagina) => InventarioManager.cargarPaginaInventario(pagina);
    window.aplicarFiltrosInventario = () => InventarioManager.aplicarFiltros();
    window.limpiarFiltrosInventario = () => InventarioManager.limpiarFiltros();
}

// Iniciar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', inicializarAplicacion);
