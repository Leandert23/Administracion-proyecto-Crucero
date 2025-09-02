// Gestor del Historial de Movimientos
(function(){
    const HistorialManager = {
        currentPage: 1,
        abortController: null,
        debounceTimeout: null,
        lastSearchText: '',
        activeFilters: { }, // { tipo: 'IN'|'OUT', rango: 'today'|'week' }
        endpoint: 'inventario/movimientos/', // Ajusta si tu URL real es distinta

        init(){
            this.cache();
            if(!this.container) return;
            this.bindSearch();
            this.bindFilters();
            this.bindPagination();
            this.loadPage(1);
        },
        cache(){
            this.container = document.querySelector('#modalHistorialMovimientos .table-container');
            this.footerExternal = document.querySelector('#modalHistorialMovimientos .table-footer');
            this.searchInput = document.getElementById('historial-buscar');
            this.filtersWrapper = document.getElementById('historial-filtros');
            this.filterInfo = document.getElementById('historial-filter-text');
        },
        buildParams(page){
            const root = document.getElementById('almacen-root');
            const cruceroId = root ? root.dataset.cruceroId : '';
            const p = new URLSearchParams({ page: page, crucero_id: cruceroId });
            const txt = (this.searchInput && this.searchInput.value.trim()) || '';
            if(txt.length >= 2) p.append('busqueda', txt);
            if(this.activeFilters.tipo) p.append('tipo', this.activeFilters.tipo); // IN / OUT
            if(this.activeFilters.rango) p.append('rango', this.activeFilters.rango); // today / week
            return p;
        },
        loadPage(page){
            this.currentPage = page;
            this.showLoading();
            const params = this.buildParams(page);
            if(this.abortController) { try { this.abortController.abort(); } catch(_){} }
            this.abortController = new AbortController();
            fetch(`${this.endpoint}?${params.toString()}`,{
                headers:{'X-Requested-With':'XMLHttpRequest'},
                signal: this.abortController.signal
            })
            .then(r=> r.json())
            .then(data=> this.processResponse(data))
            .catch(err=> { if(err.name !== 'AbortError') this.showError('Error al cargar historial'); });
        },
        processResponse(data){
            if(!data || !data.success){ this.showError('No se pudo obtener el historial'); return; }
            if(!this.container) return;
            this.container.innerHTML = data.tabla_html || '<div class="empty">Sin datos</div>';
            if(this.footerExternal){
                if(data.footer_html){
                    this.footerExternal.innerHTML = data.footer_html;
                } 
            }
            this.bindDetailButtons();
        },
        bindSearch(){
            if(!this.searchInput) return;
            this.searchInput.addEventListener('input', () => {
                const val = this.searchInput.value.trim();
                if(val === this.lastSearchText) return;
                if(this.debounceTimeout) clearTimeout(this.debounceTimeout);
                if(val && val.length < 2) return; // esperar a 2 caracteres
                this.debounceTimeout = setTimeout(()=>{
                    this.lastSearchText = val;
                    this.loadPage(1);
                }, 400);
            });
        },
        bindFilters(){
            if(!this.filtersWrapper) return;
            this.filtersWrapper.addEventListener('click', e => {
                const btn = e.target.closest('.filter-btn');
                if(!btn) return;
                this.filtersWrapper.querySelectorAll('.filter-btn').forEach(b=> b.classList.remove('active'));
                btn.classList.add('active');
                const f = btn.dataset.filter;
                this.activeFilters = {};
                switch(f){
                    case 'entrada': this.activeFilters.tipo = 'IN'; break;
                    case 'salida': this.activeFilters.tipo = 'OUT'; break;
                    case 'today': this.activeFilters.rango = 'today'; break;
                    case 'week': this.activeFilters.rango = 'week'; break;
                }
                this.updateFilterInfo();
                this.loadPage(1);
            });
        },
        updateFilterInfo(){
            if(!this.filterInfo) return;
            let txt = 'Mostrando todos los movimientos';
            if(this.activeFilters.tipo === 'IN') txt = 'Mostrando entradas';
            else if(this.activeFilters.tipo === 'OUT') txt = 'Mostrando salidas';
            else if(this.activeFilters.rango === 'today') txt = 'Movimientos de hoy';
            else if(this.activeFilters.rango === 'week') txt = 'Movimientos de esta semana';
            this.filterInfo.textContent = txt;
        },
        bindPagination(){
            if(!this.container) return;
            this.container.addEventListener('click', e => {
                const btn = e.target.closest('.pagination-btn[data-page]');
                if(!btn || btn.disabled) return;
                const page = parseInt(btn.dataset.page,10);
                if(!isNaN(page)) this.loadPage(page);
            });
            if(this.footerExternal){
                this.footerExternal.addEventListener('click', e => {
                    const btn = e.target.closest('.pagination-btn[data-page]');
                    if(!btn || btn.disabled) return;
                    const page = parseInt(btn.dataset.page,10);
                    if(!isNaN(page)) this.loadPage(page);
                });
            }
        },
        showLoading(){
            if(!this.container) return;
            this.container.innerHTML = `<div class="historial-loading" style="padding:40px;text-align:center;font-size:.8rem;color:#475569;">
                <span class="spinner" style="display:inline-block;width:22px;height:22px;border:3px solid #cbd5e1;border-top-color:#3b82f6;border-radius:50%;animation:spin .8s linear infinite;margin-right:8px;vertical-align:middle;"></span>
                Cargando movimientos...
            </div>`;
            if(this.footerExternal) this.footerExternal.innerHTML = '';
        },
        showError(msg){
            if(!this.container) return;
            this.container.innerHTML = `<div class="historial-error" style="padding:28px;text-align:center;font-size:.8rem;color:#dc2626;">
                <i class="fas fa-exclamation-triangle"></i> ${msg}
                <div style="margin-top:12px;">
                    <button type="button" class="btn btn-secondary" id="retryHistorial">Reintentar</button>
                </div>
            </div>`;
            const retry = this.container.querySelector('#retryHistorial');
            if(retry) retry.addEventListener('click', ()=> this.loadPage(this.currentPage));
        }
        ,bindDetailButtons(){
            if(!this.container) return;
            const buttons = this.container.querySelectorAll('.action-view[data-mov-id]');
            buttons.forEach(btn => {
                if(btn.dataset.detalleBound) return;
                btn.dataset.detalleBound = '1';
                btn.addEventListener('click', () => this.openDetalle(btn));
            });
        }
        ,openDetalle(btn){
            const modal = document.getElementById('modalDetalleMovimiento');
            if(!modal) return;
            const map = {
                '#mov-detalle-tipo': this.formatTipo(btn.dataset.tipo),
                '#mov-detalle-producto': btn.dataset.producto || '-',
                '#mov-detalle-lote': btn.dataset.lote || '-',
                '#mov-detalle-cantidad': this.formatCantidad(btn.dataset),
                '#mov-detalle-fecha': btn.dataset.fecha || '-',
                '#mov-detalle-modulo': btn.dataset.modulo || '-'
            };
            Object.entries(map).forEach(([sel,val]) => {
                const el = modal.querySelector(sel);
                if(el) el.innerHTML = val;
            });
            const desc = modal.querySelector('#mov-detalle-descripcion');
            if(desc) desc.textContent = btn.dataset.descripcion || '-';
            modal.style.display='flex';
            modal.setAttribute('aria-hidden','false');
            this.setupDetalleModal();
        }
        ,formatTipo(tipo){
            if(!tipo) return '-';
            let label = tipo === 'IN' ? 'Entrada' : tipo === 'OUT' ? 'Salida' : tipo === 'NEW' ? 'Creación' : tipo;
            return `${label} <span class="badge-tipo badge-${tipo}">${tipo}</span>`;
        }
        ,formatCantidad(data){
            if(!data || data.cantidad === 'N/A') return 'N/A';
            const unidad = data.unidad || '';
            return `${data.cantidad} ${unidad}`.trim();
        }
        ,setupDetalleModal(){
            if(this._detalleModalBound) return;
            this._detalleModalBound = true;
            const modal = document.getElementById('modalDetalleMovimiento');
            if(!modal) return;
            modal.addEventListener('click', e => { if(e.target.dataset.detalleClose==='true') this.closeDetalle(); });
            document.addEventListener('keydown', e => { if(e.key==='Escape') this.closeDetalle(); });
            modal.querySelectorAll('[data-detalle-close="true"]').forEach(b => b.addEventListener('click', () => this.closeDetalle()));
        }
        ,closeDetalle(){
            const modal = document.getElementById('modalDetalleMovimiento');
            if(!modal) return;
            modal.style.display='none';
            modal.setAttribute('aria-hidden','true');
        }
    };

    window.HistorialManager = HistorialManager;
    document.addEventListener('DOMContentLoaded', () => {
        // Inicializar sólo si existe el modal en DOM (no cargar innecesariamente)
        if(document.getElementById('modalHistorialMovimientos')) HistorialManager.init();
    });
})();

/* CSS helper animation (si no existe en tu hoja principal) */
/* Puedes mover este @keyframes a una hoja CSS si prefieres. */