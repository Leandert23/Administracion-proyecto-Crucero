(function() {
    // Helper para obtener CSRF desde la cookie (Django)
    function getCSRFToken(){
        const name = 'csrftoken=';
        const decoded = decodeURIComponent(document.cookie || '');
        const parts = decoded.split(';');
        for(let p of parts){
            p = p.trim();
            if(p.startsWith(name)) return p.substring(name.length);
        }
        return '';
    }

    // Sistema simple de notificaciones (toast)
    function ensureToastStyles(){
        if(document.getElementById('toast-styles')) return;
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
        #toast-container{position:fixed;top:20px;right:20px;z-index:2500;display:flex;flex-direction:column;gap:10px;max-width:320px;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
        .toast-item{display:flex;align-items:flex-start;gap:10px;padding:12px 14px;border-radius:10px;box-shadow:0 6px 18px -6px rgba(0,0,0,.25);background:#1e293b;color:#fff;font-size:.8rem;line-height:1.4;position:relative;overflow:hidden;animation:toastIn .35s ease;}
        .toast-item.success{background:#16a34a;}
        .toast-item.error{background:#dc2626;}
        .toast-item.info{background:#2563eb;}
        .toast-item.warning{background:#d97706;}
        .toast-item .toast-close{cursor:pointer;margin-left:4px;font-weight:600;opacity:.8;}
        .toast-item .toast-close:hover{opacity:1;}
        .toast-progress{position:absolute;left:0;bottom:0;height:3px;background:rgba(255,255,255,.55);width:100%;transform-origin:left;animation:toastProgress 4s linear forwards;}
        @keyframes toastIn{from{transform:translateY(-6px) scale(.95);opacity:0;}to{transform:translateY(0) scale(1);opacity:1;}}
        @keyframes toastOut{to{transform:translateY(-6px);opacity:0;}}
        @keyframes toastProgress{to{transform:scaleX(0);}}
        `;
        document.head.appendChild(style);
    }
    function getToastContainer(){
        let c = document.getElementById('toast-container');
        if(!c){
            c = document.createElement('div');
            c.id='toast-container';
            document.body.appendChild(c);
        }
        return c;
    }
    function showToast(type, message, opts={}){
        ensureToastStyles();
        const container = getToastContainer();
        const el = document.createElement('div');
        el.className = `toast-item ${type||'info'}`;
        el.setAttribute('role','status');
        el.innerHTML = `<div class="toast-msg">${message||''}</div><div class="toast-close" aria-label="Cerrar">×</div><div class="toast-progress"></div>`;
        container.appendChild(el);
        const ttl = opts.ttl || 4000;
        const remove = () => {
            if(el._removing) return; el._removing = true;
            el.style.animation = 'toastOut .25s forwards';
            setTimeout(()=>{ try{ el.remove(); }catch{} },250);
        };
        el.querySelector('.toast-close').addEventListener('click', remove);
        setTimeout(remove, ttl);
        return el;
    }
    const InventarioManager = {
        currentPage: 1,
        activeFilters: {},
        abortController: null,
        debounceTimeout: null,
        lastSearchText: '',

        loadInventoryPage(page) {
            this.currentPage = page;
            this.showLoading(true);

            const searchText = this.getSearchText();
            const previousType = this.activeFilters.tipo ? this.activeFilters.tipo : undefined;
            
            this.activeFilters = { busqueda: searchText };
            if (previousType) this.activeFilters.tipo = previousType;

            const parameters = this.buildParameters(page, searchText);

            if (this.abortController) {
                try {
                    this.abortController.abort();
                } catch (error) {}
            }

            this.abortController = new AbortController();

            fetch(`inventario/paginas-producto/?${parameters.toString()}`, {
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                signal: this.abortController.signal
            })
            .then(response => response.json())
            .then(data => this.processResponse(data))
            .catch(error => this.handleError(error))
            .finally(() => this.showLoading(false));
        },

        getSearchText() {
            const searchInput = document.getElementById('inventario-buscar');
            return searchInput ? searchInput.value : '';
        },

        buildParameters(page, searchText) {
            const rootElement = document.getElementById('almacen-root');
            const cruiseId = rootElement ? rootElement.dataset.cruceroId : '';
            
            const parameters = new URLSearchParams({
                page: page,
                crucero_id: cruiseId
            });

            if (searchText) parameters.append('busqueda', searchText);
            if (this.activeFilters.tipo) parameters.append('tipo', this.activeFilters.tipo);

            return parameters;
        },

        processResponse(data) {
            if (data.success) {
                this.updateInterface(data);
            } else {
                this.showError('Error al cargar los datos');
            }
        },

        updateInterface(data) {
            const tableContainer = document.getElementById('table-container');
            const tableFooter = document.getElementById('table-footer');
            
            if (tableContainer) tableContainer.innerHTML = data.tabla_html;
            if (tableFooter) tableFooter.innerHTML = data.paginacion_html;
            this.bindViewButtons();
            this.bindEditButtons();
            this.bindDeleteButtons();
        },

        handleError(error) {
            console.error('Error loading inventory:', error);
            this.showError('Error de conexión');
        },

        applyFilters() {
            this.loadInventoryPage(1);
        },

        clearFilters() {
            const searchInput = document.getElementById('inputBusqueda') || document.getElementById('inventario-buscar');
            if (searchInput) searchInput.value = '';
            this.applyFilters();
        },

        showLoading(show) {
            const tableContainer = document.getElementById('table-container');
            const tableFooter = document.getElementById('table-footer');
            
            if (show) {
                if (tableContainer) {
                    tableContainer.innerHTML = `
                        <div class="text-center py-5">
                            <div class="spinner-border text-primary"></div>
                            <p class="mt-2">Cargando productos...</p>
                        </div>`;
                }
                if (tableFooter) tableFooter.innerHTML = '';
            }
        },

        showError(message) {
            const tableContainer = document.getElementById('table-container');
            if (!tableContainer) return;
            
            tableContainer.innerHTML = `
                <div class="alert alert-danger text-center">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p class="mt-2">${message}</p>
                    <button class="btn btn-sm btn-outline-danger" onclick="InventarioManager.loadInventoryPage(${this.currentPage})">
                        Reintentar
                    </button>
                </div>`;
        },

        initializeLiveSearch() {
            const searchInput = document.getElementById('inventario-buscar');
            if (!searchInput) return;
            
            searchInput.addEventListener('input', () => {
                const currentValue = searchInput.value.trim();
                
                if (currentValue === this.lastSearchText) return;
                
                if (this.debounceTimeout) clearTimeout(this.debounceTimeout);
                
                if (currentValue.length > 0 && currentValue.length < 2) return;
                
                this.debounceTimeout = setTimeout(() => {
                    this.lastSearchText = currentValue;
                    this.loadInventoryPage(1);
                }, 400);
            });
        },

        initializeTypeFilters() {
            const filterContainer = document.getElementById('inventario-filtros');
            if (!filterContainer) return;

            filterContainer.addEventListener('click', event => {
                const filterButton = event.target.closest('.filter-btn');
                if (!filterButton) return;

                const filterType = filterButton.dataset.filter; // Ej: 'ALIMENTOS_FRESCOS', 'BEBIDAS', 'ALL'
                if (!filterType) return;

                filterContainer.querySelectorAll('.filter-btn').forEach(button => button.classList.remove('active'));
                filterButton.classList.add('active');

                this.activeFilters = { busqueda: this.getSearchText() };
                if (filterType !== 'ALL') {
                    // El backend espera el nombre del tipo exactamente como está en el modelo
                    this.activeFilters.tipo = filterType;
                }

                const filterInfo = document.getElementById('filter-active-text');
                if (filterInfo) {
                    if (filterType === 'ALL') {
                        filterInfo.textContent = 'Mostrando todos los productos';
                    } else {
                        // Reemplazar guiones bajos por espacios y capitalizar mínimamente
                        const legible = filterType.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
                        filterInfo.textContent = `Mostrando productos de ${legible}`;
                    }
                }

                this.loadInventoryPage(1);
            });
        },

        bindViewButtons() {
            const container = document.getElementById('table-container');
            if (!container) return;
            const buttons = container.querySelectorAll('.action-view[data-id]');
            buttons.forEach(btn => {
                if (btn.dataset.lotesBound) return;
                btn.dataset.lotesBound = '1';
                btn.addEventListener('click', () => {
                    const id = btn.getAttribute('data-id');
                    if (!id) return;
                    if (window.AlmacenLotes) {
                        window.GestorLotes.abrir(id);
                    }
                });
            });
        },

        bindEditButtons() {
            const container = document.getElementById('table-container');
            if (!container) return;
            const buttons = container.querySelectorAll('.action-edit[data-id]');
            buttons.forEach(btn => {
                if (btn.dataset.editBound) return;
                btn.dataset.editBound = '1';
                btn.addEventListener('click', () => {
                    const id = btn.getAttribute('data-id');
                    if (!id) return;
                    this.editarProducto(id);
                });
            });
        },

    editarProducto(id) {
            fetch(`inventario/producto/?id=${id}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' }})
                .then(r => r.json())
                .then(data => {
                    if(!data.success) return;
                    const f = document.getElementById('form-crear-producto');
                    if(!f) return;
                    f.querySelector('#id_nombre').value = data.producto.nombre || '';
                    f.querySelector('#id_tipo').value = data.producto.tipo || '';
            // Disparar cambio para que el gestor del formulario regenere subtipos
            try { f.querySelector('#id_tipo').dispatchEvent(new Event('change')); } catch(e) {}
                    if(data.producto.subtipo) f.querySelector('#id_subtipo').value = data.producto.subtipo;
                    f.querySelector('#id_cantidad_ideal').value = data.producto.cantidad_ideal || 0;
                    f.querySelector('#id_medida').value = data.producto.medida || '';
                    if(data.producto.seccion) f.querySelector('#id_seccion').value = data.producto.seccion;
            // Marcar ambos atributos para compatibilidad
            f.dataset.editandoId = data.producto.id;
            f.dataset.editingId = data.producto.id;
            // Rellenar campo oculto si existe
            const hiddenId = f.querySelector('input[name="producto_id"], #id_producto_edit');
            if (hiddenId) hiddenId.value = data.producto.id;
                    const modal = document.getElementById('modalCrearProducto');
                    if(modal){ modal.style.display='flex'; modal.setAttribute('aria-hidden','false'); }
                })
                .catch(()=>{});
        },

        bindDeleteButtons() {
            const container = document.getElementById('table-container');
            if (!container) return;
            const buttons = container.querySelectorAll('.action-delete[data-id]');
            buttons.forEach(btn => {
                if (btn.dataset.deleteBound) return;
                btn.dataset.deleteBound = '1';
                btn.addEventListener('click', () => {
                    const id = btn.getAttribute('data-id');
                    const row = btn.closest('tr');
                    const name = row ? row.querySelector('.product-name')?.textContent?.trim() : '';
                    this.openDeleteModal(id, name);
                });
            });
        },

        openDeleteModal(id, name) {
            const modal = document.getElementById('modalEliminarProducto');
            if(!modal) return;
            const text = modal.querySelector('#delete-text');
            if(text) text.innerHTML = `¿Seguro que deseas eliminar <strong>${name || 'este producto'}</strong>? Esta acción es irreversible.`;
            const confirmBtn = modal.querySelector('#btnConfirmDeleteProducto');
            if(confirmBtn) confirmBtn.dataset.id = id;
            modal.style.display='flex';
            modal.setAttribute('aria-hidden','false');
            this.setupDeleteModalEvents();
        },

        closeDeleteModal() {
            const modal = document.getElementById('modalEliminarProducto');
            if(!modal) return;
            modal.style.display='none';
            modal.setAttribute('aria-hidden','true');
        },

        setupDeleteModalEvents() {
            if(this._deleteModalBound) return; // bind solo una vez global
            this._deleteModalBound = true;
            const modal = document.getElementById('modalEliminarProducto');
            if(!modal) return;
            modal.addEventListener('click', e => {
                if(e.target.dataset.close==='true'){ this.closeDeleteModal(); }
            });
            const cancel = modal.querySelector('#btnCancelDeleteProducto');
            if(cancel) cancel.addEventListener('click', () => this.closeDeleteModal());
            const confirm = modal.querySelector('#btnConfirmDeleteProducto');
            if(confirm) confirm.addEventListener('click', () => {
                const id = confirm.dataset.id;
                if(!id) return;
                const formData = new FormData();
                formData.append('producto_id', id);
                const csrfToken = getCSRFToken();
                fetch('delete-producto/', {
                    method:'POST',
                    headers:{
                        'X-Requested-With':'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    },
                    body: formData
                })
                .then(r => r.json().then(j => ({ok:r.ok,status:r.status,json:j})))
                .then(res => {
                    if(!res.ok){
                        showToast('error', res.json.mensaje || 'No se pudo eliminar');
                        return;
                    }
                    // Cerrar solo modal de eliminación, mantener modal de inventario abierto
                    this.closeDeleteModal();
                    showToast('success','Producto eliminado');
                    // Remover la fila directamente sin recargar toda la tabla
                    const idEliminado = res.json.producto_id;
                    if(idEliminado){
                        const fila = document.querySelector(`#table-container tr[data-id='${idEliminado}']`);
                        if(fila){
                            const tbody = fila.parentElement;
                            fila.remove();
                            // Si ya no quedan filas con productos, mostrar mensaje vacío
                            if(tbody && !tbody.querySelector('tr[data-id]')){
                                const tr = document.createElement('tr');
                                tr.innerHTML = `<td colspan="6" style="text-align:center; padding:30px; color:#64748b;">Sin productos</td>`;
                                tbody.appendChild(tr);
                            }
                        }
                    }
                })
                .catch(()=>{ showToast('error','Error de red eliminando el producto'); });
            });
            document.addEventListener('keydown', e => {
                if(e.key==='Escape') this.closeDeleteModal();
            });
        }
    };

    window.InventarioManager = InventarioManager;
})();