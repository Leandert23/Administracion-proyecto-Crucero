// Módulo Pedidos (fase UI local antes de backend)
(function(){
    let pedidos = []; // activos (pendiente, en_proceso)
    let historial = []; // completados o cancelados
    let seq = 1;
    let pedidoSeleccionado = null;
    let proximoEstado = null;
    let editPedidoId = null; // id del pedido en edición (si aplica)

    const ESTADOS = ['pendiente','en_proceso','completado'];

    // ----- Multi productos (estado in-memory) -----
    let catalogoProductos = [];
    const cantidadesEstado = new Map(); // productoId -> { id, nombre, tipo, precio, cantidad }
    let cantidadesBackup = null; // backup para restaurar al cambiar tipo/subtipo
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

    // ========== MODIFICACIONES PARA DISEÑO Y LÓGICA DE PEDIDOS ==========

    // Eliminar referencias a cliente_id en toda la lógica
    // Mostrar número de habitación en el resumen si aplica
    // Rediseñar la caja de pedido y botones con clases animadas y coloridas
    // Solo permitir edición en estado 'pendiente'
    // Ventana de detalle tipo factura con receta y botón llamativo para completar pedido

    function buildCard(p, esHistorial){
        // Etiqueta de plan y precio si es premium
        let planLabel = '';
        let planType = 'inclusive';
        if(p.productos && p.productos.length > 0){
            const premium = p.productos.some(d => d.plan === 'pago' || d.plan === 'premium');
            if(premium){
                planLabel = `<span class="plan-label premium">Premium</span>`;
                planType = 'premium';
            } else {
                planLabel = `<span class="plan-label inclusive">All Inclusive</span>`;
            }
        }
        // Estado visual
        let estadoClass = 'pedido-estado ' + p.estado;
        let estadoTxt = p.estado.replace('_',' ');
        // Productos y cantidades - estilo factura
        const productosTxt = (p.productos||[]).map(d=> `${escapeHtml(d.nombre)} x${d.cantidad}`).join(', ');
        // Lugar/habitación
        let lugarTxt = p.tipo_consumo==='camarote' ? `Habitación: ${escapeHtml(p.habitacion_nombre||'-')}` : `Lugar: ${escapeHtml(p.lugarentrega_nombre||'-')}`;
    // Empleado (mostrar nombre y categoría si están disponibles)
    let empNom = p.empleado_nombre || null;
    let empCat = p.empleado_categoria || null;
    let empleadoTxt = 'Empleado: ' + (empNom ? `${escapeHtml(empNom)}${empCat?` — ${escapeHtml(empCat)}`:''}` : (p.empleado_id??'-'));
        // Botones
        let btns = '';
        if(esHistorial){
            btns = `<div class="pedido-actions">
                <button class="btn-secundario btn-animado" data-accion="detalle" data-id="${p.id}">Ver Detalle</button>
            </div>`;
        } else {
            btns = `<div class="pedido-actions">
                <button class="btn-secundario btn-animado" data-accion="detalle" data-id="${p.id}">Ver Detalle</button>
                <button class="btn-peligro btn-animado" data-accion="eliminar" data-id="${p.id}" ${p.estado!=='pendiente'?'disabled':''}>Eliminar</button>
            </div>`;
        }
        // Card visual estilo factura
        const card = htmlToEl(`
            <div class="pedido-card ${p.estado}" data-id="${p.id}" style="background:#fff; border:1px solid #e5e7eb; font-family: 'Fira Mono', 'Consolas', monospace; padding:18px 24px 22px;">
                <div class="pedido-head">
                    <div class="pedido-id">#${p.id}</div>
                    <div class="pedido-factura">Factura: <span style="color:#059669;font-weight:600;">${p.numero_factura||'-'}</span></div>
                    <div style="display:flex;align-items:center;gap:8px;">
                      <div class="${estadoClass}">${estadoTxt}</div>
                      ${planLabel}
                    </div>
                </div>
                <div class="pedido-body" style="display:flex;flex-direction:column;gap:8px; margin-top:10px;">
                    <div class="pedido-linea productos-lista" style="color:#64748b;">Productos: ${productosTxt||'-'}</div>
                    <div class="pedido-linea lugar-lista" style="color:#64748b;">${lugarTxt}</div>
                    <div class="pedido-linea empleado-lista" style="color:#64748b;">${empleadoTxt}</div>
                </div>
                ${btns}
            </div>
        `);
        return card;
    }

    // Ventana de detalle tipo factura con receta y botón para completar pedido
    function crearModalDetalle(p){
        const backdrop = document.createElement('div');
        backdrop.className='modal-pedido';
        backdrop.style.display='flex';
        // Receta por producto
        let recetaHtml = '';
        if(p.productos && p.productos.length){
            recetaHtml = p.productos.map(prod => `<div><strong>${prod.nombre}</strong><br>${prod.receta||'-'}</div>`).join('<hr>');
        } else {
            recetaHtml = 'Sin productos cargados aún.';
        }
        // Botón completar
    const btnCompletar = (p.estado!=='completado') ? '<button type="button" class="btn-primario btn-animado btn-completar" data-completar style="background:#16a34a;">Completar Pedido</button>' : '';
    const btnEditar = (p.estado==='pendiente') ? '<button type="button" class="btn-secundario btn-animado" data-editar style="margin-left:8px;">Editar</button>' : '';
        backdrop.innerHTML = `
            <div class="modal-pedido-dialog recibo" style="max-width:440px; background:linear-gradient(180deg,#ffffff,#f8fafc 40%,#ffffff); border:1px solid #e2e8f0;">
                <button class="modal-close" aria-label="Cerrar">×</button>
                <h2 class="modal-title">Pedido #${p.id} (Estado: ${p.estado.replace('_',' ')})</h2>
                <div style="font-family:'Fira Mono','Consolas',monospace; color:#475569; margin:10px 0 14px; font-size:.95em;">
                  <div style="color:#059669; font-weight:600;">Número de Factura: ${p.numero_factura||'-'}</div>
                </div>
                <div class="estado-resumen" style="font-size:.75rem">
                    <div class="fila">
                        <span class="tag">${p.tipo_consumo==='camarote'?'Habitación':'Lugar'}: ${p.tipo_consumo==='camarote'?(p.habitacion_nombre||'--'):(p.lugarentrega_nombre||'--')}</span>
                        <span class="tag">Empleado: ${p.empleado_nombre ? escapeHtml(p.empleado_nombre) + (p.empleado_categoria?` — ${escapeHtml(p.empleado_categoria)}`:'') : (p.empleado_id??'-')}</span>
                    </div>
                    <div class="fila"><span class="tag">Productos: ${(p.productos||[]).map(pr=>pr.nombre).join(', ')}</span></div>
                    ${p.nota?`<div class="fila"><span class="tag">Nota: ${escapeHtml(p.nota)}</span></div>`:''}
                </div>
                <div class="receta-box" style="margin-top:8px; background:#f1f5f9; border:1px dashed #cbd5e1; padding:14px 16px; border-radius:16px; font-size:.68rem;">
                    <strong>Receta / Preparación</strong>
                    ${recetaHtml}
                </div>
                <div class="estado-acciones" style="justify-content:center; margin-top:10px;">
                    ${btnCompletar}
                    ${btnEditar}
                </div>
            </div>
        `;
        // Cierre y completar
        backdrop.querySelector('.modal-close').addEventListener('click', ()=>{
            backdrop.remove();
        });
        const btnComp = backdrop.querySelector('[data-completar]');
        if(btnComp){
            btnComp.addEventListener('click', ()=>{
                // Completar pedido y actualizar stock
                fetch(`/bar/pedido/${p.id}/estado/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ estado: 'completado' }) })
                    .then(r=>r.json())
                    .then(j=>{
                        toast('Pedido completado y stock actualizado','success');
                        backdrop.remove();
                        cargarPedidosIniciales();
                    });
            });
        }
        const btnEdit = backdrop.querySelector('[data-editar]');
        if(btnEdit){
            btnEdit.addEventListener('click', ()=>{
                // Cerrar el modal de detalle y entrar en modo edición usando el submit unificado
                try{
                    backdrop.remove();
                    editPedidoId = p.id;
                    // Prellenar selección de productos y cantidades
                    cantidadesEstado.clear();
                    (p.productos||[]).forEach(d=>{
                        const pid = d.producto_id || d.id;
                        if(!pid) return;
                        cantidadesEstado.set(pid, { id:pid, nombre:d.nombre, tipo:(d.plan==='pago'?'pago':'gratis'), precio: d.precio||0, cantidad: d.cantidad||1 });
                    });
                    // Tipo de consumo
                    const tipoSel = document.getElementById('pedido-tipo-consumo');
                    if(tipoSel){ tipoSel.value = p.tipo_consumo || 'bar'; tipoSel.dispatchEvent(new Event('change')); }
                    // Inst / Hab
                    const instSel = document.getElementById('pedido-lugarentrega');
                    if(instSel && p.lugarentrega_id){ instSel.value = String(p.lugarentrega_id); instSel.dispatchEvent(new Event('change')); }
                    const habSel = document.getElementById('pedido-habitacion');
                    if(habSel && p.habitacion_id){ habSel.value = String(p.habitacion_id); habSel.dispatchEvent(new Event('change')); }
                    // Empleado y nota
                    const empInp = document.getElementById('pedido-empleado');
                    if(empInp){ empInp.value = p.empleado_id || ''; empInp.dispatchEvent(new Event('input')); }
                    const notaInp = document.getElementById('pedido-nota');
                    if(notaInp){ notaInp.value = p.nota || ''; }
                    // Abrir form y sincronizar
                    abrirModalCrear();
                    marcarSelectProductos();
                    syncCajaCantidades();
                }catch(err){ console.error(err); toast('No se pudo cargar el pedido para edición','error'); }
            });
        }
        document.body.appendChild(backdrop);
    }

    // Delegación de acciones en la caja de pedidos
    function renderListas(){
        const activosCont = document.getElementById('pedidos-lista-activos');
        const histCont = document.getElementById('pedidos-lista-historial');
        if(activosCont){
            activosCont.innerHTML = '';
            if(!pedidos.length){
                activosCont.innerHTML = '<div class="pedidos-empty">No hay pedidos activos.</div>';
            } else {
                pedidos.forEach(p=>{
                    const card = buildCard(p, false);
                    // Abrir detalle solo mediante el botón "Ver Detalle" (delegación al final del archivo)
                    activosCont.appendChild(card);
                });
            }
        }
        if(histCont){
            histCont.innerHTML = '';
            if(!historial.length){
                histCont.innerHTML = '<div class="pedidos-empty">Sin registros en historial.</div>';
            } else {
                historial.forEach(p=>{
                    const card = buildCard(p, true);
                    histCont.appendChild(card);
                });
            }
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
        // Salir de modo edición si estaba activo
        editPedidoId = null;
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
                <span class="tag">Empleado: ${p.empleado_nombre ? escapeHtml(p.empleado_nombre) + (p.empleado_categoria?` — ${escapeHtml(p.empleado_categoria)}`:'') : (p.empleado_id??'-')}</span>
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

        // Mostrar nombre y categoria del empleado al escribir el ID
        const empleadoInput = document.getElementById('pedido-empleado');
        const empleadoInfoEl = document.getElementById('empleado-info');
        let empleadoFetchTimer = null;
        if(empleadoInput && empleadoInfoEl){
            const renderEmpleado = (txt, color='#334155')=>{ empleadoInfoEl.textContent = txt; empleadoInfoEl.style.color = color; };
            const buscar = async (id)=>{
                if(!id||id<=0){ renderEmpleado(''); return; }
                try{
                    renderEmpleado('Buscando…', '#64748b');
                    const r = await fetch(`/bar/empleado/${id}/`);
                    const j = await r.json();
                    if(!r.ok || !j.success) throw new Error((j&&j.error)||'No encontrado');
                    const e = j.empleado;
                    renderEmpleado(`${e.nombre_completo} — ${e.categoria}${e.puesto?` (${e.puesto})`:''}`);
                }catch(err){
                    renderEmpleado('Empleado no encontrado', '#b91c1c');
                }
            };
            const handler = ()=>{
                const id = parseInt(empleadoInput.value||'0', 10) || 0;
                if(empleadoFetchTimer) clearTimeout(empleadoFetchTimer);
                empleadoFetchTimer = setTimeout(()=> buscar(id), 300);
            };
            empleadoInput.addEventListener('input', handler);
            empleadoInput.addEventListener('blur', handler);
        }

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

        // Delegación para abrir detalle (aseguramos DOM listo aquí)
        const contAct = document.getElementById('pedidos-lista-activos');
        const contHist = document.getElementById('pedidos-lista-historial');
        if(contAct){
            contAct.addEventListener('click', e=>{
                const btn = e.target.closest('[data-accion="detalle"]');
                if(!btn) return;
                const id = parseInt(btn.dataset.id,10);
                const p = pedidos.find(x=>x.id===id);
                if(!p) return;
                abrirDetalleFactura(p);
            });
        }
        if(contHist){
            contHist.addEventListener('click', e=>{
                const btn = e.target.closest('[data-accion="detalle"]');
                if(!btn) return;
                const id = parseInt(btn.dataset.id,10);
                const p = historial.find(x=>x.id===id);
                if(!p) return;
                abrirDetalleFactura(p);
            });
        }

        if(form){
            form.addEventListener('submit', async e=>{
                e.preventDefault();
                const data = new FormData(form);
                // Guardar nombre instalación seleccionada (si no se seteo aún)
                const selInst = document.getElementById('pedido-lugarentrega');
                if(selInst){
                    const hiddenNom = document.getElementById('pedido-lugarentrega-nombre');
                    if(hiddenNom) hiddenNom.value = selInst.options[selInst.selectedIndex]?.text || '';
                }
                const productosSel = parseListaProductos();
                const tipo = data.get('tipo_consumo');
                const selectedInstId = parseInt((document.getElementById('pedido-lugarentrega')?.value)||'0',10) || null;
                const selectedHabId = parseInt((document.getElementById('pedido-habitacion')?.value)||'0',10) || null;
                const autoLugarEntregaId = (tipo==='bar') ? selectedInstId : null;

                const payloadBase = {
                    empleado_id: parseInt(data.get('empleado_id')||'0',10) || null,
                    tipo_consumo: tipo,
                    lugarentrega_id: autoLugarEntregaId ?? (parseInt(data.get('lugarentrega_id')||'0',10) || null),
                    habitacion_id: (tipo==='camarote') ? (selectedHabId || (parseInt(data.get('habitacion_id')||'0',10)||null)) : null,
                    nota: (data.get('nota')||'').trim(),
                    productos: productosSel.map(p=> ({ producto_id: p.id, cantidad: p.cantidad }))
                };

                try{
                    if(editPedidoId){
                        // Actualizar existente
                        const r = await fetch(`/bar/pedido/${editPedidoId}/actualizar/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payloadBase) });
                        const j = await r.json();
                        if(!r.ok || !j.success) throw new Error(j && j.error || 'No se pudo actualizar');
                        const ped = j.pedido;
                        ped.productos = (ped.productos||[]).map(d=> ({ detalle_id: d.id, producto_id:d.producto_id, id:d.producto_id, nombre:d.nombre, cantidad:d.cantidad, precio:d.precio, receta:d.receta, subtotal:d.subtotal }));
                        ped.cantidad = ped.productos.reduce((a,d)=> a + (parseInt(d.cantidad,10)||0), 0);
                        // Actualizar listas: reemplazar si existe en activos o historial
                        pedidos = pedidos.map(x=> x.id===ped.id ? ped : x);
                        historial = historial.map(x=> x.id===ped.id ? ped : x);
                        renderListas();
                        toast('Pedido actualizado (#'+ped.id+')','success');
                    } else {
                        // Crear nuevo
                        const r = await fetch('/bar/crear-pedido/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payloadBase) });
                        const text = await r.text();
                        let resp;
                        try { resp = JSON.parse(text); } catch(e){ throw new Error(`HTTP ${r.status} ${r.statusText}: ${text.slice(0,400)}`); }
                        if(!r.ok || !resp.success) throw new Error(resp && resp.error ? resp.error : 'Error creando pedido');
                        const ped = resp.pedido;
                        ped.productos = ped.productos.map(d=> ({ detalle_id: d.id, producto_id:d.producto_id, id:d.producto_id, nombre:d.nombre, cantidad:d.cantidad, precio:d.precio, receta:d.receta, subtotal:d.subtotal }));
                        ped.cantidad = ped.productos.reduce((a,d)=> a + (parseInt(d.cantidad,10)||0), 0);
                        pedidos.unshift(ped);
                        renderListas();
                        toast('Pedido creado (#'+ped.id+')','success');
                    }
                }catch(err){
                    console.error(err);
                    toast(err.message || (editPedidoId?'Error al actualizar':'Error al crear el pedido'), 'error');
                } finally {
                    form.reset();
                    cantidadesEstado.clear();
                    const sel = document.getElementById('pedido-productos');
                    if(sel) Array.from(sel.options).forEach(o=>o.selected=false);
                    syncCajaCantidades();
                    cerrarModalCrear();
                }
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
                // Solo cambiar la visibilidad de los campos, sin modificar cantidadesEstado
                if(tipoConsumo.value==='bar'){
                    wrapInst.style.display='';
                    instSelect?.setAttribute('required','required');
                    wrapHab.style.display='none';
                    habitacionSelect?.removeAttribute('required');
                } else {
                    wrapHab.style.display='';
                    habitacionSelect?.setAttribute('required','required');
                    wrapInst.style.display='none';
                    instSelect?.removeAttribute('required');
                }
                // No modificar cantidadesEstado ni restaurar backup
                marcarSelectProductos();
                syncCajaCantidades();
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

    // Exponer refresco global para que otras secciones (ej. Promociones) actualicen la lista de pedidos
    try {
        window.BaresPedidos = window.BaresPedidos || {};
        window.BaresPedidos.refresh = cargarPedidosIniciales;
    } catch(_e) {}

                /* ----------- Detalle Factura / Receta ----------- */
                function abrirDetalleFactura(p){
                    // No cambiar estado automáticamente; mostrar acciones explícitas
                    const modal = crearModalFactura(p);
                    document.body.appendChild(modal.backdrop);
                }

                function crearModalFactura(p){
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-pedido';
                    backdrop.style.display = 'flex';

                    // Tabla simple: Producto | Cantidad | Receta
                    const puedeBorrar = p.estado === 'pendiente';
                    const filas = (p.productos||[]).map((d)=>{
                        const nombre = (typeof d === 'string') ? d : d.nombre;
                        const receta = (typeof d === 'object' && d.receta) ? d.receta : '';
                        const cant = (typeof d === 'object' && (d.cantidad!=null)) ? d.cantidad : '';
                        const detalleId = d.detalle_id || d.id; // preferir detalle_id
                        return `<tr data-detalle-row="${detalleId||''}">
                            <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb;">${nombre}</td>
                            <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb; text-align:center; color:#0f172a;">${cant}</td>
                            <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb; color:#64748b;">${receta||'-'}</td>
                            <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb; text-align:center;">${(puedeBorrar && detalleId)?`<button class="btn-peligro" data-del-detalle data-pedido-id="${p.id}" data-detalle-id="${detalleId}">Eliminar</button>`:''}</td>
                        </tr>`;
                    }).join('');

                    const puedePonerEnProceso = p.estado === 'pendiente';
                    const puedeCompletar = p.estado === 'en_proceso' || p.estado === 'pendiente';
                    const puedeEditar = p.estado === 'pendiente';

                    backdrop.innerHTML = `
                        <div class="modal-pedido-dialog recibo" style="max-width:560px; background:#fff; border:1px solid #e7eaf3;">
                            <button class="modal-close" aria-label="Cerrar">×</button>
                            <h2 class="modal-title">Factura Pedido #${p.id}</h2>
                            <div style="font-family:'Fira Mono','Consolas',monospace; color:#475569; display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0 14px;">
                                <div>Estado: ${p.estado.replace('_',' ')}</div>
                                <div>Tipo: ${p.tipo_consumo==='camarote'?'Camarote':'Bar'}</div>
                                <div>${p.tipo_consumo==='camarote'?'Habitación':'Lugar'}: ${p.tipo_consumo==='camarote'?(p.habitacion_nombre||'--'):(p.lugarentrega_nombre||'--')}</div>
                                <div>Empleado: ${p.empleado_nombre ? escapeHtml(p.empleado_nombre) + (p.empleado_categoria?` — ${escapeHtml(p.empleado_categoria)}`:'') : (p.empleado_id??'-')}</div>
                                <div>Fecha: ${p.fecha || '--'}</div>
                                <div>Hora: ${p.hora || '--'}</div>
                                <div style="grid-column:1 / -1;">Total: $${(p.total!=null?Number(p.total).toFixed(2):'0.00')}</div>
                                ${p.nota?`<div style="grid-column:1 / -1;">Nota: ${escapeHtml(p.nota)}</div>`:''}
                            </div>
                            <div style="border:1px solid #e7eaf3; border-radius:10px; overflow:hidden;">
                                <table style="width:100%; border-collapse:collapse;">
                    <thead style="background:#f8fafc; text-align:left;">
                                        <tr>
                                            <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3;">Producto</th>
                                            <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3; text-align:center; width:96px;">Cantidad</th>
                        <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3;">Receta</th>
                        <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3; text-align:center; width:120px;">Acciones</th>
                                        </tr>
                                    </thead>
                    <tbody>${filas||'<tr><td colspan="4" style="padding:10px; color:#64748b; text-align:center;">Sin productos</td></tr>'}</tbody>
                                </table>
                            </div>
                            <div class="estado-acciones modal-acciones" style="display:flex; gap:8px; justify-content:center; margin-top:14px;">
                                ${puedePonerEnProceso?'<button type="button" class="modal-btn btn-proceso" data-en-proceso>Poner en proceso</button>':''}
                                ${puedeCompletar?'<button type="button" class="modal-btn btn-completar" data-completar>Completar</button>':''}
                                ${puedeEditar?'<button type="button" class="btn-secundario" data-editar>Editar</button>':''}
                            </div>
                        </div>`;

                    const cerrar = ()=> backdrop.remove();
                    backdrop.querySelector('.modal-close')?.addEventListener('click', cerrar);
                    backdrop.addEventListener('click', (e)=>{ if(e.target===backdrop) cerrar(); });

                    // Eliminar detalle (producto) desde la factura
                    backdrop.addEventListener('click', (e)=>{
                        const btnDel = e.target.closest('[data-del-detalle]');
                        if(!btnDel) return;
                        const detalleId = parseInt(btnDel.getAttribute('data-detalle-id'),10);
                        if(!detalleId || p.estado!=='pendiente') return;
                        fetch(`/bar/pedido/${p.id}/detalle/${detalleId}/eliminar/`, { method:'POST', headers:{'X-Requested-With':'XMLHttpRequest'} })
                          .then(r=>r.json().then(j=>({ok:r.ok, j})))
                          .then(({ok,j})=>{
                              if(!ok || !j.success){ throw new Error((j&&j.error)||'No se pudo eliminar el producto'); }
                              if(j.pedido_deleted){
                                  // quitar tarjeta y cerrar
                                  pedidos = pedidos.filter(x=> x.id!==p.id);
                                  historial = historial.filter(x=> x.id!==p.id);
                                  toast('Pedido eliminado (sin productos).','success');
                                  cerrar();
                              } else if(j.pedido){
                                  // Actualizar pedido en memoria
                                  const pedAct = j.pedido;
                                  // Mantener forma de productos con detalle_id
                                  pedAct.productos = (pedAct.productos||[]).map(d=> ({ detalle_id: d.id, producto_id:d.producto_id, id:d.producto_id, nombre:d.nombre, cantidad:d.cantidad, precio:d.precio, receta:d.receta, subtotal:d.subtotal }));
                                  pedidos = pedidos.map(x=> x.id===pedAct.id ? pedAct : x);
                                  historial = historial.map(x=> x.id===pedAct.id ? pedAct : x);
                                  toast('Producto eliminado del pedido.','success');
                                  cerrar();
                              }
                              renderListas();
                              try { window.BaresOrdenes && window.BaresOrdenes.refresh && window.BaresOrdenes.refresh(); } catch(e){}
                          })
                          .catch(err=>{ console.error(err); toast(err.message||'Error al eliminar producto','error'); });
                    });

                    // Acción: Poner en proceso
                    const btnProceso = backdrop.querySelector('[data-en-proceso]');
                    if(btnProceso){
                        btnProceso.addEventListener('click', ()=>{
                            fetch(`/bar/pedido/${p.id}/estado/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ estado: 'en_proceso' }) })
                                .then(r=>r.json()).then(({success, pedido, error})=>{
                                    if(!success){ toast(error||'No se pudo poner en proceso', 'error'); return; }
                                    toast('Pedido en proceso','success');
                                    cerrar();
                                    cargarPedidosIniciales();
                                    try { window.BaresOrdenes && window.BaresOrdenes.refresh && window.BaresOrdenes.refresh(); } catch(e){}
                                })
                                .catch(()=> toast('Error de red', 'error'));
                        });
                    }

                    // Acción: Completar (descuenta stock en servidor)
                    const btnComp = backdrop.querySelector('[data-completar]');
                    if(btnComp){
                        btnComp.addEventListener('click', ()=>{
                            // Si está pendiente, primero pasarlo a en_proceso para respetar la secuencia
                            const encadenar = p.estado==='pendiente'
                                ? fetch(`/bar/pedido/${p.id}/estado/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ estado: 'en_proceso' }) }).then(r=>r.json())
                                : Promise.resolve({ success:true });
                            encadenar.then(()=>{
                                return fetch(`/bar/pedido/${p.id}/estado/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ estado: 'completado' }) })
                                    .then(r=>r.json());
                            }).then(({success, pedido, error})=>{
                                if(!success){ toast(error||'No se pudo completar', 'error'); return; }
                                toast('Pedido completado','success');
                                cerrar();
                                cargarPedidosIniciales();
                                try { window.BaresOrdenes && window.BaresOrdenes.refresh && window.BaresOrdenes.refresh(); } catch(e){}
                            }).catch(()=> toast('Error de red', 'error'));
                        });
                    }

                    // Acción: Editar (solo pendiente)
                    const btnEdit = backdrop.querySelector('[data-editar]');
                    if(btnEdit){
                        btnEdit.addEventListener('click', ()=>{
                            try{
                                cerrar();
                                editPedidoId = p.id;
                                cantidadesEstado.clear();
                                (p.productos||[]).forEach(d=>{
                                    const pid = d.producto_id || d.id; if(!pid) return;
                                    cantidadesEstado.set(pid, { id:pid, nombre:d.nombre, tipo:(d.plan==='pago'?'pago':'gratis'), precio: d.precio||0, cantidad: d.cantidad||1 });
                                });
                                const tipoSel = document.getElementById('pedido-tipo-consumo');
                                if(tipoSel){ tipoSel.value = p.tipo_consumo || 'bar'; tipoSel.dispatchEvent(new Event('change')); }
                                const instSel = document.getElementById('pedido-lugarentrega');
                                if(instSel && p.lugarentrega_id){ instSel.value = String(p.lugarentrega_id); instSel.dispatchEvent(new Event('change')); }
                                const habSel = document.getElementById('pedido-habitacion');
                                if(habSel && p.habitacion_id){ habSel.value = String(p.habitacion_id); habSel.dispatchEvent(new Event('change')); }
                                const empInp = document.getElementById('pedido-empleado');
                                if(empInp){ empInp.value = p.empleado_id || ''; empInp.dispatchEvent(new Event('input')); }
                                const notaInp = document.getElementById('pedido-nota');
                                if(notaInp){ notaInp.value = p.nota || ''; }
                                abrirModalCrear();
                                marcarSelectProductos();
                                syncCajaCantidades();
                            }catch(err){ console.error(err); toast('No se pudo cargar el pedido para edición','error'); }
                        });
                    }

                    return { backdrop };
                }

// Delegación para abrir detalle con click en botón o tarjeta
// Delegación de detalle se maneja dentro de init() una vez el DOM está listo

        /* ----------- Toast ----------- */
        function toast(msg, tipo='info'){
                let host = document.getElementById('toast-host');
                if(!host){ host=document.createElement('div'); host.id='toast-host'; host.style.position='fixed'; host.style.top='16px'; host.style.right='16px'; host.style.display='flex'; host.style.flexDirection='column'; host.style.gap='10px'; host.style.zIndex='5000'; document.body.appendChild(host); }
                const el = document.createElement('div');
                el.textContent=msg;
            if(tipo==='success'){
                el.style.background='#16a34a';
                el.style.color='#f0fdf4';
            } else {
                el.style.background='#0ea5e9';
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