(function(){
    function iniciarAplicacion(){
        if(window.GestorModales && typeof GestorModales.init === 'function') GestorModales.init();
        if(window.ProductFormManager && typeof ProductFormManager.init === 'function') ProductFormManager.init();
        if(window.InventarioManager){
            if(typeof InventarioManager.initializeLiveSearch === 'function') InventarioManager.initializeLiveSearch();
            if(typeof InventarioManager.initializeTypeFilters === 'function') InventarioManager.initializeTypeFilters();
        }
        if(window.LotFormManager && typeof LotFormManager.init === 'function') LotFormManager.init();
        window.cargarPaginaInventario = p => window.InventarioManager && InventarioManager.loadInventoryPage(p);
    }
    document.addEventListener('DOMContentLoaded', iniciarAplicacion);
})();
