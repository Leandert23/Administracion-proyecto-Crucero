(function() {
    function obtenerElementoPorId(id) {
        return document.getElementById(id);
    }

    function obtenerCampoFormulario(formulario, nombre) {
        return formulario.querySelector('.form-field[data-field="' + nombre + '"]');
    }

    function obtenerElementoError(formulario, nombre) {
        const campo = obtenerCampoFormulario(formulario, nombre);
        return campo ? campo.querySelector('.error-text') : null;
    }

    function mostrarError(formulario, nombre, mensaje) {
        const elementoError = obtenerElementoError(formulario, nombre);
        if (elementoError) {
            elementoError.hidden = false;
            elementoError.textContent = mensaje;
        }
    }

    function limpiarErrores(formulario) {
        formulario.querySelectorAll('.error-text').forEach(elemento => {
            elemento.textContent = '';
            elemento.hidden = true;
        });
        
        const errorGeneral = formulario.querySelector('.form-error-general');
        if (errorGeneral) errorGeneral.remove();
    }

    function mostrarErrorGeneral(formulario, mensaje) {
        let errorGeneral = formulario.querySelector('.form-error-general');
        
        if (!errorGeneral) {
            errorGeneral = document.createElement('div');
            errorGeneral.className = 'form-error-general';
            errorGeneral.style.color = '#dc2626';
            errorGeneral.style.margin = '0 24px 8px';
            formulario.prepend(errorGeneral);
        }
        
        errorGeneral.textContent = mensaje;
    }

    function aplicarEstilosEnfoque(formulario) {
        const controles = formulario.querySelectorAll('.form-field input, .form-field select, .form-field textarea');
        
        controles.forEach(control => {
            control.addEventListener('focus', () => {
                control.closest('.form-field').classList.add('focused');
            });
            
            control.addEventListener('blur', () => {
                control.closest('.form-field').classList.remove('focused');
            });
        });
    }

    function recargarInventario() {
            try {
                // Solo refrescar si el modal de inventario está visible (evita fetch innecesario)
                if (!window.GestorModales || !GestorModales.estaAbierto || !GestorModales.estaAbierto('inventario')) return;

                // Compatibilidad: diferentes nombres posibles del gestor de inventario
                const gestor = window.GestorInventario || window.InventarioManager || window.InventoryManager;
                if (!gestor) return;

                // Detectar función de recarga disponible
                const fnPagina = gestor.cargarPagina || gestor.loadInventoryPage || gestor.loadPage;
                if (typeof fnPagina !== 'function') return;

                const paginaActual = gestor.paginaActual || gestor.currentPage || 1;
                // Pequeño delay para asegurar commit en backend antes de reflejar (evita ver lista sin nuevo item)
                setTimeout(() => {
                    try { fnPagina.call(gestor, paginaActual); } catch(e) {}
                }, 180);
            } catch (error) {}
    }

        // Refresca el historial de movimientos si el modal está abierto
        function recargarHistorial() {
            try {
                // Verificar presencia y visibilidad del modal de historial
                const modalHist = document.getElementById('modalHistorialMovimientos');
                if (!modalHist) return;
                const visible = modalHist.style.display !== 'none' && modalHist.getAttribute('aria-hidden') !== 'true';
                if (!visible) return; // Solo recargar si está abierto

                const gestor = window.GestorHistorial;
                if (!gestor || typeof gestor.cargarPagina !== 'function') return;

                const paginaActual = gestor.paginaActual || 1;
                // Pequeño delay para asegurar que el backend haya persistido el movimiento
                setTimeout(() => {
                    try { gestor.cargarPagina(paginaActual); } catch(e){}
                }, 220);
            } catch (e) {}
        }

        // Cerrar modal por clave (producto, lote, salida, merma)
        function cerrarModalClave(clave) {
            try {
                if (window.GestorModales && typeof GestorModales.cerrar === 'function') {
                    GestorModales.cerrar(clave);
                    return;
                }
                const idsFallback = {
                    producto: 'modalCrearProducto',
                    lote: 'modalCrearLote',
                    salida: 'modalCrearSalida',
                    merma: 'modalCrearMerma'
                };
                const id = idsFallback[clave];
                if (id) {
                    const modal = document.getElementById(id);
                    if (modal) {
                        modal.style.display = 'none';
                        modal.classList.remove('is-open');
                        modal.setAttribute('aria-hidden','true');
                    }
                }
            } catch(e) {}
        }

    const GestorFormularios = {
        configuraciones: {
            producto: {
                idFormulario: 'form-crear-producto',
                claveModal: 'producto',
                // Acepta ambos atributos (editandoId / editingId) para robustez
                endpoint: formulario => (formulario.dataset.editandoId || formulario.dataset.editingId) ? formulario.dataset.updateUrl : formulario.action,
                
                inicializar(contexto) {
                    aplicarEstilosEnfoque(contexto.formulario);
                    
                    this.selectSubtipo = contexto.formulario.querySelector('#id_subtipo');
                    this.selectTipo = contexto.formulario.querySelector('#id_tipo');
                    
                    this.mapeoSubtipo = {
                        COMIDA: ['CADUCABLE', 'NO_CADUCABLE', 'REFRIGERADO', 'NO_REFRIGERADO', 'BEBIDA', 'LICOR'],
                        BIENES: ['REPUESTOS', 'LIMPIEZA', 'MEDICOS', 'ACTIVOS']
                    };
                    
                    this.llenarSelectSubtipo();
                    
                    if (this.selectTipo) {
                        this.selectTipo.addEventListener('change', () => this.llenarSelectSubtipo());
                    }
                },
                
                llenarSelectSubtipo() {
                    if (!this.selectTipo || !this.selectSubtipo) return;
                    
                    const tipoSeleccionado = this.selectTipo.value;
                    this.selectSubtipo.innerHTML = '<option value="" hidden>Opcional...</option>';
                    
                    if (!tipoSeleccionado || !this.mapeoSubtipo[tipoSeleccionado]) return;
                    
                    this.mapeoSubtipo[tipoSeleccionado].forEach(subtipo => {
                        const opcion = document.createElement('option');
                        opcion.value = subtipo;
                        opcion.textContent = subtipo.replace('_', ' ');
                        this.selectSubtipo.appendChild(opcion);
                    });
                },
                
                antesDeEnviar(contexto) {
                    const idEdicion = contexto.formulario.dataset.editandoId || contexto.formulario.dataset.editingId;
                    if (idEdicion) {
                        contexto.datosFormulario.append('producto_id', idEdicion);
                    }
                },
                
                validar() {
                    return true;
                },
                
                exito(contexto, respuesta) {
                    contexto.formulario.reset();
                    this.llenarSelectSubtipo();
                    contexto.formulario.dataset.editandoId = '';
                    contexto.formulario.dataset.editingId = '';
                    
                    const campoOcultoId = obtenerElementoPorId('id_producto_edit');
                    if (campoOcultoId) campoOcultoId.value = '';
                    
                    cerrarModalClave('producto');
                    recargarInventario();
                    recargarHistorial();
                },
                
                reiniciar(contexto) {
                    contexto.formulario.reset();
                    this.llenarSelectSubtipo();
                    limpiarErrores(contexto.formulario);
                    contexto.formulario.dataset.editandoId = '';
                    contexto.formulario.dataset.editingId = '';
                }
            },
            
            lote: {
                idFormulario: 'form-crear-lote',
                claveModal: 'lote',
                endpoint: 'registrar-lote/',
                
                inicializar(contexto) {
                    aplicarEstilosEnfoque(contexto.formulario);
                },
                
                validar(contexto) {
                    if (!obtenerElementoPorId('id_producto') || !obtenerElementoPorId('id_producto').value) {
                        mostrarError(contexto.formulario, 'producto', 'Selecciona un producto de la lista');
                        return false;
                    }
                    return true;
                },
                
                exito(contexto) {
                    contexto.formulario.reset();
                    limpiarErrores(contexto.formulario);
                    cerrarModalClave('lote');
                    recargarInventario();
                    recargarHistorial();
                },
                
                reiniciar(contexto) {
                    contexto.formulario.reset();
                    
                    const campoProducto = obtenerElementoPorId('id_producto');
                    if (campoProducto) campoProducto.value = '';
                    
                    limpiarErrores(contexto.formulario);
                }
            },
            
            salida: {
                idFormulario: 'form-crear-salida',
                claveModal: 'salida',
                endpoint: 'registrar-salida/',
                
                inicializar(contexto) {
                    aplicarEstilosEnfoque(contexto.formulario);
                },
                
                validar(contexto) {
                    let esValido = true;
                    
                    const campoProducto = obtenerElementoPorId('id_producto_salida');
                    const campoCantidad = obtenerElementoPorId('id_cantidad_productos_salida');
                    const campoModulo = obtenerElementoPorId('id_modulo_entrega');
                    
                    if (!campoProducto || !campoProducto.value) {
                        mostrarError(contexto.formulario, 'producto', 'Selecciona un producto de la lista');
                        esValido = false;
                    }
                    
                    const cantidad = campoCantidad ? parseInt(campoCantidad.value, 10) : 0;
                    if (!cantidad || cantidad <= 0) {
                        mostrarError(contexto.formulario, 'cantidad_productos', 'Ingresa una cantidad válida (>0)');
                        esValido = false;
                    }
                    
                    if (!campoModulo || !campoModulo.value.trim()) {
                        mostrarError(contexto.formulario, 'modulo_entrega', 'Indica el módulo de entrega');
                        esValido = false;
                    }
                    
                    return esValido;
                },
                
                exito(contexto) {
                    contexto.formulario.reset();
                    limpiarErrores(contexto.formulario);
                    const campoProducto = obtenerElementoPorId('id_producto_salida');
                    if (campoProducto) campoProducto.value = '';
                    cerrarModalClave('salida');
                    recargarInventario();
                    recargarHistorial();
                },
                
                reiniciar(contexto) {
                    contexto.formulario.reset();
                    
                    const campoProducto = obtenerElementoPorId('id_producto_salida');
                    if (campoProducto) campoProducto.value = '';
                    
                    limpiarErrores(contexto.formulario);
                }
            },
            
            merma: {
                idFormulario: 'form-crear-merma',
                claveModal: 'merma',
                endpoint: 'registrar-merma/',
                
                inicializar(contexto) {
                    aplicarEstilosEnfoque(contexto.formulario);
                    
                    const campoOcultoProducto = obtenerElementoPorId('id_producto_merma');
                    if (campoOcultoProducto) {
                        campoOcultoProducto.addEventListener('change', () => this.cargarLotes());
                    }
                    
                    this.selectLote = obtenerElementoPorId('id_lote_merma');
                },
                
                cargarLotes() {
                    const campoOcultoProducto = obtenerElementoPorId('id_producto_merma');
                    const selectLote = this.selectLote;
                    
                    if (!campoOcultoProducto || !selectLote) return;
                    
                    const idProducto = campoOcultoProducto.value;
                    
                    if (!idProducto) {
                        selectLote.innerHTML = '<option value="">Selecciona primero un producto...</option>';
                        selectLote.disabled = true;
                        return;
                    }
                    
                    selectLote.disabled = true;
                    selectLote.innerHTML = '<option>Cargando lotes...</option>';
                    
                    fetch(`inventario/lotes-json/?producto=${encodeURIComponent(idProducto)}`)
                        .then(respuesta => respuesta.json())
                        .then(datos => {
                            if (!datos.success || !Array.isArray(datos.lotes)) throw new Error('Error en respuesta');
                            
                            const opciones = datos.lotes
                                .filter(lote => lote.disponible > 0)
                                .map(lote => {
                                    const texto = `Lote #${lote.id} - ${lote.disponible} disp`;
                                    const fechaCaducidad = lote.fecha_caducidad ? ` - vence ${lote.fecha_caducidad}` : '';
                                    return `<option value="${lote.id}" data-max="${lote.disponible}">${texto}${fechaCaducidad}</option>`;
                                });
                            
                            if (!opciones.length) {
                                selectLote.innerHTML = '<option value="">Sin lotes con stock</option>';
                                selectLote.disabled = true;
                            } else {
                                selectLote.innerHTML = '<option value="">Selecciona un lote...</option>' + opciones.join('');
                                selectLote.disabled = false;
                            }
                        })
                        .catch(() => {
                            selectLote.innerHTML = '<option value="">Error cargando lotes</option>';
                            selectLote.disabled = true;
                        });
                },
                
                validar(contexto) {
                    let esValido = true;
                    
                    const campoProducto = obtenerElementoPorId('id_producto_merma');
                    const selectLote = obtenerElementoPorId('id_lote_merma');
                    const campoCantidad = obtenerElementoPorId('id_cantidad_mermada');
                    
                    if (!campoProducto || !campoProducto.value) {
                        mostrarError(contexto.formulario, 'producto', 'Selecciona un producto');
                        esValido = false;
                    }
                    
                    if (!selectLote || !selectLote.value) {
                        mostrarError(contexto.formulario, 'lote', 'Selecciona un lote');
                        esValido = false;
                    }
                    
                    const cantidad = campoCantidad ? parseInt(campoCantidad.value, 10) : 0;
                    
                    if (!cantidad || cantidad <= 0) {
                        mostrarError(contexto.formulario, 'cantidad_mermada', 'Cantidad inválida');
                        esValido = false;
                    } else if (selectLote && selectLote.value) {
                        const opcion = selectLote.querySelector('option[value="' + selectLote.value + '"]');
                        if (opcion) {
                            const maximo = parseInt(opcion.dataset.max || '0', 10);
                            if (cantidad > maximo) {
                                mostrarError(contexto.formulario, 'cantidad_mermada', 'No debe exceder ' + maximo);
                                esValido = false;
                            }
                        }
                    }
                    
                    return esValido;
                },
                
                exito(contexto) {
                    contexto.formulario.reset();
                    
                    const selectLote = obtenerElementoPorId('id_lote_merma');
                    if (selectLote) {
                        selectLote.innerHTML = '<option value="">Selecciona primero un producto...</option>';
                        selectLote.disabled = true;
                    }
                    
                    limpiarErrores(contexto.formulario);
                    
                    cerrarModalClave('merma');
                    recargarInventario();
                    recargarHistorial();
                },
                
                reiniciar(contexto) {
                    contexto.formulario.reset();
                    
                    const selectLote = obtenerElementoPorId('id_lote_merma');
                    if (selectLote) {
                        selectLote.innerHTML = '<option value="">Selecciona primero un producto...</option>';
                        selectLote.disabled = true;
                    }
                    
                    limpiarErrores(contexto.formulario);
                }
            }
        },
        
        inicializar() {
            Object.entries(this.configuraciones).forEach(([clave, configuracion]) => {
                const formulario = obtenerElementoPorId(configuracion.idFormulario);
                
                if (!formulario || formulario.dataset.formularioVinculado) return;
                
                formulario.dataset.formularioVinculado = 'true';
                
                const contexto = {
                    formulario: formulario,
                    configuracion: configuracion
                };
                
                if (configuracion.inicializar) {
                    configuracion.inicializar(contexto);
                }
                
                formulario.addEventListener('submit', evento => {
                    evento.preventDefault();
                    limpiarErrores(formulario);
                    
                    const datosFormulario = new FormData(formulario);
                    contexto.datosFormulario = datosFormulario;
                    
                    if (configuracion.antesDeEnviar) {
                        configuracion.antesDeEnviar(contexto);
                    }
                    
                    const esValido = !configuracion.validar || configuracion.validar(contexto);
                    
                    if (esValido) {
                        // Resolución robusta del endpoint
                        let endpoint = null;
                        if (typeof configuracion.endpoint === 'function') {
                            endpoint = configuracion.endpoint(formulario);
                        } else if (typeof configuracion.endpoint === 'string') {
                            endpoint = configuracion.endpoint;
                        } else if (typeof configuracion.obtenerEndpoint === 'function') { // compatibilidad vieja
                            endpoint = configuracion.obtenerEndpoint(formulario);
                        } else if (formulario.action) {
                            endpoint = formulario.action;
                        }

                        if (!endpoint || endpoint === 'undefined') {
                            mostrarErrorGeneral(formulario, 'Endpoint no definido');
                            return;
                        }

                        // Normalizar: si es relativo sin slash inicial, preparamos relativo al path actual
                        // (opcional, puedes forzar absoluto agregando '/' si deseas)
                        fetch(endpoint, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': (formulario.querySelector('input[name="csrfmiddlewaretoken"]') || {}).value || ''
                            },
                            body: datosFormulario
                        })
                        .then(async respuesta => {
                            let datos = {}; let parseOk = false;
                            try {
                                if ((respuesta.headers.get('Content-Type') || '').includes('application/json')) {
                                    datos = await respuesta.json();
                                    parseOk = true;
                                } else {
                                    const texto = await respuesta.text();
                                    try { datos = JSON.parse(texto); parseOk = true; } catch(e) {}
                                }
                            } catch(e) {}
                            return { ok: respuesta.ok, status: respuesta.status, datos, parseOk };
                        })
                        .then(r => {
                            const d = r.datos || {};
                            const heuristicaExito = d.exitoso === true || d.success === true || typeof d.id !== 'undefined' || typeof d.pk !== 'undefined';
                            if (r.ok && heuristicaExito) {
                                if (configuracion.exito) configuracion.exito(contexto, d);
                                if (window.GestorModales) GestorModales.cerrar(configuracion.claveModal);
                                return;
                            }
                            if (r.ok && !heuristicaExito) {
                                if (configuracion.exito) configuracion.exito(contexto, d);
                                if (window.GestorModales) GestorModales.cerrar(configuracion.claveModal);
                                return;
                            }
                            if (!r.ok && !d.error && !d.errores) {
                                mostrarErrorGeneral(formulario, 'Error (' + r.status + ')');
                            }
                            this.manejarErrores(formulario, d);
                        })
                        .catch(() => mostrarErrorGeneral(formulario, 'Error de red'));
                    }
                });
                
                this.configurarCierreModal(configuracion.claveModal, () => {
                    if (configuracion.reiniciar) {
                        configuracion.reiniciar(contexto);
                    }
                });
            });
        },
        
        manejarErrores(formulario, datos) {
            if (!datos) {
                mostrarErrorGeneral(formulario, 'Error desconocido');
                return;
            }
            
            if (datos.error) {
                const mapeoErrores = {
                    producto_requerido: 'producto',
                    producto_no_encontrado: 'producto',
                    cantidad_invalida: 'cantidad_productos',
                    cantidad_no_valida: 'cantidad_productos',
                    stock_insuficiente: 'cantidad_productos',
                    operacion_invalida: 'cantidad_productos',
                    lote_requerido: 'lote',
                    lote_no_encontrado: 'lote',
                    cantidad_excede: 'cantidad_mermada'
                };
                
                const campo = mapeoErrores[datos.error];
                if (campo) {
                    mostrarError(formulario, campo, datos.mensaje || 'Error');
                } else {
                    mostrarErrorGeneral(formulario, datos.mensaje || 'Error');
                }
            }
            
            if (datos.errores) {
                Object.entries(datos.errores).forEach(([campo, mensaje]) => {
                    if (campo !== '__all__') {
                        mostrarError(formulario, campo, mensaje);
                    }
                });
            }
        },
        
        configurarCierreModal(clave, funcionReinicio) {
            if (!window.GestorModales || this.cierreConfigurado) return;
            
            const cerrarOriginal = GestorModales.cerrar ? GestorModales.cerrar.bind(GestorModales) : null;
            
            if (!cerrarOriginal) return;
            
            GestorModales.cerrar = claveModal => {
                if (claveModal === clave) {
                    try {
                        funcionReinicio();
                    } catch (error) {}
                }
                
                return cerrarOriginal(claveModal);
            };
            
            this.cierreConfigurado = true;
        }
    };

    document.addEventListener('DOMContentLoaded', () => GestorFormularios.inicializar());
    
    window.GestorFormularios = GestorFormularios;
})();