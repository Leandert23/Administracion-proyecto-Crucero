// Módulo Pedidos (fase UI local antes de backend)
(function(){
    let pedidos = []; // activos (pendiente, en_proceso)
    let historial = []; // completados o cancelados
    let seq = 1;
    let pedidoSeleccionado = null;
    let proximoEstado = null;

    const ESTADOS = ['pendiente','en_proceso','completado'];

    // ----- Multi productos (estado in-memory) -----
    let catalogoProductos = [];
    const cantidadesEstado = new Map(); // productoId -> { id, nombre, tipo, precio, cantidad }
    function parseListaProductos(){ return Array.from(cantidadesEstado.values()); }

    function syncCajaCantidades(){
        const cont = document.getElementById('pedido-productos-cantidades');
        if(!cont) return;
        if(!cantidadesEstado.size){ cont.innerHTML='<div style="font-size:.65rem; color:#64748b;">(Sin productos seleccionados)</div>'; return; }
        const frag = document.createDocumentFragment();
        cantidadesEstado.forEach(p=>{
            const row = document.createElement('div');
            row.className='producto-cant-row';
            row.style.display='flex';
            row.style.alignItems='center';
            row.style.gap='6px';
            row.style.fontSize='.7rem';
            row.dataset.id=p.id;
            row.innerHTML=`<span style="flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.nombre}</span>
                <input type="number" min="1" value="${p.cantidad}" style="width:60px; padding:2px 4px; font-size:.65rem;" />
                <button type="button" aria-label="Quitar" style="background:#ef4444; color:#fff; border:none; border-radius:4px; padding:2px 6px; font-size:.65rem; cursor:pointer;">✕</button>`;
            const inp = row.querySelector('input');
            inp.addEventListener('input', ()=>{ let v=parseInt(inp.value,10); if(isNaN(v)||v<1){ v=1; inp.value=1;} p.cantidad=v; calcularDisponibilidadResumen(); });
            row.querySelector('button').addEventListener('click',()=>{ cantidadesEstado.delete(p.id); marcarSelectProductos(); syncCajaCantidades(); });
            frag.appendChild(row);
        });
        cont.innerHTML='';
        cont.appendChild(frag);
    // Recalcular disponibilidad global (resumen)
    calcularDisponibilidadResumen();
    }

    function marcarSelectProductos(){
        const sel = document.getElementById('pedido-productos');
        if(!sel) return;
        Array.from(sel.options).forEach(opt=>{ const pid=parseInt(opt.value,10); opt.selected = cantidadesEstado.has(pid); });
    }

    function onChangeSelectProductos(){
        const sel = document.getElementById('pedido-productos');
        if(!sel) return;
        const actuales = new Set(Array.from(sel.selectedOptions).map(o=> parseInt(o.value,10)));
        // Quitar los que ya no están
        Array.from(cantidadesEstado.keys()).forEach(id=>{ if(!actuales.has(id)) cantidadesEstado.delete(id); });
        // Añadir nuevos
        Array.from(sel.selectedOptions).forEach(o=>{
            const id = parseInt(o.value,10); if(!id) return;
            if(!cantidadesEstado.has(id)){
                cantidadesEstado.set(id, { id, nombre:o.textContent.trim(), tipo:o.dataset.tipo||'', precio: parseFloat(o.dataset.precio||'0')||0, cantidad:1 });
            }
        });
    syncCajaCantidades();
    }
    async function cargarCatalogoProductos(){
        const sel = document.getElementById('pedido-productos');
        if(!sel) return;
        sel.innerHTML='<option disabled>Cargando...</option>';
        try {
            const r = await fetch('/bar/productos-bar/');
            const data = await r.json();
            catalogoProductos = Array.isArray(data)? data: [];
            if(!catalogoProductos.length){ sel.innerHTML='<option disabled>(Sin productos)</option>'; return; }
            sel.innerHTML='';
            catalogoProductos.forEach(p=>{
                const opt=document.createElement('option');
                opt.value=p.id; opt.textContent=p.nombre + (p.tipo==='pago'&&p.precio?` ($${p.precio})`:'' );
                opt.dataset.tipo=p.tipo; opt.dataset.precio=p.precio||0;
                sel.appendChild(opt);
            });
        } catch(err){
            console.error('Error cargando productos bar', err);
            sel.innerHTML='<option disabled>Error cargando</option>';
        }
    }

    async function calcularDisponibilidadResumen(){
        const box = document.getElementById('resumen-disponibilidad');
        if(!box) return;
        const lista = parseListaProductos();
        if(!lista.length){ box.innerHTML = '<em>(Selecciona productos para ver disponibilidad)</em>'; return; }
        try {
            const r = await fetch('/bar/disponibilidad-productos/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ productos: lista.map(p=>({ producto_id:p.id, cantidad:p.cantidad })) }) });
            const data = await r.json();
            if(!r.ok || !data.success) throw new Error((data && data.error) || 'Error');
            const map = new Map((data.items||[]).map(it=> [it.producto_id, it] ));
            const html = lista.map(p=>{
                const it = map.get(p.id);
                if(!it){ return `<div>- ${escapeHtml(p.nombre)}: <span style="color:#64748b">n/d</span></div>`; }
                let disp = it.disponible;
                const dispTxt = (disp<0)? 'sin receta' : String(disp);
                const puede = (disp<0) || (disp>=p.cantidad);
                return `<div>- ${escapeHtml(p.nombre)}: <strong style="color:${puede?'#166534':'#b91c1c'}">${dispTxt}</strong> ${disp>=0?`(sol: ${p.cantidad})`:''}</div>`;
            }).join('');
            box.innerHTML = html;
        } catch(err){
            console.warn('Disponibilidad fallo', err);
            box.innerHTML = '<span style="color:#b91c1c">No se pudo calcular disponibilidad.</span>';
        }
    }

    function escapeHtml(str){
        if(str==null) return '';
        return String(str)
            .replace(/&/g,'&amp;')
            .replace(/</g,'&lt;')
            .replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;')
            .replace(/'/g,'&#39;');
    }

    function htmlToEl(html){
        const t = document.createElement('template');
        t.innerHTML = html.trim();
        return t.content.firstElementChild;
    }

    function buildCard(p, esHistorial){
        const productosTxt = (p.productos||[]).map(d=> typeof d==='string'? d : `${escapeHtml(d.nombre)} x${d.cantidad}`).join(', ');
        const totalTxt = (p.total!=null)? Number(p.total).toFixed(2) : (p.productos||[]).reduce((a,d)=> a + ((parseFloat(d.precio)||0)*(parseInt(d.cantidad,10)||0)), 0).toFixed(2);
        const btns = esHistorial? '' : `
            <div class="pedido-actions">
                <button class="btn-secundario" data-accion="estado" data-id="${p.id}">Estado</button>
                <button class="btn-peligro" data-accion="eliminar" data-id="${p.id}" ${p.estado!=='pendiente'?'disabled':''}>Eliminar</button>
            </div>`;
        const card = htmlToEl(`
            <div class="pedido-card" data-id="${p.id}">
                <div class="pedido-head">
                    <div class="pedido-id">#${p.id}</div>
                    <div class="pedido-estado ${escapeHtml(p.estado)}">${escapeHtml(p.estado.replace('_',' '))}</div>
                </div>
                <div class="pedido-body">
                    <div class="pedido-linea"><strong>Cliente:</strong> ${p.cliente_id??'-'}</div>
                    <div class="pedido-linea"><strong>Empleado:</strong> ${p.empleado_id??'-'}</div>
                    <div class="pedido-linea"><strong>${p.tipo_consumo==='camarote'?'Habitación':'Lugar'}:</strong> ${escapeHtml(p.lugarentrega_nombre||p.habitacion_nombre||'-')}</div>
                    <div class="pedido-linea"><strong>Productos:</strong> ${productosTxt||'-'}</div>
                    <div class="pedido-linea"><strong>Total:</strong> $${totalTxt}</div>
                </div>
                ${btns}
            </div>`);
        return card;
    }

    function renderListas(){
        const activosCont = document.getElementById('pedidos-lista-activos');
        const histCont = document.getElementById('pedidos-lista-historial');
        if(activosCont){
            const existentes = new Map(Array.from(activosCont.children).filter(el=>el.classList.contains('pedido-card')).map(el=>[parseInt(el.dataset.id,10), el]));
            const frag = document.createDocumentFragment();
            if(!pedidos.length){
                frag.appendChild(htmlToEl('<div class="pedidos-empty">No hay pedidos activos.</div>'));
            } else {
                pedidos.forEach(p=>{
                    let card = existentes.get(p.id);
                    if(card){ existentes.delete(p.id); }
                    else { card = buildCard(p,false); card.classList.add('anim-enter'); }
                    frag.appendChild(card);
                });
            }
            existentes.forEach(card=> { card.classList.add('anim-exit'); card.addEventListener('animationend', ()=> card.remove(), { once:true }); });
            activosCont.innerHTML='';
            activosCont.appendChild(frag);
        }
        if(histCont){
            const existentesH = new Map(Array.from(histCont.children).filter(el=>el.classList.contains('pedido-card')).map(el=>[parseInt(el.dataset.id,10), el]));
            const fragH = document.createDocumentFragment();
            if(!historial.length){
                fragH.appendChild(htmlToEl('<div class="pedidos-empty">Sin registros en historial.</div>'));
            } else {
                historial.forEach(p=>{
                    let card = existentesH.get(p.id);
                    if(card){ existentesH.delete(p.id); }
                    else { card = buildCard(p,true); card.classList.add('anim-enter'); }
                    fragH.appendChild(card);
                });
            }
            existentesH.forEach(card=> { card.classList.add('anim-exit'); card.addEventListener('animationend', ()=> card.remove(), { once:true }); });
            histCont.innerHTML='';
            histCont.appendChild(fragH);
        }
    }

    function calcularProximoEstado(actual){
        if(actual==='pendiente') return 'en_proceso';
        if(actual==='en_proceso') return 'completado';
        return null; // completado no avanza
    }

    function abrirModalCrear(){
        const modal = document.getElementById('modal-crear-pedido');
        if(!modal) return; modal.classList.remove('closing'); modal.setAttribute('aria-hidden','false');
        const hoy = new Date();
        document.getElementById('pedido-fecha').value = hoy.toISOString().slice(0,10);
        document.getElementById('pedido-hora').value = hoy.toTimeString().slice(0,5);
    // estado fijo pendiente; no campo editable
    }
    function cerrarModalCrear(){
        const modal = document.getElementById('modal-crear-pedido');
        if(!modal) return; modal.classList.add('closing'); setTimeout(()=> modal.setAttribute('aria-hidden','true'),260);
    }

    function abrirModalEstado(p){
        const modal = document.getElementById('modal-estado-pedido');
        if(!modal) return; modal.classList.remove('closing'); modal.setAttribute('aria-hidden','false');
        pedidoSeleccionado = p;
        proximoEstado = calcularProximoEstado(p.estado);
        const resumen = document.getElementById('estado-resumen');
        const warn = document.getElementById('estado-warning');
        const titulo = document.getElementById('estado-modal-titulo');
        titulo.textContent = `Modificar Estado #${p.id}`;
        resumen.innerHTML = `
            <div class="fila">
                <span class="tag">Estado Actual: ${p.estado.replace('_',' ')}</span>
                <span class="tag">Cliente: ${p.cliente_id}</span>
                <span class="tag">Empleado: ${p.empleado_id}</span>
                <span class="tag">Cantidad: ${p.cantidad}</span>
                <span class="tag">${p.tipo_consumo==='camarote'?'Habitación':'Lugar'}: ${p.tipo_consumo==='camarote'?(p.habitacion_nombre||'--'):(p.lugarentrega_nombre||'--')}</span>
            </div>
            ${p.nota?`<div class="fila"><span class="tag">Nota: ${p.nota}</span></div>`:''}
        `;
        if(p.estado==='pendiente'){
            warn.className='estado-warning';
            warn.textContent = 'Cambiar a EN PROCESO: ya no podrás modificar la factura ni eliminar el pedido. ¿Confirmas?';
        } else if(p.estado==='en_proceso'){
            warn.className='estado-warning en-proceso';
            warn.textContent = 'Cambiar a COMPLETADO: el pedido se moverá al historial y no será editable.';
        } else {
            warn.className='estado-warning completado';
            warn.textContent = 'Pedido completado. No hay más cambios disponibles.';
        }
        document.getElementById('confirmar-estado').disabled = (proximoEstado===null);
    }
    function cerrarModalEstado(){
        const modal = document.getElementById('modal-estado-pedido');
        if(!modal) return; modal.classList.add('closing'); setTimeout(()=> modal.setAttribute('aria-hidden','true'),250);
        pedidoSeleccionado = null; proximoEstado=null;
    }

    function aplicarCambioEstado(){
        if(!pedidoSeleccionado || !proximoEstado) return;
        const id = pedidoSeleccionado.id;
        actualizarEstadoPedido(id, proximoEstado)
            .then(ped=>{
                // Actualiza listas según nuevo estado
                pedidos = pedidos.filter(p=>p.id!==id);
                historial = historial.filter(p=>p.id!==id);
                if(ped.estado==='completado') historial.unshift(ped); else pedidos.unshift(ped);
                const card = document.querySelector('.pedido-card[data-id="'+id+'"]');
                if(card){ card.classList.add('state-changed'); setTimeout(()=> card.classList.remove('state-changed'),1300); }
                toast(`Pedido #${id} ahora está en ${ped.estado.replace('_',' ')}`,'success');
            })
            .catch(err=>{ console.error(err); toast(err.message||'Error al cambiar estado','error'); })
            .finally(()=>{ cerrarModalEstado(); renderListas(); });
    }

    function actualizarEstadoPedido(id, estado){
        return fetch(`/bar/pedido/${id}/estado/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ estado }) })
            .then(r=>r.json().then(j=>({ ok:r.ok, j })))
            .then(({ok,j})=>{ if(!ok||!j.success) throw new Error((j&&j.error)||'No se pudo actualizar estado'); return j.pedido; });
    }

    function cargarPedidosIniciales(){
        Promise.all([
            fetch('/bar/pedidos/?scope=activos').then(r=>r.json()).catch(()=>({success:false,items:[]})),
            fetch('/bar/pedidos/?scope=historial').then(r=>r.json()).catch(()=>({success:false,items:[]})),
        ]).then(([a,h])=>{
            if(a && a.success && Array.isArray(a.items)) pedidos = a.items; else pedidos = [];
            if(h && h.success && Array.isArray(h.items)) historial = h.items; else historial = [];
            renderListas();
        }).catch(()=>{ renderListas(); });
    }

    function init(){
        const btnCrear = document.getElementById('btn-abrir-crear-pedido');
        const cerrar = document.getElementById('close-modal-pedido');
        const cancelar = document.getElementById('cancelar-pedido');
        const form = document.getElementById('form-crear-pedido');
        const modalCrear = document.getElementById('modal-crear-pedido');
        if(btnCrear) btnCrear.addEventListener('click', abrirModalCrear);
        ;[cerrar,cancelar].forEach(el=> el && el.addEventListener('click', cerrarModalCrear));
        if(modalCrear){ modalCrear.addEventListener('click', e=>{ if(e.target===modalCrear) cerrarModalCrear(); }); }

        // Lógica demo camarote según cliente y lugar
    const lugarSelect = document.getElementById('pedido-lugar');
        const clienteIdInput = document.getElementById('pedido-cliente');
        const camaroteDisplay = document.getElementById('camarote-display');
        const camaroteCodigo = document.getElementById('camarote-codigo');
        function actualizarCamarote(){
            if(!lugarSelect || !clienteIdInput) return;
            if(lugarSelect.value==='Camarote'){
                const cid = parseInt(clienteIdInput.value||'0',10);
                if(cid>0){
                    // Simulación: código camarote = 'CAB-' + (100 + cliente_id)
                    camaroteCodigo.textContent = 'CAB-' + (100 + cid);
                } else {
                    camaroteCodigo.textContent = '-';
                }
                camaroteDisplay.style.display='block';
            } else {
                camaroteDisplay.style.display='none';
            }
        }
        if(lugarSelect){ lugarSelect.addEventListener('change', actualizarCamarote); }
    if(clienteIdInput){ clienteIdInput.addEventListener('input', ()=> { if(lugarSelect && lugarSelect.value==='Camarote') actualizarCamarote(); }); }

        const closeEstado = document.getElementById('close-modal-estado');
        const cancelEstado = document.getElementById('cancelar-estado');
        const confirmEstado = document.getElementById('confirmar-estado');
        const modalEstado = document.getElementById('modal-estado-pedido');
        if(closeEstado) closeEstado.addEventListener('click', cerrarModalEstado);
        if(cancelEstado) cancelEstado.addEventListener('click', cerrarModalEstado);
        if(confirmEstado) confirmEstado.addEventListener('click', aplicarCambioEstado);
        if(modalEstado){ modalEstado.addEventListener('click', e=> { if(e.target===modalEstado) cerrarModalEstado(); }); }

    if(form){
            form.addEventListener('submit', e=>{
                e.preventDefault();
                const data = new FormData(form);
                // Guardar nombre instalación seleccionada (si no se seteo aún)
                const selInst = document.getElementById('pedido-lugarentrega');
                if(selInst){
                    const hiddenNom = document.getElementById('pedido-lugarentrega-nombre');
                    if(hiddenNom) hiddenNom.value = selInst.options[selInst.selectedIndex]?.text || '';
                }
                const productosSel = parseListaProductos();
                const totalCantSel = productosSel.reduce((a,p)=> a + (parseInt(p.cantidad,10)||0), 0);
                const selectedInstId = parseInt((document.getElementById('pedido-lugarentrega')?.value)||'0',10) || null;
                const selectedInstCodigo = '';
                const tipo = data.get('tipo_consumo');
                const autoLugarEntregaId = (tipo==='bar') ? selectedInstId : null;
    const pedido = {
                    id: seq++,
                    fecha: data.get('fecha'),
                    hora: data.get('hora'),
                    estado: 'pendiente',
            tipo_consumo: tipo,
            lugarentrega_id: autoLugarEntregaId ?? (parseInt(data.get('lugarentrega_id')||'0',10) || null),
                    lugarentrega_nombre: (data.get('lugarentrega_nombre')||'').trim(),
                    habitacion_id: parseInt(data.get('habitacion_id')||'0',10) || null,
                    habitacion_nombre: (data.get('habitacion_nombre')||'').trim(),
                    cliente_id: parseInt(data.get('cliente_id'),10),
                    empleado_id: parseInt(data.get('empleado_id'),10),
            
            cantidad: totalCantSel,
                    productos: productosSel,
                    cliente_nombre: (data.get('cliente_nombre')||'').trim(),
                    nota: (data.get('nota')||'').trim()
                };
                // Enviar al backend
                const payload = {
                    cliente_id: pedido.cliente_id,
                    empleado_id: pedido.empleado_id,
                    
            tipo_consumo: pedido.tipo_consumo,
            lugarentrega_id: pedido.lugarentrega_id,
                    nota: pedido.nota,
                    productos: productosSel.map(p=> ({ producto_id: p.id, cantidad: p.cantidad }))
                };
                fetch('/bar/crear-pedido/', {
                    method:'POST',
                    headers:{ 'Content-Type':'application/json' },
                    body: JSON.stringify(payload)
                }).then(async r=>{
                    const text = await r.text();
                    let resp;
                    try { resp = JSON.parse(text); }
                    catch(e){
                        throw new Error(`HTTP ${r.status} ${r.statusText}: ${text.slice(0,400)}`);
                    }
                    if(!r.ok || !resp.success){
                        throw new Error(resp && resp.error ? resp.error : 'Error creando pedido');
                    }
                    return resp;
                }).then(resp=>{
                    // Actualizar con ID real de backend
                    const ped = resp.pedido;
                    ped.productos = ped.productos.map(d=> ({ id:d.producto_id, nombre:d.nombre, cantidad:d.cantidad, precio:d.precio }));
                    ped.cantidad = ped.productos.reduce((a,d)=> a + (parseInt(d.cantidad,10)||0), 0);
                    pedidos.unshift(ped);
                    renderListas();
                    toast('Pedido creado (#'+ped.id+')','success');
                }).catch(err=>{
                    console.error(err);
                    toast(err.message||'Error al crear el pedido','error');
                }).finally(()=>{
                    form.reset();
                    cantidadesEstado.clear();
                    const sel = document.getElementById('pedido-productos');
                    if(sel) Array.from(sel.options).forEach(o=>o.selected=false);
                    syncCajaCantidades();
                    cerrarModalCrear();
                });
            });
        }

    // Campo Bar eliminado, sólo se usa lugarentrega
        const instSelect = document.getElementById('pedido-lugarentrega');
        const tipoConsumo = document.getElementById('pedido-tipo-consumo');
        const habitacionSelect = document.getElementById('pedido-habitacion');
        const wrapInst = document.getElementById('wrapper-instalacion');
        const wrapHab = document.getElementById('wrapper-habitacion');
    if(instSelect){
            // Poblar instalaciones reales (bares/cafés)
            fetch('/bar/bares/').then(r=>r.json()).then(data=>{
                if(Array.isArray(data)){
                    data.forEach(i=>{
                        const opt=document.createElement('option');
                        opt.value=i.id; // id de Instalacion
                        opt.textContent=i.nombre + (i.crucero?` · ${i.crucero}`:'');
                        instSelect.appendChild(opt);
                    });
                }
            }).catch(()=>{});
            instSelect.addEventListener('change',()=>{
                const hiddenNom = document.getElementById('pedido-lugarentrega-nombre');
                if(hiddenNom){ hiddenNom.value = instSelect.options[instSelect.selectedIndex]?.text || ''; }
            });
        }
        if(habitacionSelect){
            // Poblar desde backend
            fetch('/bar/habitaciones/')
                .then(r=>r.json())
                .then(data=>{
                    if(Array.isArray(data)){
                        data.forEach(h=>{
                            const opt=document.createElement('option');
                            opt.value=h.id;
                            opt.textContent=(h.label || (`HAB: ${h.codigo} ${(h.lado==='babor'?'BAB':'EST')}`));
                            opt.dataset.codigo=h.codigo;
                            opt.dataset.lado=h.lado;
                            habitacionSelect.appendChild(opt);
                        });
                    }
                }).catch(()=>{});
            habitacionSelect.addEventListener('change',()=>{
                const hiddenHab = document.getElementById('pedido-habitacion-nombre');
                if(hiddenHab){ hiddenHab.value = habitacionSelect.options[habitacionSelect.selectedIndex]?.text || ''; }
            });
        }
        if(tipoConsumo && wrapInst && wrapHab){
            const applyTipo = ()=>{
                if(tipoConsumo.value==='bar'){
                    // Mostrar instalación (bar) requerido
                    wrapInst.style.display='';
                    instSelect?.setAttribute('required','required');
                    // Camarote oculto
                    wrapHab.style.display='none';
                    habitacionSelect?.removeAttribute('required');
                } else {
                    // Modo camarote: requerir habitación
                    wrapHab.style.display='';
                    habitacionSelect?.setAttribute('required','required');
                    wrapInst.style.display='none';
                    instSelect?.removeAttribute('required');
                }
            };
            tipoConsumo.addEventListener('change', applyTipo);
            applyTipo();
        }

        // Delegación acciones activos
        const activosCont = document.getElementById('pedidos-lista-activos');
        if(activosCont){
            activosCont.addEventListener('click', e=>{
                const btn = e.target.closest('[data-accion]');
                if(!btn) return;
                const id = parseInt(btn.dataset.id,10);
                const p = pedidos.find(x=>x.id===id);
                if(!p) return;
                if(btn.dataset.accion==='eliminar'){
                    if(p.estado!=='pendiente') return; // seguridad
                    fetch(`/bar/pedido/${id}/eliminar/`, { method:'POST', headers:{'X-Requested-With':'XMLHttpRequest'} })
                        .then(r=>r.json().then(j=>({ ok:r.ok, j })))
                        .then(({ok,j})=>{
                            if(!ok || !j.success) throw new Error((j&&j.error)||'No se pudo eliminar');
                            pedidos = pedidos.filter(x=>x.id!==id);
                            renderListas();
                            toast(`Pedido #${id} eliminado`, 'success');
                        })
                        .catch(err=>{ console.error(err); toast(err.message||'Error al eliminar', 'error'); });
                } else if(btn.dataset.accion==='estado'){
                    abrirModalEstado(p);
                }
            });
        }
    cargarPedidosIniciales();
    }

    document.addEventListener('DOMContentLoaded', init);
    document.addEventListener('DOMContentLoaded', cargarCatalogoProductos);
    document.addEventListener('DOMContentLoaded', ()=>{
        const sel = document.getElementById('pedido-productos');
        if(sel){
            sel.addEventListener('change', onChangeSelectProductos);
            // Permitir seleccionar/deseleccionar múltiples SIN usar Ctrl/Cmd
            sel.addEventListener('mousedown', (e)=>{
                const opt = e.target;
                if(opt && opt.tagName === 'OPTION'){
                    e.preventDefault();
                    opt.selected = !opt.selected;
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
        syncCajaCantidades();
        calcularDisponibilidadResumen();
    });

        /* ----------- Detalle Factura / Receta ----------- */
        function abrirDetalleFactura(p){
        // NO cambiamos estado aquí; se hará al cerrar si estaba pendiente
                const modal = crearModalDetalle(p);
                document.body.appendChild(modal.backdrop);
        }

        function crearModalDetalle(p){
                const backdrop = document.createElement('div');
                backdrop.className='modal-pedido';
                backdrop.style.display='flex';
            backdrop.innerHTML=`<div class="modal-pedido-dialog recibo" style="max-width:440px; background:linear-gradient(180deg,#ffffff,#f8fafc 40%,#ffffff); border:1px solid #e2e8f0;">
                        <button class="modal-close" aria-label="Cerrar">×</button>
                        <h2 class="modal-title">Pedido #${p.id} (Estado: ${p.estado.replace('_',' ')})</h2>
                        <div class="estado-resumen" style="font-size:.75rem">
                            <div class="fila">
                                <span class="tag">Cliente: ${p.cliente_id}</span>
                                <span class="tag">Empleado: ${p.empleado_id}</span>
                                
                                <span class="tag">${p.tipo_consumo==='camarote'?'Habitación':'Lugar'}: ${p.tipo_consumo==='camarote'?(p.habitacion_nombre||'--'):(p.lugarentrega_nombre||'--')}</span>
                                <span class="tag">Cant: ${p.cantidad}</span>
                            </div>
                            ${(p.productos && p.productos.length)?`<div class="fila"><span class="tag">Productos: ${p.productos.map(pr=> (typeof pr==='string'? pr : pr.nombre)).join(', ')}</span></div>`:''}
                            ${p.cliente_nombre?`<div class="fila"><span class="tag">Nombre Cliente: ${p.cliente_nombre}</span></div>`:''}
                            ${p.nota?`<div class="fila"><span class="tag">Nota: ${p.nota}</span></div>`:''}
                        </div>
                                    <div class="receta-box" style="margin-top:8px; background:#f1f5f9; border:1px dashed #cbd5e1; padding:14px 16px; border-radius:16px; font-size:.68rem;">
                            <strong>Receta / Preparación</strong>
                            <p style="margin:6px 0 0; line-height:1.4;">(Hover en el botón para ver ejemplo)</p>
                            <button class="pedido-btn" id="btn-hover-receta" style="margin-top:10px; position:relative;">Ver Receta
                                <span class="receta-tooltip" style="position:absolute; left:0; top:110%; background:#0f172a; color:#fff; padding:10px 12px; border-radius:10px; font-size:.6rem; width:260px; opacity:0; pointer-events:none; transform:translateY(6px); transition:.25s;">${(p.productos && p.productos.length)?p.productos.map(prod=>`<strong>${prod}</strong>:<br>- Paso 1<br>- Paso 2<br><br>`).join(''):'Sin productos cargados aún.'}</span>
                            </button>
                        </div>
                                    <p class="nota-proceso" style="margin:20px 0 4px; font-size:.55rem; letter-spacing:.05em; color:#64748b; text-align:center; text-transform:uppercase;">al cerrar esta pestaña, el pedido comenzará su proceso</p>
                                    <div class="estado-acciones" style="justify-content:center; margin-top:10px;">
                                        ${(p.estado!=='completado')?'<button type="button" class="btn-primario btn-completar" data-completar style="background:#16a34a;">Completar Pedido</button>':''}
                                    </div>
                </div>`;
                const dialog = backdrop.querySelector('.modal-pedido-dialog');
                const close = backdrop.querySelector('[data-close], .modal-close');
                backdrop.addEventListener('click', e=>{ if(e.target===backdrop) cerrar(); });
                backdrop.querySelector('.modal-close').addEventListener('click', cerrar);
                            if(close) close.addEventListener('click', cerrar);
            const btnComp = backdrop.querySelector('[data-completar]');
                if(btnComp){
                        btnComp.addEventListener('click',()=>{
                            const id = p.id;
                            const chain = (p.estado==='pendiente')
                                ? actualizarEstadoPedido(id, 'en_proceso').then(()=> actualizarEstadoPedido(id, 'completado'))
                                : actualizarEstadoPedido(id, 'completado');
                            chain.then(pedFinal=>{
                                pedidos = pedidos.filter(x=>x.id!==id);
                                historial = historial.filter(x=>x.id!==id);
                                if(pedFinal.estado==='completado') historial.unshift(pedFinal); else pedidos.unshift(pedFinal);
                                toast(`Pedido #${id} completado`,'success');
                                cerrar();
                                renderListas();
                            }).catch(err=>{ console.error(err); toast(err.message||'No se pudo completar','error'); });
                        });
                }
                const hoverBtn = backdrop.querySelector('#btn-hover-receta');
                if(hoverBtn){
                        const tooltip = hoverBtn.querySelector('.receta-tooltip');
                        hoverBtn.addEventListener('mouseenter',()=>{ tooltip.style.opacity='1'; tooltip.style.transform='translateY(0)'; });
                        hoverBtn.addEventListener('mouseleave',()=>{ tooltip.style.opacity='0'; tooltip.style.transform='translateY(6px)'; });
                }
                const estadoInicial = p.estado;
                function cerrar(){
                    backdrop.classList.add('closing');
                    if(estadoInicial==='pendiente' && p.estado==='pendiente'){
                        actualizarEstadoPedido(p.id, 'en_proceso')
                            .then(ped=>{
                                pedidos = pedidos.filter(x=>x.id!==p.id);
                                historial = historial.filter(x=>x.id!==p.id);
                                pedidos.unshift(ped);
                                toast(`Has empezado el pedido #${p.id}`,'success');
                                renderListas();
                            })
                            .catch(err=>{ console.warn('No se pudo poner en proceso automáticamente', err); });
                    }
                    setTimeout(()=> backdrop.remove(), 260);
                }
                return { backdrop, dialog };
        }

        /* ----------- Toast ----------- */
        function toast(msg, tipo='info'){
                let host = document.getElementById('toast-host');
                if(!host){ host=document.createElement('div'); host.id='toast-host'; host.style.position='fixed'; host.style.top='16px'; host.style.right='16px'; host.style.display='flex'; host.style.flexDirection='column'; host.style.gap='10px'; host.style.zIndex='5000'; document.body.appendChild(host); }
                const el = document.createElement('div');
                el.textContent=msg;
            if(tipo==='success'){
                el.style.background='linear-gradient(135deg,#16a34a,#059669)';
                el.style.color='#f0fdf4';
            } else {
                el.style.background='linear-gradient(135deg,#0ea5e9,#6366f1)';
                el.style.color='#fff';
            }
                el.style.padding='10px 16px';
                el.style.borderRadius='12px';
                el.style.fontSize='.7rem';
                el.style.boxShadow='0 6px 20px -6px rgba(14,165,233,.55)';
                el.style.opacity='0';
                el.style.transform='translateY(-6px)';
                el.style.transition='.4s';
                host.appendChild(el);
                requestAnimationFrame(()=> { el.style.opacity='1'; el.style.transform='translateY(0)'; });
                setTimeout(()=> { el.style.opacity='0'; el.style.transform='translateY(-6px)'; setTimeout(()=> el.remove(), 400); }, 3500);
        }
})();