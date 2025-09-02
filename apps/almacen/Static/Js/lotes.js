(function(){
    const modal = document.getElementById('modalLotesProducto');
    if(!modal) return;
    const bodyEl = modal.querySelector('#lotes-contenido');
    let controller = null;

    const show = () => { modal.style.display = 'flex'; modal.setAttribute('aria-hidden','false'); };
    const hide = () => { modal.style.display = 'none'; modal.setAttribute('aria-hidden','true'); if(bodyEl) bodyEl.innerHTML=''; };
    const setContent = html => { if(bodyEl) bodyEl.innerHTML = html; };
    const loading = () => setContent('<div class="lotes-loading">Cargando...</div>');
    const errorMsg = msg => setContent(`<div class="lotes-error">${msg}</div>`);
    const buildUrl = id => {
        const params = new URLSearchParams({ producto: id });
        return `inventario/lotes/?${params.toString()}`; // relativo al path actual (igual que otros endpoints)
    };

    const fetchLotes = (productoId) => {
        if(!productoId) return Promise.resolve();
        if(controller) controller.abort();
        controller = new AbortController();
        loading();
        return fetch(buildUrl(productoId), { signal: controller.signal, headers:{'X-Requested-With':'XMLHttpRequest'} })
            .then(res => { if(!res.ok) throw new Error('bad_response'); return res.json(); })
            .then(data => { if(data && data.success) setContent(data.html); else errorMsg('No se pudo cargar'); })
            .catch(e => { if(e.name === 'AbortError') return; errorMsg('Error de red'); });
    };

    document.addEventListener('click', e => {
        if(e.target.matches('[data-close="true"]')) hide();
        const btn = e.target.closest('[data-ver-lotes]');
        if(btn){ const id = btn.getAttribute('data-ver-lotes'); if(id){ show(); fetchLotes(id); } }
    });

    window.AlmacenLotes = {
        open(productoId){ show(); if(productoId) fetchLotes(productoId); },
        close: hide,
        load: fetchLotes
    };
})();
