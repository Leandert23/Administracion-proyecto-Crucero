document.addEventListener('DOMContentLoaded', function(){
    const btnRefresh = document.getElementById('btn-refresh');
    const searchInput = document.getElementById('search-admins');
    const openCreate = document.getElementById('open-create');
    const createPanel = document.getElementById('create-panel');
    const cancelCreate = document.getElementById('cancel-create');
    const createForm = document.getElementById('create-superuser-form');

    function fetchList(q){
        const url = new URL(window.location.href);
        if(q) url.searchParams.set('q', q);
        fetch(url.pathname + url.search, {headers:{'X-Requested-With':'XMLHttpRequest'}})
            .then(r => r.json())
            .then(data => {
                if(data.ok && data.html){
                    try{
                        // Parse returned HTML safely
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(data.html, 'text/html');

                        // Extract tbody from response
                        const newTbody = doc.querySelector('#um-users-tbody');
                        if(newTbody){
                            const currTbody = document.querySelector('#um-users-tbody');
                            if(currTbody) currTbody.innerHTML = newTbody.innerHTML;
                        }

                        // Extract pagination from response (nav.um-pagination or .pagination-container)
                        const newPagination = doc.querySelector('.um-pagination') || doc.querySelector('.pagination-container');
                        const currPagination = document.querySelector('.um-pagination') || document.querySelector('.pagination-container');
                        if(newPagination && currPagination){
                            currPagination.innerHTML = newPagination.innerHTML;
                        }

                        // If the response contains other areas (like totals), update them as needed
                        const newTotalsScript = doc.querySelector('script');
                        // (we already have a small inline script that updates totals when partial is loaded)
                        return;
                    }catch(e){
                        console.error('Error parsing partial HTML', e);
                        // fallback: brute replace
                        const tableContainer = document.querySelector('.table-container');
                        if(tableContainer) tableContainer.innerHTML = data.html;
                    }
                }
            }).catch(console.error);
    }

    const searchInputFallback = document.getElementById('users-search');
    if(btnRefresh) btnRefresh.addEventListener('click', function(){ fetchList((searchInput && searchInput.value) || (searchInputFallback && searchInputFallback.value) || ''); });
    if(searchInput) searchInput.addEventListener('keyup', function(e){ if(e.key==='Enter') fetchList(this.value); });
    if(searchInputFallback) {
        // Debounce helper
        function debounce(fn, wait){
            let t;
            return function(){
                const args = arguments;
                clearTimeout(t);
                t = setTimeout(function(){ fn.apply(null, args); }, wait);
            };
        }

        // Trigger search on Enter
        searchInputFallback.addEventListener('keyup', function(e){ if(e.key === 'Enter') fetchList(this.value); });

        // Live search (debounced)
        const doSearch = debounce(function(){ fetchList(searchInputFallback.value); }, 350);
        searchInputFallback.addEventListener('input', doSearch);
    }
    if(openCreate) openCreate.addEventListener('click', function(){ createPanel.style.display='block'; });
    if(cancelCreate) cancelCreate.addEventListener('click', function(){ createPanel.style.display='none'; });

    if(createForm) createForm.addEventListener('submit', function(e){
        e.preventDefault();
        const fd = new FormData(createForm);
        // Validar que no exista un usuario con el mismo username en la tabla actual
        const usernameInput = createForm.querySelector('[name="username"]');
        if(usernameInput) {
            const username = usernameInput.value.trim().toLowerCase();
            // Buscar en la tabla actual (tbody) si existe ese username
            const rows = document.querySelectorAll('#um-users-tbody tr');
            for(const row of rows) {
                const userCell = row.querySelector('.username');
                if(userCell && userCell.textContent.trim().toLowerCase() === username) {
                    alert('Ya existe un usuario con ese nombre de usuario.');
                    return;
                }
            }
        }
        // mark as superuser and no crucero
        fd.append('is_superuser', '1');
        fd.append('crucero', '');
        // obtain CSRF token from cookie
        function getCookie(name){
            const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
            return v ? v.pop() : '';
        }
        const csrftoken = getCookie('csrftoken');

        fetch('/usuarios/admin/superusers/create/', { method: 'POST', body: fd, headers: {'X-Requested-With':'XMLHttpRequest', 'X-CSRFToken': csrftoken}, credentials: 'same-origin' })
            .then(r => r.json())
            .then(data => {
                if(data.ok){
                    alert('Superusuario creado: ' + data.username);
                    createForm.reset();
                    createPanel.style.display='none';
                    fetchList();
                } else {
                    alert('Error: ' + (data.error || 'unknown'));
                }
            }).catch(err => { console.error(err); alert('Error al crear usuario'); });
    });

    // helper to read csrftoken (same logic used elsewhere)
    function getCookie(name){
        const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    // Delegate clicks for action buttons inside the users list (deactivate/activate/edit)
    document.addEventListener('click', function(e){
        const target = e.target.closest && e.target.closest('[data-action]');
        if(!target) return;
        const action = target.getAttribute('data-action');
        const userId = target.getAttribute('data-user-id');
        if(!action || !userId) return;

        // Edit user
        if(action === 'edit'){
            // Buscar la fila del usuario y extraer los datos
            const row = target.closest('tr');
            if(!row) return;
            const username = row.querySelector('.username') ? row.querySelector('.username').textContent.trim() : '';
            const nombre = row.querySelector('.user-details .username') ? row.querySelector('.user-details .username').textContent.trim() : '';
            const rolNombre = row.querySelector('.role-badge') ? row.querySelector('.role-badge').textContent.trim() : '';
            // Abrir el modal y rellenar los datos
            if(typeof openEditUser_prefill === 'function'){
                openEditUser_prefill({
                    id: userId,
                    username: username,
                    rol_nombre: rolNombre
                });
            } else {
                alert('No se pudo abrir el modal de edición.');
            }
            return;
        }

        // Deactivate user
        if(action === 'deactivate'){
            if(!confirm('¿Seguro que desea desactivar este usuario?')) return;
            const csrftoken = getCookie('csrftoken');
            fetch(`/usuarios/${userId}/deactivate/`, { method: 'POST', headers: {'X-Requested-With':'XMLHttpRequest', 'X-CSRFToken': csrftoken}, credentials: 'same-origin' })
                .then(r => r.json())
                .then(data => {
                    if(data.ok){
                        // refresh the list
                        fetchList();
                    } else {
                        alert('Error al desactivar: ' + (data.error || 'unknown'));
                    }
                }).catch(err => { console.error(err); alert('Error al desactivar usuario'); });
        }

        // Activate user
        if(action === 'activate'){
            if(!confirm('¿Seguro que desea activar este usuario?')) return;
            const csrftoken = getCookie('csrftoken');
            fetch(`/usuarios/${userId}/activate/`, { method: 'POST', headers: {'X-Requested-With':'XMLHttpRequest', 'X-CSRFToken': csrftoken}, credentials: 'same-origin' })
                .then(r => r.json())
                .then(data => {
                    if(data.ok){
                        fetchList();
                    } else {
                        alert('Error al activar: ' + (data.error || 'unknown'));
                    }
                }).catch(err => { console.error(err); alert('Error al activar usuario'); });
        }
    });

    // Listen for the custom event dispatched by the simple modal after a user is created
    document.addEventListener('userCreated', function(e){
        console.log('userCreated event received, refreshing list');
        fetchList();
    });
});
