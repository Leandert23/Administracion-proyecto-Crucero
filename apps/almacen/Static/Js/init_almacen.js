(function(){
    function iniciarAplicacion(){
        if(window.GestorModales && typeof GestorModales.inicializar === 'function') GestorModales.inicializar();
        if(window.ProductFormManager && typeof ProductFormManager.init === 'function') ProductFormManager.init();
        if(window.InventarioManager){
            if(typeof InventarioManager.initializeLiveSearch === 'function') InventarioManager.initializeLiveSearch();
            if(typeof InventarioManager.initializeTypeFilters === 'function') InventarioManager.initializeTypeFilters();
        }
        if(window.LotFormManager && typeof LotFormManager.init === 'function') LotFormManager.init();
        // Alias globales para la paginación usados por el partial de botones
        window.cargarPaginaInventario = p => window.InventarioManager && InventarioManager.loadInventoryPage(p);
        // Función única que decide según contexto (historial abierto => paginar historial, si no inventario)
        window.cargarPagina = function(p){
            const modalHistorial = document.getElementById('modalHistorialMovimientos');
            const historialVisible = modalHistorial && modalHistorial.style.display === 'flex';
            if(historialVisible && window.GestorHistorial && typeof GestorHistorial.cargarPagina === 'function'){
                GestorHistorial.cargarPagina(p);
                return;
            }
            if(window.InventarioManager && typeof InventarioManager.loadInventoryPage === 'function'){
                InventarioManager.loadInventoryPage(p);
            }
        };
        cargarOrdenesCompra(1);
    vincularBotonesRevisar();
    }
    function cargarOrdenesCompra(pagina){
        const contenedor = document.getElementById('tabla-ordenes-compra-wrapper');
        if(!contenedor) return;
        contenedor.innerHTML = '<div class="cargando-historial" style="padding:24px; text-align:center; font-size:.85rem; color:#475569;">Cargando órdenes...</div>';
        const params = new URLSearchParams();
        if(pagina) params.append('page', pagina);
        const url = 'ordenes-compra/por-registrar/' + (params.toString() ? ('?'+params.toString()) : '');
        fetch(url, {headers:{'X-Requested-With':'XMLHttpRequest'}})
            .then(r=>r.json())
            .then(d=>{
                if(d.success){
                    contenedor.innerHTML = d.tabla_html;
                    const footer = contenedor.querySelector('#ordenes-footer');
                    if(footer && d.paginacion_html){ footer.innerHTML = d.paginacion_html; }
                    vincularBotonesRevisar();
                } else {
                    contenedor.innerHTML = '<div style="padding:16px; font-size:.85rem; color:#b91c1c;">Error al cargar órdenes</div>';
                }
            })
            .catch(()=>{
                contenedor.innerHTML = '<div style="padding:16px; font-size:.85rem; color:#b91c1c;">Error de red</div>';
            });
    }
    function vincularBotonesRevisar(){
        document.querySelectorAll('.btn-revisar[data-orden-id]').forEach(btn=>{
            if(btn.dataset.vinculado) return; btn.dataset.vinculado='1';
            btn.addEventListener('click', ()=>{
                const id = btn.getAttribute('data-orden-id');
                if(!id) return;
                fetch('ordenes-compra/detalle/'+id+'/', {headers:{'X-Requested-With':'XMLHttpRequest'}})
                    .then(r=>r.ok?r.json():Promise.reject())
                    .then(d=>{
                        if(!d.success) return;
                        // Prefill form
                        const inputHiddenProducto = document.getElementById('id_producto');
                        const inputSearch = document.getElementById('buscar_producto_lote');
                        const hiddenOrden = document.getElementById('id_orden_compra_id');
                        const campoCantidad = document.getElementById('id_cantidad_productos');
                        const campoPrecio = document.getElementById('id_precio_lote');
                        if(inputHiddenProducto) inputHiddenProducto.value = d.producto.id;
                        if(inputSearch) inputSearch.value = d.producto.nombre;
                        if(hiddenOrden) hiddenOrden.value = d.orden.id;
                        if(campoPrecio) campoPrecio.value = d.orden.precio_lote;
                        if(campoCantidad) campoCantidad.placeholder = 'Esperado: '+ d.orden.cantidad_productos;
                        if(window.GestorModales && typeof GestorModales.abrir==='function'){ GestorModales.abrir('lote'); }
                    })
                    .catch(()=>{});
            });
        });
    }
    // Exponer función global para paginación de órdenes
    window.cargarPaginaOrdenes = function(p){ cargarOrdenesCompra(p); };
    document.addEventListener('DOMContentLoaded', iniciarAplicacion);
})();
