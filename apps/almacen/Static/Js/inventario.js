(function() {
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
                
                const filterType = filterButton.dataset.filter;
                if (!filterType) return;
                
                filterContainer.querySelectorAll('.filter-btn').forEach(button => {
                    button.classList.remove('active');
                });
                
                filterButton.classList.add('active');
                
                let selectedType = '';
                if (filterType === 'low') selectedType = 'COMIDA';
                else if (filterType === 'elec') selectedType = 'BIENES';
                
                const searchText = this.getSearchText();
                this.activeFilters = { busqueda: searchText };
                if (selectedType) this.activeFilters.tipo = selectedType;
                
                const filterInfo = document.getElementById('filter-active-text');
                if (filterInfo) {
                    let infoText = 'Mostrando todos los productos';
                    if (selectedType === 'COMIDA') infoText = 'Mostrando productos de Comida';
                    else if (selectedType === 'BIENES') infoText = 'Mostrando productos de Bienes';
                    filterInfo.textContent = infoText;
                }
                
                this.loadInventoryPage(1);
            });
    }
    };

    window.InventarioManager = InventarioManager;
})();