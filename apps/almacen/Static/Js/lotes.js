(function() {
    const modal = document.getElementById('modalLotesProducto');
    if (!modal) return;

    const contenidoModal = modal.querySelector('#lotes-contenido');
    let controladorPeticion = null;

    const mostrarModal = () => {
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
    };

    const ocultarModal = () => {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        if (contenidoModal) contenidoModal.innerHTML = '';
    };

    const establecerContenido = html => {
        if (contenidoModal) contenidoModal.innerHTML = html;
    };

    const mostrarCargando = () => {
        establecerContenido('<div class="cargando-lotes">Cargando...</div>');
    };

    const mostrarError = mensaje => {
        establecerContenido(`<div class="error-lotes">${mensaje}</div>`);
    };

    const construirUrl = idProducto => {
        const parametros = new URLSearchParams({ producto: idProducto });
        return `inventario/lotes/?${parametros.toString()}`;
    };

    const obtenerLotes = idProducto => {
        if (!idProducto) return Promise.resolve();

        if (controladorPeticion) {
            controladorPeticion.abort();
        }

        controladorPeticion = new AbortController();
        mostrarCargando();

        return fetch(construirUrl(idProducto), {
            signal: controladorPeticion.signal,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(respuesta => {
            if (!respuesta.ok) throw new Error('respuesta_fallida');
            return respuesta.json();
        })
        .then(datos => {
            if (datos && datos.success) {
                establecerContenido(datos.html);
            } else {
                mostrarError('No se pudieron cargar los lotes');
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') return;
            mostrarError('Error de conexión');
        });
    };

    const manejarClicDocumento = evento => {
        if (evento.target.matches('[data-close="true"]')) {
            ocultarModal();
            return;
        }

        const botonLotes = evento.target.closest('[data-ver-lotes]');
        if (!botonLotes) return;

        const idProducto = botonLotes.getAttribute('data-ver-lotes');
        if (!idProducto) return;

        mostrarModal();
        obtenerLotes(idProducto);
    };

    document.addEventListener('click', manejarClicDocumento);

    window.GestorLotes = {
        abrir: idProducto => {
            mostrarModal();
            if (idProducto) obtenerLotes(idProducto);
        },
        cerrar: ocultarModal,
        cargar: obtenerLotes
    };
})();