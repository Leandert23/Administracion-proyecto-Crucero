// Órdenes: espejo de Pedidos solo para cambio de estado, sin historial ni edición
(function(){
  const ESTADOS = ['pendiente','en_proceso','completado'];
  // Estado local: mantener pedidos activos renderizados para abrir detalle
  let pedidosMap = new Map(); // id -> pedido

  function escapeHtml(str){
    if(str==null) return '';
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }

  function badgeEstado(estado){
    return `<span class="ord-estado ${estado}">${estado.replace('_',' ')}</span>`;
  }

  function cardOrden(p){
    const productosTxt = (p.productos||[]).map(d=> `${escapeHtml(d.nombre)} x${d.cantidad}`).join(', ');
    const lugarTxt = p.tipo_consumo==='camarote' ? `Habitación: ${escapeHtml(p.habitacion_nombre||'-')}` : `Lugar: ${escapeHtml(p.lugarentrega_nombre||'-')}`;
    const empTxt = p.empleado_nombre ? `${escapeHtml(p.empleado_nombre)}${p.empleado_categoria?` — ${escapeHtml(p.empleado_categoria)}`:''}` : (p.empleado_id??'-');
    const puedeEnProceso = p.estado==='pendiente';
    const puedeCompletar = p.estado==='en_proceso' || p.estado==='pendiente';
  return `
      <div class="orden-card ${p.estado}" data-id="${p.id}">
        <div class="orden-head">
          <div class="orden-id">#${p.id}</div>
          <div class="orden-factura">Factura: <span style="color:#059669;font-weight:600;">${p.numero_factura||'-'}</span></div>
          ${badgeEstado(p.estado)}
        </div>
        <div class="orden-body">
          <div class="orden-linea">${lugarTxt}</div>
          <div class="orden-linea">Empleado: ${empTxt}</div>
          <div class="orden-linea productos">${productosTxt||'-'}</div>
        </div>
        <div class="orden-actions">
      <button class="btn btn-detalle" data-accion="detalle" data-id="${p.id}">Ver Detalle</button>
        </div>
      </div>`;
  }

  function renderPorCategoria(items){
    const host = document.getElementById('ordenes-contenedor');
    if(!host) return;
    host.innerHTML = '';
    pedidosMap = new Map();
    const activos = (items||[]).filter(p=> p.estado!=='completado');
    if(!activos.length){
      host.innerHTML = '<div class="ordenes-empty">No hay órdenes.</div>';
      return;
    }
    // Agrupar por categoria (cargo) del empleado
    const grupos = new Map(); // categoria -> [pedidos]
    activos.forEach(p=>{
      const cat = p.empleado_categoria || 'Sin categoría';
      if(!grupos.has(cat)) grupos.set(cat, []);
      grupos.get(cat).push(p);
      pedidosMap.set(p.id, p);
    });
    // Render
    grupos.forEach((lista, categoria)=>{
      const sec = document.createElement('section');
      sec.className = 'orden-grupo';
      sec.innerHTML = `<h3 class="orden-grupo-titulo">${escapeHtml(categoria)}</h3><div class="orden-grid"></div>`;
      const grid = sec.querySelector('.orden-grid');
      lista.forEach(p=>{ grid.insertAdjacentHTML('beforeend', cardOrden(p)); });
      host.appendChild(sec);
    });
  }

  function cargarPedidosActivos(){
    return fetch('/bar/pedidos/?scope=activos').then(r=>r.json()).then(j=>{
      if(!j || !j.success) throw new Error('No se pudo cargar pedidos');
      renderPorCategoria(j.items||[]);
    }).catch(err=>{
      console.warn('[Órdenes] Error', err);
      const host = document.getElementById('ordenes-contenedor');
      if(host) host.innerHTML = '<div class="ordenes-empty">No se pudieron cargar las órdenes.</div>';
    });
  }

  function actualizarEstado(id, estado){
    return fetch(`/bar/pedido/${id}/estado/`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ estado }) })
      .then(r=>r.json());
  }

  function onClick(e){
    const btn = e.target.closest('[data-accion]');
    if(!btn) return;
    const id = parseInt(btn.getAttribute('data-id'), 10);
    const acc = btn.getAttribute('data-accion');
    if(acc === 'detalle'){
      const pedido = pedidosMap.get(id);
      if(pedido){
        if(window.BaresPedidos && typeof window.BaresPedidos.abrirDetalleFactura === 'function'){
          try { window.BaresPedidos.abrirDetalleFactura(pedido); } catch(err) { console.warn('No se pudo abrir detalle', err); crearFacturaLocal(pedido); }
        } else {
          crearFacturaLocal(pedido);
        }
      }
      return;
    }
    // Respetar flujo: si era pendiente y se quiere completar, encadenar en_proceso -> completado
    if(acc === 'completado'){
      // Intentar primero poner en proceso; si falla por estado, ignorar
      actualizarEstado(id, 'en_proceso')
        .finally(()=> actualizarEstado(id, 'completado'))
        .then(({success, error})=>{
          if(!success){ console.warn('[Órdenes] No se pudo completar:', error); }
          cargarPedidosActivos();
          try { window.BaresPedidos && window.BaresPedidos.refresh && window.BaresPedidos.refresh(); } catch(e){}
        })
        .catch(()=> cargarPedidosActivos());
    } else if(acc === 'en_proceso'){
      actualizarEstado(id, 'en_proceso').then(()=> { cargarPedidosActivos(); try { window.BaresPedidos && window.BaresPedidos.refresh && window.BaresPedidos.refresh(); } catch(e){} }).catch(()=> cargarPedidosActivos());
    }
  }

  function init(){
    const host = document.getElementById('ordenes-contenedor');
    if(!host) return;
    host.addEventListener('click', onClick);
    cargarPedidosActivos();
    // refresco periódico simple
    setInterval(cargarPedidosActivos, 15000);
  // Exponer un pequeño API para que Pedidos pueda refrescar Órdenes
  try { window.BaresOrdenes = { refresh: cargarPedidosActivos }; } catch(e){}
  }

  // Factura local de respaldo (Producto | Cantidad | Receta + metadatos clave)
  function crearFacturaLocal(p){
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-pedido';
    backdrop.style.display = 'flex';
    const filas = (p.productos||[]).map(d=>{
      const nombre = d.nombre || '';
      const cant = d.cantidad != null ? d.cantidad : '';
      const receta = d.receta || '';
      return `<tr>
        <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb;">${nombre}</td>
        <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb; text-align:center;">${cant}</td>
        <td style="padding:8px 10px; border-bottom:1px solid #e5e7eb; color:#64748b;">${receta||'-'}</td>
      </tr>`;
    }).join('');
    const puedeEnProceso = p.estado==='pendiente';
    const puedeCompletar = p.estado==='en_proceso' || p.estado==='pendiente';
    backdrop.innerHTML = `
      <div class="modal-pedido-dialog recibo" style="max-width:560px; background:#fff; border:1px solid #e7eaf3;">
        <button class="modal-close" aria-label="Cerrar">×</button>
        <h2 class="modal-title">Factura Pedido #${p.id}</h2>
        <div style="font-family:'Fira Mono','Consolas',monospace; color:#475569; display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0 14px;">
          <div style="grid-column:1 / -1; color:#059669; font-weight:600;">Número de Factura: ${p.numero_factura||'-'}</div>
          <div>Estado: ${p.estado?.replace('_',' ')||'-'}</div>
          <div>Tipo: ${p.tipo_consumo==='camarote'?'Camarote':'Bar'}</div>
          <div>${p.tipo_consumo==='camarote'?'Habitación':'Lugar'}: ${p.tipo_consumo==='camarote'?(p.habitacion_nombre||'--'):(p.lugarentrega_nombre||'--')}</div>
          <div>Empleado: ${p.empleado_nombre ? p.empleado_nombre + (p.empleado_categoria?` — ${p.empleado_categoria}`:'') : (p.empleado_id??'-')}</div>
          <div>Fecha: ${p.fecha || '--'}</div>
          <div>Hora: ${p.hora || '--'}</div>
          ${p.nota?`<div style="grid-column:1 / -1;">Nota: ${p.nota}</div>`:''}
        </div>
        <div style="border:1px solid #e7eaf3; border-radius:10px; overflow:hidden;">
          <table style="width:100%; border-collapse:collapse;">
            <thead style="background:#f8fafc; text-align:left;">
              <tr>
                <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3;">Producto</th>
                <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3; text-align:center; width:96px;">Cantidad</th>
                <th style="padding:10px; font-weight:600; border-bottom:1px solid #e7eaf3;">Receta</th>
              </tr>
            </thead>
            <tbody>${filas||'<tr><td colspan="3" style="padding:10px; color:#64748b;">Sin productos</td></tr>'}</tbody>
          </table>
        </div>
        <div class="modal-acciones">
          ${puedeEnProceso?'<button class="btn modal-btn btn-proceso" data-proceso>Poner en proceso</button>':''}
          ${puedeCompletar?'<button class="btn modal-btn btn-completar" data-completar>Completar</button>':''}
        </div>
      </div>`;
    const close = ()=> backdrop.remove();
    backdrop.querySelector('.modal-close')?.addEventListener('click', close);
    backdrop.addEventListener('click', (e)=>{ if(e.target===backdrop) close(); });
    document.body.appendChild(backdrop);

    // Handlers de estado dentro del modal local
    const btnProc = backdrop.querySelector('[data-proceso]');
    if(btnProc){
      btnProc.addEventListener('click', ()=>{
        actualizarEstado(p.id, 'en_proceso').then(()=>{
          try { window.BaresPedidos?.refresh?.(); } catch(e){}
        }).finally(()=>{ cargarPedidosActivos(); close(); });
      });
    }
    const btnComp = backdrop.querySelector('[data-completar]');
    if(btnComp){
      btnComp.addEventListener('click', ()=>{
        const chain = p.estado==='pendiente' ? actualizarEstado(p.id, 'en_proceso') : Promise.resolve({success:true});
        chain.finally(()=> actualizarEstado(p.id, 'completado')).then(()=>{
          try { window.BaresPedidos?.refresh?.(); } catch(e){}
        }).finally(()=>{ cargarPedidosActivos(); close(); });
      });
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
