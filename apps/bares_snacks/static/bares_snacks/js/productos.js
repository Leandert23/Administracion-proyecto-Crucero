// Gestión de productos (Bares & Snacks) - Versión con filtros por plan y resumen inline
// --- Mantener ingredientes seleccionados globalmente entre cambios de tipo/subtipo ---
let ingredientesSeleccionadosGlobal = [];
// Gestión de productos (Bares & Snacks) - Versión con filtros por plan y resumen inline
(function(){
	// Stub for renderChips to prevent ReferenceError, now in correct scope
	function renderChips() {}
	const state = { productos: [], categorias: [], categoriaSeleccionada:'__ALL__', planFiltro:'todos', ingredientesCache:{}, cargando:false, edit:{active:false, producto:null} };
	let btnCrear, modal, form, contenedorProductos, selectFiltroCategoria, btnCerrarModal, planFiltrosWrap;
	let selectCategoriaFiltro, selectTipoAlmacen, selectSubtipoAlmacen, selectPlan, precioWrapper, inputPrecio, selectIngredientes, inputNombre, resumenList, contenedorTags, tablaIngredientes;
	let selectCategoria, selectSubcategoria, selectTipo;
	const ce = (t,c)=>{const e=document.createElement(t); if(c) e.className=c; return e;};

	function mapDom(){
		btnCrear = document.getElementById('btn-abrir-crear-producto');
		modal = document.getElementById('modal-crear-producto');
		form = document.getElementById('form-crear-producto');
		contenedorProductos = document.getElementById('productos-contenedor');
		selectFiltroCategoria = document.getElementById('filtro-categoria-select');
		planFiltrosWrap = document.getElementById('plan-filtros');
		btnCerrarModal = document.getElementById('close-modal-crear');
		selectCategoriaFiltro = document.getElementById('categoria-filtro-select');
		selectTipoAlmacen = document.getElementById('tipo-almacen-select');
		selectSubtipoAlmacen = document.getElementById('subtipo-almacen-select');
		selectPlan = document.getElementById('plan-producto');
		precioWrapper = document.getElementById('precio-wrapper');
		inputPrecio = document.getElementById('precio-input');
		selectIngredientes = document.getElementById('ingredientes-select');
		inputNombre = document.getElementById('nombre-producto');
		resumenList = document.getElementById('resumen-list');
		contenedorTags = document.getElementById('ingredientes-tags');
		tablaIngredientes = document.getElementById('ingredientes-tabla');
		selectCategoria = selectTipoAlmacen; selectSubcategoria = selectSubtipoAlmacen; selectTipo = selectPlan;
	}

	function abrirModal(){
		if(!modal) return;
		modal.setAttribute('aria-hidden','false');
		document.body.style.overflow='hidden';
		if(inputNombre){
			inputNombre.removeAttribute('readonly');
			inputNombre.removeAttribute('disabled');
		}
	}
	function setModalTitle(t){ const h = modal?.querySelector('.modal-title'); if(h) h.textContent=t; }
	function setSubmitText(t){ const b = form?.querySelector('button[type="submit"]'); if(b) b.textContent=t; }
	function cerrarModal(){
		if(!modal) return;
		modal.setAttribute('aria-hidden','true');
		document.body.style.overflow='';
		form?.reset();
		limpiarTags();
		selectIngredientes.innerHTML='';
		state.edit={active:false, producto:null};
		setModalTitle('Crear Producto');
		setSubmitText('Guardar');
		if(inputNombre){
			inputNombre.removeAttribute('readonly');
			inputNombre.removeAttribute('disabled');
		}
		actualizarResumen();
	}
	function togglePrecio(){ // siempre visible; sólo placeholder / validación
		const isPremium = (selectPlan?.value === 'premium');
		if(precioWrapper){ precioWrapper.style.display = isPremium ? '' : 'none'; }
		if(isPremium){
			if(!inputPrecio.value) inputPrecio.placeholder='Ej: 5.50';
		}else{
			// Oculto: limpia valor para evitar confusiones, backend ya trata gratis como 0
			if(inputPrecio){ inputPrecio.value=''; inputPrecio.placeholder='0.00'; }
		}
		actualizarResumen(); }

	async function api(u,opt={}){ const r= await fetch(u,{headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json','Content-Type':'application/json'},credentials:'same-origin',...opt}); if(!r.ok) throw new Error(r.status); return r.json(); }

	async function cargarCategorias(){
		try {
			const data = await api('/bar/categorias-almacen/');
			// Solo dejar los que tienen mostrar:true
				state.categorias = Array.isArray(data)
					? data.filter(c => c.mostrar).slice(0,3).map(c => ({
							id: c.id??c.pk??c.codigo??c.code??c.value,
							nombre: c.nombre??c.name??c.descripcion??'Sin nombre',
							subcategorias: c.subcategorias??c.subtipos??c.sub_tipos??c.subTipos??c.children??c.lista_subtipos??[]
						}))
					: [];
			poblarSelectCategorias();
		} catch(e){
			console.error('Cat',e);
		}
	}
	function poblarSelectCategorias(){ selectTipoAlmacen.innerHTML='<option value="">Selecciona tipo</option>'+ state.categorias.map(c=>`<option value="${c.id}">${escapeHtml(c.nombre)}</option>`).join(''); selectSubtipoAlmacen.innerHTML='<option value="">Selecciona subtipo</option>'; }
	function getSubtipos(c){ return c? c.subcategorias||c.subtipos||c.sub_tipos||c.subTipos||c.children||[]:[]; }
	function onChangeCategoria() {
		const catId = selectTipoAlmacen.value;
		const cat = state.categorias.find(c => String(c.id) === catId);
		const subs = getSubtipos(cat);
	// Guardar ingredientes seleccionados en variable global antes de limpiar, incluyendo cantidad y stock
	const actuales = obtenerIngredientesSeleccionados();
	// Fusionar sin duplicados, manteniendo cantidad y stock
	ingredientesSeleccionadosGlobal = actuales.concat(
		ingredientesSeleccionadosGlobal.filter(ingOld => !actuales.some(ingNew => ingNew.id === ingOld.id))
	);
		if (!cat) {
			selectSubtipoAlmacen.innerHTML = '<option value="">Selecciona subtipo</option>';
			selectIngredientes.innerHTML = '';
		limpiarTags();
		// Restaurar todos los tags de ingredientes seleccionados globalmente, manteniendo cantidad y stock
		ingredientesSeleccionadosGlobal.forEach(ing => {
			agregarTagIngrediente({
				id: ing.id,
				nombre: ing.nombre,
				unidad: ing.unidad,
				stock: ing.stock,
				cantidad: ing.cantidad // Mantener la cantidad ingresada
			});
		});
		actualizarResumen();
			return;
		}
		if (!subs.length) {
			selectSubtipoAlmacen.innerHTML = '<option value="">(Sin subtipos)</option>';
			selectIngredientes.innerHTML = '';
			limpiarTags();
			ingredientesSeleccionadosGlobal.forEach(ing => agregarTagIngrediente(ing));
			actualizarResumen();
			return;
		}
		selectSubtipoAlmacen.innerHTML = '<option value="">Selecciona subtipo</option>' + subs.map(s => {
			const sid = s.id ?? s.pk ?? s.codigo ?? s.code ?? s.value;
			const sn = s.nombre ?? s.name ?? s.descripcion ?? 'Subtipo';
			return `<option value="${sid}">${escapeHtml(sn)}</option>`;
		}).join('');
		selectIngredientes.innerHTML = '';
		limpiarTags();
		// Restaurar los tags de ingredientes seleccionados globalmente
		ingredientesSeleccionadosGlobal.forEach(ing => agregarTagIngrediente(ing));
		actualizarResumen();
	}
	async function onChangeSubcategoria() {
		const catId = selectTipoAlmacen.value;
		const subId = selectSubtipoAlmacen.value;
	// Guardar ingredientes seleccionados en variable global antes de limpiar
	const actuales = obtenerIngredientesSeleccionados();
	// Fusionar sin duplicados
	ingredientesSeleccionadosGlobal = actuales.concat(ingredientesSeleccionadosGlobal.filter(ingOld => !actuales.some(ingNew => ingNew.id === ingOld.id)));
		if (!catId || !subId) {
			selectIngredientes.innerHTML = '';
			if (tablaIngredientes) tablaIngredientes.innerHTML = '';
		limpiarTags();
		// Restaurar todos los tags de ingredientes seleccionados globalmente
		ingredientesSeleccionadosGlobal.forEach(ing => agregarTagIngrediente(ing));
			return;
		}
		const key = `${catId}|${subId}`;
		if (!state.ingredientesCache[key]) {
			try {
				selectIngredientes.innerHTML = '<option>Cargando ingredientes...</option>';
				let ing = [];
				try {
					const d = await api(`/bar/productos-almacen-filtrados/?tipo=${encodeURIComponent(catId)}&subtipo=${encodeURIComponent(subId)}`);
					ing = extraerIngredientes(d);
				} catch (err) { console.warn('Fallback a ingredientes almacen', err); }
				if (!ing.length) {
					try {
						const todos = await api('/bar/ingredientes-almacen/');
						ing = (Array.isArray(todos) ? todos : []).filter(x => (String(x.tipo) === String(catId)) && (!subId || String(x.subtipo || x.sub_tipo || '') === String(subId)));
					} catch (err2) { console.error('Error fallback ingredientes almacen', err2); }
				}
				state.ingredientesCache[key] = ing;
			} catch (e) { console.error('Ing', e); state.ingredientesCache[key] = []; }
		}
		poblarIngredientes(key);
		limpiarTags();
		// Restaurar los tags de ingredientes seleccionados globalmente
		ingredientesSeleccionadosGlobal.forEach(ing => agregarTagIngrediente(ing));
		renderTablaIngredientes(key);
	}
	function poblarIngredientes(key){ const list= state.ingredientesCache[key]||[]; if(!list.length){ selectIngredientes.innerHTML='<option value="">(Sin ingredientes)</option>'; actualizarResumen(); return; } selectIngredientes.size=Math.min(12,Math.max(6,list.length)); selectIngredientes.innerHTML=list.map(i=>{ const id=i.id??i.pk??i.codigo??i.code??i.value; const nombre=i.nombre||i.nombre_producto||i.descripcion||'Ingrediente'; const unidad=normalizarUnidad(i.unidad||i.unidad_medida||i.unidadMedida||i.medida||i.tipo_unidad||i.presentacion); const stock = (i.stock??i.cantidad??i.cantidad_disponible??i.disponible??i.existencias); const stockMostrar = (stock===0 || stock>0)? stock : ''; const detalle=[unidad, (stockMostrar!==''?`Stock:${stockMostrar}`:null)].filter(Boolean).join(' · '); return `<option value="${id}" data-unidad="${escapeHtml(unidad)}" data-stock="${stockMostrar}">${escapeHtml(nombre)}${detalle?` (${escapeHtml(detalle)})`:''}</option>`; }).join(''); actualizarResumen(); }

	function renderTablaIngredientes(key){ if(!tablaIngredientes) return; const list = state.ingredientesCache[key]||[]; if(!list.length){ tablaIngredientes.innerHTML = '<div class="tabla-vacia">No hay ingredientes para este tipo/subtipo.</div>'; return; } const rows = list.map(i=>{ const id=i.id??i.pk??i.codigo??i.code??i.value; const nombre=escapeHtml(i.nombre||i.nombre_producto||i.descripcion||'Ingrediente'); const unidad=escapeHtml(normalizarUnidad(i.unidad||i.unidad_medida||i.unidadMedida||i.medida||i.tipo_unidad||i.presentacion)||''); const stock = (i.stock??i.cantidad??i.cantidad_disponible??i.disponible??i.existencias); const stockMostrar = (stock===0 || stock>0)? stock : ''; return `<tr data-id="${id}" data-nombre="${nombre}" data-unidad="${unidad}" data-stock="${stockMostrar}"><td>${nombre}</td><td>${unidad||''}</td><td style="text-align:right;">${stockMostrar!==''?stockMostrar:''}</td><td><button type="button" class="btn-mini-add">Agregar</button></td></tr>`; }).join(''); tablaIngredientes.innerHTML = `<table class="tabla-ingredientes"><thead><tr><th>Producto</th><th>Unidad</th><th>Stock</th><th></th></tr></thead><tbody>${rows}</tbody></table>`; tablaIngredientes.querySelectorAll('button.btn-mini-add').forEach(btn=>{ btn.addEventListener('click', (e)=>{ const tr=e.target.closest('tr'); if(!tr) return; const id=tr.getAttribute('data-id'); const nombre=tr.getAttribute('data-nombre'); const unidad=tr.getAttribute('data-unidad'); const stock=tr.getAttribute('data-stock'); agregarTagIngrediente({id, nombre, unidad, stock}); actualizarResumen(); }); }); }
	function extraerIngredientes(data){ if(!data) return []; if(Array.isArray(data.ingredientes)) return data.ingredientes; if(Array.isArray(data.items)) return data.items; if(Array.isArray(data.lista)) return data.lista; if(Array.isArray(data)) return data; return []; }
	function normalizarUnidad(u){ if(!u) return ''; const t=String(u).toLowerCase(); if(/mililit/.test(t)||t==='ml') return 'ml'; if(/^l(itro)?s?$/.test(t)||t==='lt') return 'L'; if(/gram/.test(t)||t==='gr'||t==='g') return 'g'; if(/unidad|unid|u$/.test(t)) return 'und'; if(/kilo|kg/.test(t)) return 'kg'; return u; }

	function poblarSelectFiltro(){
		if(!selectFiltroCategoria) return;
		const productosPlan = filtrarPorPlan(state.productos);
		const g = agruparPorCategoria(productosPlan);
		const prev = state.categoriaSeleccionada;
		selectFiltroCategoria.innerHTML = '<option value="__ALL__">Todas</option>' + state.categorias.map(cat=>{
			const count=(g[cat.id]||[]).length;
			return `<option value="${cat.id}">${escapeHtml(cat.nombre)} (${count})</option>`;
		}).join('');
		if(prev && [...selectFiltroCategoria.options].some(o=>o.value===prev)){
			selectFiltroCategoria.value=prev;
		}else{
			state.categoriaSeleccionada='__ALL__';
		}
	}
	function agruparPorCategoria(list){ return list.reduce((a,p)=>{ const id=p.categoria_id||p.categoria||'0'; (a[id]||(a[id]=[])).push(p); return a; },{}); }
	function filtrarPorPlan(list){
		if(state.planFiltro==='todos') return list;
		return list.filter(p=>{
			const t=p.tipo; // ya normalizado
			if(state.planFiltro==='premium') return t==='pago';
			if(state.planFiltro==='all_inclusive') return t==='gratis';
			return true;
		});
	}

	function renderProductos(){ if(!contenedorProductos) return; const productosPlan=filtrarPorPlan(state.productos); if(!productosPlan.length){ contenedorProductos.innerHTML='<div id="productos-empty" class="productos-empty">No hay productos.</div>'; return;} const g=agruparPorCategoria(productosPlan); let ids=Object.keys(g); if(state.categoriaSeleccionada && state.categoriaSeleccionada!=='__ALL__'){ ids=ids.filter(id=> id===state.categoriaSeleccionada); } if(!ids.length){ contenedorProductos.innerHTML='<div class="productos-empty">No hay productos para el filtro seleccionado.</div>'; return;} const frag=document.createDocumentFragment(); ids.forEach(id=>{ const cat=state.categorias.find(c=>String(c.id)===id); const nombreCat=cat?cat.nombre:'Categoría'; const wrap=ce('section','categoria-wrapper'); wrap.dataset.catId=id; const header=ce('div','categoria-header'); const title=ce('h3','categoria-title'); title.innerHTML=`${escapeHtml(nombreCat)} <span class="categoria-count">${g[id].length}</span>`; header.appendChild(title); wrap.appendChild(header); const grid=ce('div','productos-grid'); g[id].forEach(p=>grid.appendChild(crearCardProducto(p))); wrap.appendChild(grid); frag.appendChild(wrap); }); contenedorProductos.innerHTML=''; contenedorProductos.appendChild(frag); }
	function crearCardProducto(p){
		const card=ce('div','product-card');
		card.dataset.id = p.id;
		if(p.origen) card.dataset.origen = p.origen;
		const nombre=ce('h4','product-name'); nombre.textContent=p.nombre||'Producto';
		const tags=ce('div','product-tags');
		const tipoTag=ce('span','tag '+(p.tipo==='pago'?'premium':'gratis'));
		if(p.tipo==='pago'){
			tipoTag.textContent = 'PAGO';
		}else{
			tipoTag.textContent = 'ALL INCLUSIVE';
		}
		tags.appendChild(tipoTag);
		if(p.tipo==='pago'&&p.precio){ const price=ce('span','price'); price.textContent=formatPrecio(p.precio); tags.appendChild(price);} 
		const acciones=ce('div','card-actions');
		const btns=ce('div','card-btns');
		bDel=ce('button','icon-btn delete'); bDel.type='button'; bDel.innerHTML='<span style="font-size:1.2em; font-weight:bold; color:#dc2626;">×</span>';
		bEdit=ce('button','icon-btn edit'); bEdit.type='button'; bEdit.innerHTML='<svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 13.5V16H6.5L14.81 7.69L12.31 5.19L4 13.5Z" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M13.5 6.5L15 8" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
		bInfo=ce('button','icon-btn info'); bInfo.type='button'; bInfo.innerHTML='<span style="font-size:1.2em; font-weight:bold; color:#2563eb;">i</span>'; bInfo.title='Ver más';
		bDel.addEventListener('click', ()=> intentarEliminarProducto(card, p));
	bEdit.addEventListener('click', async ()=> await abrirEdicionProducto(p));
		bInfo.addEventListener('click', ()=> verMasProducto(p));
		btns.appendChild(bInfo); btns.appendChild(bEdit); btns.appendChild(bDel);
		acciones.appendChild(btns);
		card.appendChild(nombre); card.appendChild(tags); card.appendChild(acciones);
		return card;
	}

	async function verMasProducto(p){
		const modal = document.getElementById('modal-detalle-producto');
		const titulo = document.getElementById('detalle-producto-titulo');
		const body = document.getElementById('detalle-producto-body');
		if(!modal||!titulo||!body) return;
		titulo.textContent = `Detalle: ${p.nombre}`;
		body.innerHTML = '<div class="cargando">Cargando...</div>';
		modal.setAttribute('aria-hidden','false');
		document.body.style.overflow='hidden';
		try{
			const data = await api(`/bar/producto-bar/${encodeURIComponent(p.id)}/receta/`);
			if(!data.success){ throw new Error(data.error||'Error'); }
			if(!data.items.length){ body.innerHTML = '<div class="vacio">Sin ingredientes de receta.</div>'; return; }
						const rows = data.items.map(it=>{
								let cantidad = (typeof it.cantidad === 'number') ? it.cantidad.toFixed(2) : (parseFloat(it.cantidad).toFixed(2) || it.cantidad || '');
								let unidad = (it.unidad||'').toUpperCase();
								let equivalencia = '';
								if(unidad === 'K') {
									let gramos = parseFloat(it.cantidad) * 1000;
									if(!isNaN(gramos)) equivalencia = `<span class='eq' style='color:#64748b;font-size:0.9em;'>(= ${gramos.toFixed(2)} g)</span>`;
								} else if(unidad === 'L') {
									let ml = parseFloat(it.cantidad) * 1000;
									if(!isNaN(ml)) equivalencia = `<span class='eq' style='color:#64748b;font-size:0.9em;'>(= ${ml.toFixed(2)} ml)</span>`;
								}
								return `<tr><td>${escapeHtml(it.ingrediente_nombre||'')}</td><td style="text-align:right;">${cantidad} ${equivalencia}</td><td>${escapeHtml(it.unidad||'')}</td></tr>`;
						}).join('');
			body.innerHTML = `<table class="tabla-ingredientes-detalle"><thead><tr><th>Ingrediente</th><th>Cantidad</th><th>Unidad</th></tr></thead><tbody>${rows}</tbody></table>`;
		}catch(err){ console.error(err); body.innerHTML='<div class="error">No se pudo cargar la receta.</div>'; }
	}

	document.addEventListener('DOMContentLoaded', function(){
		// Modal detalle producto
		var modalDetalle = document.getElementById('modal-detalle-producto');
		var btnCloseDetalle = document.getElementById('close-modal-detalle');
		if (btnCloseDetalle && modalDetalle) {
			btnCloseDetalle.addEventListener('click', function() {
				modalDetalle.setAttribute('aria-hidden','true');
				document.body.style.overflow='';
			});
		}
		if (modalDetalle) {
			modalDetalle.addEventListener('click', function(e) {
				if(e.target===modalDetalle){
					modalDetalle.setAttribute('aria-hidden','true');
					document.body.style.overflow='';
				}
			});
			document.addEventListener('keydown', function escDetalleListener(e) {
				if(e.key==='Escape' && modalDetalle.getAttribute('aria-hidden')==='false'){
					modalDetalle.setAttribute('aria-hidden','true');
					document.body.style.overflow='';
				}
			});
		}
	});

	async function abrirEdicionProducto(p){
	// Activar modo edición y prellenar formulario con los datos actuales
	state.edit = { active:true, producto:p };
	setModalTitle('Editar Producto');
	setSubmitText('Guardar cambios');

	// Nombre
	if(inputNombre){
		inputNombre.value = p.nombre || '';
		inputNombre.setAttribute('readonly', 'readonly');
	}

	// Categoría (filtro)
	if(selectCategoriaFiltro){
		let target = String(p.categoria || p.categoria_id || '');
		let opt = Array.from(selectCategoriaFiltro.options).find(o => o.value===target || o.textContent.trim()===target);
		selectCategoriaFiltro.value = opt ? opt.value : '';
	}

	// Tipo almacén y subtipo: esperar a que los selects estén poblados
	const tipoVal = p.tipo_categoria || p.tipo_almacen || p.categoria_id || '';
	const subVal = p.subtipo_categoria || p.subtipo_almacen || p.subcategoria_id || '';

	if(selectTipoAlmacen){
		selectTipoAlmacen.value = String(tipoVal||'');
		// Esperar a que se cargue el subtipo
		await onChangeCategoria();
	}

	if(selectSubtipoAlmacen){
		selectSubtipoAlmacen.value = String(subVal||'');
		// Esperar a que se carguen los ingredientes
		await onChangeSubcategoria();
	}

	// Plan
	if(selectPlan){ selectPlan.value = (p.tipo==='pago') ? 'premium' : 'all_inclusive'; }

	// Precio
	if(inputPrecio){ inputPrecio.value = (p.precio!=null ? p.precio : (p.precio_vta!=null ? p.precio_vta : '')); }
	togglePrecio();

	// Limpiar solo los tags de ingredientes
	if(contenedorTags) contenedorTags.innerHTML = '';



	// Mostrar ingredientes actuales de la receta (solo informativo)
	const contActuales = document.getElementById('ingredientes-actuales');
	const listaActuales = document.getElementById('ingredientes-actuales-list');
	if(contActuales && listaActuales) {
		contActuales.style.display = 'none';
		listaActuales.innerHTML = '';
	}
	if(p.id && p.origen === 'producto_bar'){
		try {
			const recetaResp = await api(`/bar/producto-bar/${encodeURIComponent(p.id)}/receta/`);
			if(recetaResp.success && Array.isArray(recetaResp.items)){
				// Mostrar ingredientes actuales en formato tabla igual que en detalle
				if(contActuales && listaActuales){
					if(recetaResp.items.length){
						let rows = recetaResp.items.map(it=>{
							let cantidad = (typeof it.cantidad === 'number') ? it.cantidad.toFixed(2) : (parseFloat(it.cantidad).toFixed(2) || it.cantidad || '');
							let unidad = (it.unidad||'').toUpperCase();
							let equivalencia = '';
							if(unidad === 'K') {
								let gramos = parseFloat(it.cantidad) * 1000;
								if(!isNaN(gramos)) equivalencia = `<span class='eq' style='color:#64748b;font-size:0.9em;'>(= ${gramos.toFixed(2)} g)</span>`;
							} else if(unidad === 'L') {
								let ml = parseFloat(it.cantidad) * 1000;
								if(!isNaN(ml)) equivalencia = `<span class='eq' style='color:#64748b;font-size:0.9em;'>(= ${ml.toFixed(2)} ml)</span>`;
							}
							return `<tr><td>${escapeHtml(it.ingrediente_nombre||'')}</td><td style=\"text-align:right;\">${cantidad} ${equivalencia}</td><td>${escapeHtml(it.unidad||'')}</td></tr>`;
						}).join('');
						listaActuales.innerHTML = `<table class=\"tabla-ingredientes-detalle\"><thead><tr><th>Ingrediente</th><th>Cantidad</th><th>Unidad</th></tr></thead><tbody>${rows}</tbody></table>`;
						contActuales.style.display = '';
					} else {
						listaActuales.innerHTML = '<div class=\"vacio\">Sin ingredientes de receta.</div>';
						contActuales.style.display = 'none';
					}
				}
				// También agregar los tags para edición normal
				recetaResp.items.forEach(item => {
					agregarTagIngrediente({
						id: item.ingrediente_id,
						nombre: item.ingrediente_nombre,
						unidad: item.unidad || '',
						cantidad: item.cantidad,
						stock: ''
					});
					// Marcar como seleccionado en el select múltiple
					if(selectIngredientes){
						const opt = Array.from(selectIngredientes.options).find(o => String(o.value) === String(item.ingrediente_id));
						if(opt) opt.selected = true;
					}
				});
			}
		} catch(e){
			console.error('No se pudieron cargar los ingredientes actuales', e);
		}
	}

	abrirModal();
	}

	async function intentarEliminarProducto(card, p){
		const nombre = p.nombre || 'este producto';
		if(!confirm(`¿Eliminar ${nombre}?`)) return;
		card.classList.add('deleting');
		let recargando = false;
		try {
			const resp = await fetch('/bar/eliminar-producto-bar/', { method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'}, body: JSON.stringify({ id: p.id, origen: p.origen }) });
			let data;
			try {
				data = await resp.json();
			} catch(jsonErr) {
				// If response is not valid JSON
				throw new Error('Respuesta inválida del servidor.');
			}
			if(resp.ok && data.success){
				recargando = true;
				window.location.reload();
				return;
			}
			// Solo mostrar error si el backend responde con error
			throw new Error(data.error||'Error eliminando');
		}catch(err){ 
			console.error(err); 
			if(!recargando){
				alert('No se pudo eliminar: ' + (err.message || 'Error desconocido'));
			}
			card.classList.remove('deleting'); 
		}
	}

	function mostrarToastInfo(titulo, detalle){
		const toast=document.createElement('div');
		toast.className='producto-toast info';
		toast.innerHTML=`<div class="fila"><strong class="nombre">${escapeHtml(titulo)}</strong></div><div class="detalle">${escapeHtml(detalle)}</div>`;
		document.body.appendChild(toast);
		requestAnimationFrame(()=>toast.classList.add('show'));
		setTimeout(()=>{ toast.classList.add('hide'); setTimeout(()=>toast.remove(), 400); }, 3000);
	}
	// (inline summary eliminado en favor de box global)

	function onAddIngredientesDesdeSelect(){ if(!selectIngredientes) return; Array.from(selectIngredientes.selectedOptions).forEach(o=>{ const id=o.value; if(!id) return; if(contenedorTags.querySelector(`[data-id="${CSS.escape(id)}"]`)) return; const unidad=o.getAttribute('data-unidad')||''; const stock=o.getAttribute('data-stock')||''; const nombreRaw=o.textContent.trim().replace(/\s*\([^)]*\)$/,''); agregarTagIngrediente({id, nombre:nombreRaw, unidad, stock}); }); selectIngredientes.selectedIndex=-1; Array.from(selectIngredientes.options).forEach(o=>o.selected=false); actualizarResumen(); }
	function agregarTagIngrediente(obj){
		if(!contenedorTags) return;
		// Si el tag ya existe, solo modificar la cantidad
		const existingTag = contenedorTags.querySelector(`[data-id="${CSS.escape(obj.id)}"]`);
		if (existingTag) {
			const inputCantidad = existingTag.querySelector('.input-cantidad');
			if (inputCantidad && typeof obj.cantidad !== 'undefined') {
				inputCantidad.value = obj.cantidad;
				inputCantidad.dispatchEvent(new Event('input'));
			}
			return;
		}
		// Si es nuevo, agregar el tag con el span de stock
		const tag=document.createElement('div');
		tag.className='ingrediente-tag';
		tag.dataset.id=obj.id;
		// Limpiar el texto 'Stock:' si ya está incluido en obj.stock
		let stockValue = obj.stock || '';
		stockValue = stockValue.replace(/^(Stock:\s*)+/i, '');
		const stockNum = parseFloat(stockValue);
		const tieneStock = !isNaN(stockNum) && stockNum>0;
		const statusTxt = tieneStock ? 'Disponible' : 'Sin stock';
		const stockTxt=stockValue!==''?`Stock: ${escapeHtml(stockValue)}`:'';
		const cantidad = (typeof obj.cantidad !== 'undefined') ? obj.cantidad : '';
		let unidadDesc = '';
		if(obj.unidad && obj.unidad.toUpperCase() === 'K') unidadDesc = ' (kilogramos)';
		else if(obj.unidad && obj.unidad.toUpperCase() === 'L') unidadDesc = ' (litros)';
		tag.innerHTML = `
			<span class="nombre">${escapeHtml(obj.nombre)}</span>
			<input type="number" class="input-cantidad" min="0" step="0.001" placeholder="Cantidad" value="${cantidad}" style="width:60px; margin:0 6px;" />
			<span class="conversion-eq"></span>
			${obj.unidad?`<span class="unidad">${escapeHtml(obj.unidad)}${unidadDesc}</span>`:''}
			${stockTxt?`<span class=\"stock\">${stockTxt}</span>`:''}
			<span class="status ${tieneStock?'disponible':'sin-stock'}">${statusTxt}</span>
			<button type="button" class="remove" aria-label="Eliminar">×</button>
		`;
		const inputCantidad = tag.querySelector('.input-cantidad');
		const eqSpan = tag.querySelector('.conversion-eq');
		function actualizarEq(){
			let val = parseFloat(inputCantidad.value);
			let unidad = (obj.unidad||'').toUpperCase();
			let eq = '';
			if(!isNaN(val)){
				if(unidad==='K') eq = `${(val*1000).toFixed(3)} g`;
				else if(unidad==='L') eq = `${(val*1000).toFixed(3)} ml`;
			}
			eqSpan.textContent = eq;
		}
		inputCantidad && inputCantidad.addEventListener('input', actualizarEq);
		setTimeout(actualizarEq, 10);
		tag.querySelector('button.remove').addEventListener('click',()=>{ tag.remove(); actualizarResumen(); });
		contenedorTags.appendChild(tag);
	}
	function limpiarTags(){ if(contenedorTags) contenedorTags.innerHTML=''; }
	function obtenerIngredientesSeleccionados(){
		if(!contenedorTags) return [];
		return Array.from(contenedorTags.querySelectorAll('.ingrediente-tag')).map(t=>({
			id: t.dataset.id,
			nombre: t.querySelector('.nombre')?.textContent.trim()||'',
			unidad: t.querySelector('.unidad')?.textContent.trim()||'',
			stock: t.querySelector('.stock')?.textContent.trim()||'',
			cantidad: (()=>{
				const input = t.querySelector('.input-cantidad');
				return input ? input.value : '';
			})()
		}));
	}

	async function onSubmit(e){ e.preventDefault(); if(state.cargando) return; const fd=new FormData(form); const ingredientesSeleccionados=obtenerIngredientesSeleccionados(); const nombre=(fd.get('nombre')||'').trim()||inputNombre.value.trim(); const tipoCat= fd.get('tipo_almacen')||selectTipoAlmacen.value||''; const subTipoCat= fd.get('subtipo_almacen')||selectSubtipoAlmacen.value||''; const plan = fd.get('plan')||selectPlan.value||'all_inclusive'; const esPremium = plan==='premium'; const precioBruto = parseFloat(fd.get('precio')||inputPrecio.value||'0')||0; if(!nombre||!tipoCat||!subTipoCat){ alert('Completa nombre, tipo y subtipo.'); return;} if(esPremium && precioBruto<=0){ alert('Ingresa precio (>0) para Premium.'); return;} const precioVal = precioBruto; const categoriaFiltroVal = document.getElementById('categoria-filtro-select')?.value||''; const payloadBase={ nombre, categoria: categoriaFiltroVal, tipo_categoria: tipoCat, subtipo_categoria: subTipoCat, tipo: esPremium?'pago':'gratis', precio: precioVal };
	try { 
		state.cargando=true; 
		let data=null; 
		if(state.edit.active && state.edit.producto){
			// Actualizar producto
			const payload = { id: state.edit.producto.id, ...payloadBase };
			const resp = await fetch('/bar/actualizar-producto-bar/', { method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'}, body: JSON.stringify(payload) });
			data = await resp.json();
			if(!resp.ok || !data.success){ console.error('Error actualización', data); alert('Error actualizando producto'); return; }
			// Guardar receta/ingredientes
			console.log('Ingredientes seleccionados para receta:', ingredientesSeleccionados);
			const recetaPayload = { items: ingredientesSeleccionados.map(i=>({ id: i.id, ingrediente_id: i.id, cantidad: i.cantidad, unidad: i.unidad })) };
			console.log('Payload enviado a guardar-receta:', recetaPayload);
		const recetaResp = await fetch(`/bar/producto-bar/${state.edit.producto.id}/receta/guardar/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
				body: JSON.stringify(recetaPayload)
			});
			const recetaData = await recetaResp.json();
			if(!recetaResp.ok || !recetaData.success){
				console.error('Error guardando receta', recetaData);
				alert('Error guardando ingredientes de la receta: ' + (recetaData.error || JSON.stringify(recetaData)));
				return;
			}
			// Refrescar en memoria
			const idx = state.productos.findIndex(x=> String(x.id)===String(state.edit.producto.id));
			if(idx>=0){ state.productos[idx] = { ...state.productos[idx], nombre, tipo: payloadBase.tipo, precio: precioVal, categoria: categoriaFiltroVal, tipo_categoria: tipoCat, subtipo_categoria: subTipoCat, categoria_id: tipoCat, subcategoria_id: subTipoCat } }
			renderChips(); renderProductos(); cerrarModal(); mostrarToastInfo('Producto actualizado', nombre);
		}else{
			// Crear
			const payload = { ...payloadBase, ingredientes: ingredientesSeleccionados.map(i=>i.id) };
			let respRaw = await fetch('/bar/crear-producto-bar/', {method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'}, body: JSON.stringify(payload)});
			try { data= await respRaw.json(); } catch(parseErr){ const txt= await respRaw.text(); console.error('Respuesta no JSON', txt); throw new Error('Formato inesperado'); }
			if(!respRaw.ok || !data.success){ console.error('Error creación', data); alert('Error creando producto'); return; }
			await cargarProductosInicial(); // fallback: producto creado por nombre o último
			let creado = state.productos.slice().reverse().find(p=> (p.nombre||'').trim().toLowerCase() === nombre.toLowerCase());
			if(!creado && state.productos.length){ creado = state.productos[state.productos.length-1]; }
			renderChips(); renderProductos(); cerrarModal(); mostrarResumenCreado(creado || {nombre, tipo: esPremium?'pago':'gratis', precio: precioVal}, ingredientesSeleccionados.length, esPremium);
		}
	} catch(err){ console.error(err); alert('Error en operación'); } finally { state.cargando=false; } }
	function mostrarResumenCreado(prod, cantidadIng, esPremium){
		// Eliminar cualquier toast anterior
		document.querySelectorAll('.producto-toast').forEach(n=>n.remove());
		const toast = document.createElement('div');
		toast.className='producto-toast';
		const planTag= esPremium ? 'Premium' : 'All Inclusive';
		const precioTxt = esPremium && prod.precio ? `<span class="precio">${formatPrecio(prod.precio)}</span>` : '';
		toast.innerHTML=`<div class="fila"><span class="plan ${esPremium?'premium':'allinc'}">${planTag}</span><strong class="nombre">${escapeHtml(prod.nombre)}</strong>${precioTxt}</div>
		<div class="detalle">Ingredientes seleccionados: ${cantidadIng}</div>`;
		document.body.appendChild(toast);
		requestAnimationFrame(()=>toast.classList.add('show'));
		setTimeout(()=>{ toast.classList.add('hide'); setTimeout(()=>toast.remove(), 400); }, 4200);
	}
	function resolverTipoPlan(p){
		let raw = (p.tipo||p.plan||p.tipo_plan||p.modalidad||p.modo||'').toString().toLowerCase();
		if(!raw){
			if(p.es_premium || p.is_premium || p.premium===true) raw='premium';
		}
		if(['pago','premium','prem','pay','de_pago'].includes(raw)) return 'pago';
		if(['gratis','all_inclusive','all-inclusive','incluido','incluida','free','libre','sin_costo','sin-costo'].includes(raw)) return 'gratis';
		const price = parseFloat(p.precio||p.price||0);
		if(price>0) return 'pago';
		return 'gratis';
	}
	function normalizarProducto(p){
		let catId = p.tipo_categoria||p.tipo_almacen||p.categoria_id||p.categoria||String(selectTipoAlmacen.value||'');
		if(!state.categorias.some(c=>String(c.id)===String(catId))){
			const byName=state.categorias.find(c=> c.nombre === p.categoria || c.nombre === p.categoria_id || c.nombre === p.tipo_almacen);
			if(byName) catId = byName.id;
		}
		const tipoNorm = resolverTipoPlan(p);
		return { id:p.id||p.pk||Date.now(), nombre:p.nombre||p.nombre_producto||'Producto', categoria_id: catId, subcategoria_id: p.subtipo_categoria||p.subtipo_almacen||p.subcategoria_id||p.subcategoria||String(selectSubtipoAlmacen.value||''), tipo: tipoNorm, precio: (p.precio!=null?p.precio:(p.precio_vta!=null?p.precio_vta:'')) || inputPrecio.value||'', ingredientes: p.ingredientes||[], categoria: p.categoria||'', tipo_categoria: p.tipo_categoria||p.tipo_almacen||'', subtipo_categoria: p.subtipo_categoria||p.subtipo_almacen||'' };
	}
	function formatPrecio(v){ const n=parseFloat(v); if(isNaN(n)) return ''; return '$'+n.toFixed(2);} function escapeHtml(s){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c])); }

	function wireEvents(){ btnCrear?.addEventListener('click', abrirModal); btnCerrarModal?.addEventListener('click', cerrarModal); document.getElementById('cancelar-crear')?.addEventListener('click', cerrarModal); modal?.addEventListener('click', e=>{ if(e.target===modal) cerrarModal(); }); document.addEventListener('keydown', e=>{ if(e.key==='Escape'&&modal?.getAttribute('aria-hidden')==='false') cerrarModal(); }); selectPlan?.addEventListener('change', togglePrecio); selectTipoAlmacen?.addEventListener('change', onChangeCategoria); selectSubtipoAlmacen?.addEventListener('change', onChangeSubcategoria); selectCategoriaFiltro?.addEventListener('change', actualizarResumen); inputNombre?.addEventListener('input', actualizarResumen); selectIngredientes?.addEventListener('change', onAddIngredientesDesdeSelect); form?.addEventListener('submit', onSubmit); selectFiltroCategoria?.addEventListener('change', e=>{ state.categoriaSeleccionada = e.target.value || '__ALL__'; renderProductos(); }); planFiltrosWrap?.addEventListener('click', e=>{ const btn=e.target.closest('.plan-filter-btn'); if(!btn) return; const plan=btn.getAttribute('data-plan'); state.planFiltro=plan; state.categoriaSeleccionada='__ALL__'; planFiltrosWrap.querySelectorAll('.plan-filter-btn').forEach(b=>b.classList.toggle('activo', b===btn)); poblarSelectFiltro(); renderProductos(); }); }

	function actualizarResumen(){ if(!resumenList) return; const nombre=inputNombre?.value.trim()||'—'; const cf=selectCategoriaFiltro?.value||'—'; const tAl=selectTipoAlmacen?.selectedOptions[0]?.textContent||'—'; const sAl=selectSubtipoAlmacen?.selectedOptions[0]?.textContent||'—'; const plan=selectPlan?.value==='premium'?'Premium':'All Inclusive'; const precio=(selectPlan?.value==='premium'&&inputPrecio.value)?formatPrecio(inputPrecio.value):(selectPlan?.value==='premium'?'(sin precio)':'—'); const ingSel=obtenerIngredientesSeleccionados().map(o=>`${o.nombre}${o.unidad?` (${o.unidad})`:''}`); const ingText=ingSel.length?ingSel.join(', '):'—'; resumenList.innerHTML=[ {k:'Nombre',v:nombre},{k:'Categoría filtro',v:cf},{k:'Tipo almacén',v:tAl},{k:'Subtipo almacén',v:sAl},{k:'Plan',v:plan},{k:'Precio',v:precio},{k:'Ingredientes',v:ingText} ].map(i=>`<li><span class="key">${escapeHtml(i.k)}:</span> <span class="value">${escapeHtml(i.v)}</span></li>`).join(''); }

	async function cargarProductosInicial(){ try { const data=await api('/bar/productos-bar/'); state.productos= Array.isArray(data)? data.map(normalizarProducto):[]; if(state.productos.length){ planFiltrosWrap?.setAttribute('aria-hidden','false'); } else { planFiltrosWrap?.setAttribute('aria-hidden','true'); } } catch(e){ state.productos=[]; } }
	async function init(){ mapDom(); wireEvents(); await cargarCategorias(); await cargarProductosInicial(); poblarSelectFiltro(); renderProductos(); togglePrecio(); actualizarResumen(); }
	if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

