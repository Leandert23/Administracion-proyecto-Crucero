// Gestor genérico de modales (versión en español)
(function(){
    const DISPARADOR_TITULO = 'quick-card-title';
    const registro = {
        inventario: {
            id: 'modalInventario',
            triggers: [ { type: DISPARADOR_TITULO, value: 'inventario' } ],
            display: 'block',
            closeSelectors: ['.inventario-overlay','[data-close="true"]'],
            onOpen(){ if(window.InventarioManager && typeof InventarioManager.loadInventoryPage==='function') InventarioManager.loadInventoryPage(1); },
            onAfterInit(){}
        },
        producto: {
            id: 'modalCrearProducto',
            triggers: ['#btnAgregarProducto','#btnAgregarProductoHeader'],
            display: 'flex',
            closeSelectors: ['[data-close="true"]','#btn-cancelar-producto'],
            onOpen(){},
            onAfterInit(){}
        },
        lote: {
            id: 'modalCrearLote',
            triggers: [ { type: DISPARADOR_TITULO, value: 'entrada de lote' } ],
            display: 'flex',
            closeSelectors: ['[data-close="true"]','#btn-cancelar-lote'],
            onOpen(){
                if(window.LotFormManager){
                    const fn = LotFormManager.init || LotFormManager.initialize;
                    if(typeof fn === 'function') fn.call(LotFormManager);
                }
            },
            onAfterInit(){}
        },
        salida: {
            id: 'modalCrearSalida',
            triggers: [ { type: DISPARADOR_TITULO, value: 'salida de producto' } ],
            display: 'flex',
            closeSelectors: ['[data-close="true"]','#btn-cancelar-salida'],
            onOpen(){
                try {
                    const inp = document.getElementById('buscar_producto_salida');
                    if (inp) setTimeout(()=> inp.focus(), 60);
                } catch(e){ console.warn('No se pudo enfocar input salida', e); }
            },
            onAfterInit(){}
        }
    };

        const GestorModales = {
        configs: registro,
        initialized:false,
        init(){
            if(this.initialized) return; this.initialized=true;
            Object.entries(this.configs).forEach(([clave,cfg])=> this._preparar(clave,cfg));
            this._escGlobal();
            this._aliasLegado();
        },
        _preparar(clave,cfg){
            cfg.element = document.getElementById(cfg.id);
            if(!cfg.element) return;
            (cfg.triggers||[]).forEach(tr=> this._vincularDisparador(clave,cfg,tr));
            cfg.element.addEventListener('click', e=>{ if(this._debeCerrar(cfg,e.target)) this.close(clave); });
        },
        _vincularDisparador(clave,cfg,tr){
            if(typeof tr === 'string'){
                document.querySelectorAll(tr).forEach(el=>{
                    if(!el.dataset._modalBind){
                        el.dataset._modalBind='1';
                        el.addEventListener('click', e=>{ e.preventDefault(); this.open(clave); });
                    }
                });
            } else if(tr.type === DISPARADOR_TITULO){
                document.querySelectorAll('.quick-card').forEach(card=>{
                    const t = card.querySelector('.quick-card__title');
                    if(t && t.textContent.trim().toLowerCase() === tr.value){
                        if(!card.dataset._modalBind){
                            card.dataset._modalBind='1';
                            card.addEventListener('click', e=>{ e.preventDefault(); this.open(clave); });
                        }
                    }
                });
            }
        },
        _debeCerrar(cfg,target){
            if(!target) return false;
            if(target.dataset && target.dataset.close==='true') return true;
            if(target.classList && target.classList.contains('inventario-overlay')) return true;
            if(cfg.closeSelectors) return cfg.closeSelectors.some(sel=> target.matches && target.matches(sel));
            if(target===cfg.element) return true;
            return false;
        },
        open(clave){
            const cfg = this.configs[clave]; if(!cfg||!cfg.element) return;
            cfg.element.style.display = cfg.display || 'flex';
            cfg.element.setAttribute('aria-hidden','false');
            document.body.style.overflow='hidden';
            try{ cfg.onOpen && cfg.onOpen(); }catch(e){ console.warn('error en onOpen modal', clave, e); }
        },
        close(clave){
            const cfg = this.configs[clave]; if(!cfg||!cfg.element) return;
            cfg.element.style.display='none';
            cfg.element.setAttribute('aria-hidden','true');
            document.body.style.overflow='';
        },
        _escGlobal(){
            document.addEventListener('keydown', e=>{
                if(e.key==='Escape'){
                    Object.entries(this.configs).forEach(([k,cfg])=>{ if(cfg.element && cfg.element.getAttribute('aria-hidden')==='false') this.close(k); });
                }
            });
        },
        _aliasLegado(){ /* Eliminado: ya no se crean objetos legacy */ },
        isOpen(clave){
            const cfg=this.configs[clave];
            return !!(cfg && cfg.element && cfg.element.getAttribute('aria-hidden')==='false');
        }
    };

        window.GestorModales = GestorModales;
})();