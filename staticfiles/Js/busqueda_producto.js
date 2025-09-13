(function() {
    if (window.BuscadorProductoInicializado) return;
    window.BuscadorProductoInicializado = true;

    const SELECTOR_WRAPPER = '.js-buscador-producto';

    function obtenerCruceroId() {
        const raiz = document.getElementById('almacen-root');
        return raiz ? raiz.dataset.cruceroId || '' : '';
    }

    function buscarProductos(urlBase, termino, signal) {
        const parametros = new URLSearchParams();
        const cruceroId = obtenerCruceroId();
        
        if (cruceroId) parametros.append('crucero_id', cruceroId);
        if (termino) parametros.append('busqueda', termino);
        
        const url = `${urlBase}?${parametros.toString()}`;
        
        return fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            signal: signal
        }).then(respuesta => respuesta.json());
    }

    function inicializarBuscador(contenedor) {
        const entrada = contenedor.querySelector('.buscador-producto-input');
        const campoOcultoId = document.getElementById(contenedor.dataset.hiddenId);
        const listaResultados = document.getElementById(contenedor.dataset.listaId);
        const urlBusqueda = contenedor.dataset.url;
        const longitudMinima = parseInt(contenedor.dataset.minLength || '2', 10);

        let controladorAbortar = null;
        let tiempoEspera = null;

        function limpiarResultados(mensaje) {
            if (!listaResultados) return;
            
            if (mensaje) {
                listaResultados.innerHTML = `<div class="lista-resultados vacio">${mensaje}</div>`;
                listaResultados.classList.add('visible');
            } else {
                listaResultados.classList.remove('visible');
                listaResultados.innerHTML = '';
            }
        }

        function mostrarResultadosHTML(html) {
            if (!listaResultados) return;
            
            if (!html) {
                limpiarResultados('Sin resultados');
                return;
            }
            
            listaResultados.innerHTML = html;
            listaResultados.classList.add('visible');
            activarElementosLista();
        }

        function activarElementosLista() {
            listaResultados.querySelectorAll('.item-resultado').forEach(elemento => {
                elemento.addEventListener('mouseenter', () => resaltarElemento(elemento));
                elemento.addEventListener('mousedown', evento => {
                    evento.preventDefault();
                    seleccionarElemento(elemento);
                });
            });
        }

        function resaltarElemento(elemento) {
            listaResultados.querySelectorAll('.item-resultado').forEach(item => {
                item.classList.remove('activo');
            });
            
            elemento.classList.add('activo');
            elemento.scrollIntoView({ block: 'nearest' });
        }

        function seleccionarElemento(elemento) {
            const id = elemento.getAttribute('data-id');
            const elementoTexto = elemento.querySelector('strong');
            const texto = elementoTexto ? elementoTexto.textContent.trim() : elemento.textContent.trim();
            
            if (campoOcultoId) {
                campoOcultoId.value = id;
                try { campoOcultoId.dispatchEvent(new Event('change', { bubbles: true })); } catch(e) { /* fallback */ }
            }
            if (entrada) entrada.value = texto;
            
            limpiarResultados();
        }

        function manejarTeclado(evento) {
            if (!listaResultados.classList.contains('visible')) return;
            
            const elementos = Array.from(listaResultados.querySelectorAll('.item-resultado'));
            if (!elementos.length) return;
            
            const indiceActual = elementos.findIndex(item => item.classList.contains('activo'));
            
            switch(evento.key) {
                case 'ArrowDown':
                    evento.preventDefault();
                    const siguiente = indiceActual < elementos.length - 1 ? indiceActual + 1 : 0;
                    resaltarElemento(elementos[siguiente]);
                    break;
                    
                case 'ArrowUp':
                    evento.preventDefault();
                    const anterior = indiceActual > 0 ? indiceActual - 1 : elementos.length - 1;
                    resaltarElemento(elementos[anterior]);
                    break;
                    
                case 'Enter':
                    if (indiceActual >= 0) {
                        evento.preventDefault();
                        seleccionarElemento(elementos[indiceActual]);
                    }
                    break;
                    
                case 'Escape':
                    limpiarResultados();
                    break;
            }
        }

        function ejecutarBusqueda(termino) {
            if (controladorAbortar) controladorAbortar.abort();
            
            controladorAbortar = new AbortController();
            
            limpiarResultados('Buscando...');
            
            buscarProductos(urlBusqueda, termino, controladorAbortar.signal)
                .then(datos => {
                    if (!datos || !datos.success) {
                        limpiarResultados('Sin resultados');
                        return;
                    }
                    
                    const html = (datos.lista_html || '').trim();
                    mostrarResultadosHTML(html);
                })
                .catch(error => {
                    if (error.name !== 'AbortError') {
                        limpiarResultados('Error');
                    }
                });
        }

        function manejarEntrada() {
            const valor = entrada.value.trim();
            
            if (tiempoEspera) clearTimeout(tiempoEspera);
            
            if (!valor) {
                if (campoOcultoId) campoOcultoId.value = '';
                limpiarResultados();
                return;
            }
            
            if (valor.length < longitudMinima) {
                const letrasFaltantes = longitudMinima - valor.length;
                limpiarResultados(`Escribe ${letrasFaltantes} letra(s) más`);
                return;
            }
            
            tiempoEspera = setTimeout(() => ejecutarBusqueda(valor), 280);
        }

        entrada.addEventListener('input', manejarEntrada);
        entrada.addEventListener('keydown', manejarTeclado);
        
        document.addEventListener('click', evento => {
            if (!listaResultados.contains(evento.target) && evento.target !== entrada) {
                limpiarResultados();
            }
        }, true);
    }

    function inicializarTodos() {
        document.querySelectorAll(SELECTOR_WRAPPER).forEach(inicializarBuscador);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarTodos);
    } else {
        inicializarTodos();
    }
})();