// Importa productos desde el módulo de menú
// Si usas módulos ES6, deberías importar productos desde productos.js
// Aquí se asume que 'productos' está en window (por ejemplo, window.productos = productos; al final de productos.js)

let pedidos = []; // Aquí se guardan los pedidos activos

// Cambia los botones de acciones en pedidos a circulares
function renderPedidos() {
    const activosBody = document.getElementById('pedidos-activos-body');
    const pendientesBody = document.getElementById('historial-pedidos-pendientes');
    const completadosBody = document.getElementById('historial-pedidos-completados');
    activosBody.innerHTML = '';
    pendientesBody.innerHTML = '';
    completadosBody.innerHTML = '';

    let hayActivos = false;

    // Encabezados coherentes
    activosBody.parentElement.querySelector('thead').innerHTML = `
        <tr>
            <th>ID</th>
            <th>Cliente</th>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Estado</th>
            <th>Bar</th>
            <th>Acciones</th>
        </tr>
    `;
    pendientesBody.parentElement.querySelector('thead').innerHTML = `
        <tr>
            <th>ID</th>
            <th>Cliente</th>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Estado</th>
            <th>Bar</th>
            <th>Acciones</th>
        </tr>
    `;
    completadosBody.parentElement.querySelector('thead').innerHTML = `
        <tr>
            <th>ID</th>
            <th>Cliente</th>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Estado</th>
            <th>Bar</th>
            <th>Acciones</th>
        </tr>
    `;

    pedidos.forEach((pedido, idx) => {
        // Pedidos Activos (solo no completados)
        if (pedido.status !== 'completado') {
            hayActivos = true;
            activosBody.innerHTML += `
                <tr>
                    <td>${pedido.id}</td>
                    <td>${pedido.quien}</td>
                    <td>${pedido.producto}</td>
                    <td>${pedido.cantidad}</td>
                    <td>
                        <span class="estado ${pedido.status === 'pendiente' ? '' : 'preparando'}">${pedido.status.toUpperCase()}</span>
                    </td>
                    <td>BAR 1</td>
                    <td>
                        <button type="button" class="btn detalles" onclick="verDetalles(${pedido.id})">Ver Detalles</button>
                        ${pedido.status === 'preparando' ? `<button type="button" class="btn completar" onclick="completarPedido(${pedido.id})">Completar</button>` : ''}
                        ${pedido.status === 'pendiente' ? `<button type="button" class="btn completar" onclick="prepararPedido(${pedido.id})">Comenzar</button>` : ''}
                        ${pedido.status !== 'completado' ? `<button type="button" class="btn eliminar" onclick="eliminarPedido(${pedido.id})">Eliminar</button>` : ''}
                    </td>
                </tr>
            `;
        }
        // Historial de pedidos pendientes
        if (pedido.status !== 'completado') {
            pendientesBody.innerHTML += `
                <tr>
                    <td>${pedido.id}</td>
                    <td>${pedido.quien}</td>
                    <td>${pedido.producto}</td>
                    <td>${pedido.cantidad}</td>
                    <td>
                        <span class="estado ${pedido.status === 'pendiente' ? '' : 'preparando'}">${pedido.status.toUpperCase()}</span>
                    </td>
                    <td>BAR 1</td>
                    <td>
                        <div style="display:flex; gap:8px; justify-content:center;">
                            <button class="btn detalles" title="Ver Detalles" onclick="verDetalles(${pedido.id})">
                                Ver Detalles
                            </button>
                            <button class="menu-btn-circle menu-btn-x" title="Eliminar" onclick="eliminarPedido(${pedido.id})"><span>X</span></button>
                            <button class="menu-btn-circle menu-btn-hammer" title="Modificar" onclick="modificarPedido(${pedido.id})"><span>🔨</span></button>
                        </div>
                    </td>
                </tr>
            `;
        }
        // Historial de pedidos completados
        if (pedido.status === 'completado') {
            completadosBody.innerHTML += `
                <tr>
                    <td>${pedido.id}</td>
                    <td>${pedido.quien}</td>
                    <td>${pedido.producto}</td>
                    <td>${pedido.cantidad}</td>
                    <td>
                        <span class="estado completado">${pedido.status.toUpperCase()}</span>
                    </td>
                    <td>BAR 1</td>
                    <td>
                        <div style="display:flex; gap:8px; justify-content:center;">
                            <button class="btn detalles" title="Ver Detalles" onclick="verDetalles(${pedido.id})">
                                Ver Detalles
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }
    });

    // Si no hay pedidos activos, mostrar mensaje
    if (!hayActivos) {
        activosBody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align:center; color:#64748b; font-size:1.1rem; padding:32px;">
                    No hay ordenes activas
                </td>
            </tr>
        `;
    }
}

function calcularCantidad(producto) {
    // Esta función debe estar igual que en productos.js
    let min = Infinity;
    producto.ingredientes.forEach(ing => {
        const match = ing.cantidad.match(/(\d+)\s*ml/);
        if (match && typeof ing.stock === 'number') {
            const porProducto = parseInt(match[1]);
            const cantidad = Math.floor(ing.stock / porProducto);
            if (cantidad < min) min = cantidad;
        }
    });
    return isFinite(min) ? min : "N/A";
}

// Modal lógica para crear pedido
document.addEventListener('DOMContentLoaded', function() {
    const crearBtn = document.getElementById('crear-pedido-btn');
    const modal = document.getElementById('modal-crear-pedido');
    const closeModal = document.getElementById('close-modal');
    const form = document.getElementById('form-crear-pedido');
    const productoSelect = document.createElement('select');
    productoSelect.id = "producto";
    productoSelect.name = "producto";
    productoSelect.required = true;

    // Genera las opciones del menú
    function actualizarOpcionesProducto() {
        productoSelect.innerHTML = '';
        if (window.productos && window.productos.length > 0) {
            window.productos.forEach(prod => {
                const cantidadDisponible = calcularCantidad(prod);
                const disabled = cantidadDisponible === 0 || cantidadDisponible === "N/A" ? "disabled" : "";
                const premium = prod.tipo === 'pago' ? '⭐ ' : '';
                const precio = prod.tipo === 'pago' ? ` - $${prod.precio}` : '';
                productoSelect.innerHTML += `<option value="${prod.nombre}" ${disabled}>
                    ${premium}${prod.nombre} ${!disabled ? `(Disponible: ${cantidadDisponible}${precio})` : '(Sin disponibilidad)'}
                </option>`;
            });
        } else {
            productoSelect.innerHTML = '<option disabled>No hay productos disponibles</option>';
        }
    }

    // Reemplaza el input por el select en el formulario
    form.querySelector('input[name="producto"]').replaceWith(productoSelect);

    // Agrega campo para tipo de pedido
    let tipoPedidoGroup = document.createElement('div');
    tipoPedidoGroup.className = "form-group";
    tipoPedidoGroup.innerHTML = `
        <label for="tipo-pedido">¿Dónde se entrega?</label>
        <select id="tipo-pedido" name="tipo-pedido" required>
            <option value="local">En el lugar</option>
            <option value="cuarto">Para llevar al cuarto</option>
        </select>
    `;
    form.querySelector('input[name="quien"]').parentNode.after(tipoPedidoGroup);

    const precioInput = form.querySelector('input[name="precio"]');
    if (precioInput && precioInput.parentNode) {
        precioInput.parentNode.remove();
    }

    crearBtn.addEventListener('click', function() {
        actualizarOpcionesProducto();
        modal.style.display = 'flex';
    });

    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const productoNombre = form.producto.value;
        const cantidad = parseInt(form.cantidad.value);
        const quien = form.quien.value;
        const tipoPedido = form['tipo-pedido'].value;

        // Busca el producto en el menú
        const productoObj = window.productos.find(p => p.nombre === productoNombre);
        const cantidadDisponible = calcularCantidad(productoObj);

        // Validación visual en vez de alert
        const cantidadInput = form.querySelector('input[name="cantidad"]');
        const cantidadGroup = cantidadInput.parentNode;
        // Limpia estilos previos
        cantidadInput.style.border = '';
        cantidadGroup.querySelector('.error-stock')?.remove();

        if (!productoObj || cantidad > cantidadDisponible) {
            cantidadInput.style.border = '2px solid #ef4444';
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-stock';
            errorMsg.style.color = '#ef4444';
            errorMsg.style.fontSize = '13px';
            errorMsg.style.marginTop = '6px';
            errorMsg.textContent = 'No hay suficiente stock para este producto.';
            cantidadGroup.appendChild(errorMsg);
            return;
        }

        // NO RESTAR STOCK AQUÍ, SOLO AL COMPLETAR EL PEDIDO (cuando integres Django, elimina cualquier lógica de stock aquí y hazlo en backend)

        const nuevoPedido = {
            id: Date.now(),
            producto: productoNombre,
            cantidad,
            quien,
            tipoPedido,
            status: 'pendiente',
            precio: productoObj.precio || 0,
            tipo: productoObj.tipo
        };
        pedidos.push(nuevoPedido);
        renderPedidos();
        modal.style.display = 'none';
        form.reset();
        cantidadInput.style.border = '';
        cantidadGroup.querySelector('.error-stock')?.remove();
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    renderPedidos();
});

// Cambiar status a "completado" (solo desde activos)
window.completarPedido = function(id) {
    const pedido = pedidos.find(p => p.id === id);
    if (!pedido) return;
    pedido.status = 'completado';

    // Descontar stock solo al completar el pedido
    const productoObj = window.productos.find(p => p.nombre === pedido.producto);
    if (productoObj) {
        productoObj.ingredientes.forEach(ing => {
            const match = ing.cantidad.match(/(\d+)\s*ml/);
            if (match && typeof ing.stock === 'number') {
                const porProducto = parseInt(match[1]);
                ing.stock -= porProducto * pedido.cantidad;
            }
        });
    }

    renderPedidos();
};

// Modal para ver detalles tipo factura (igual para ordenes y pedidos)
window.verDetalles = function(id) {
    const pedido = pedidos.find(p => p.id === id);
    if (!pedido) return;
    const productoObj = window.productos.find(p => p.nombre === pedido.producto);
    const premium = productoObj && productoObj.tipo === 'pago' ? '⭐ ' : '';
    const precio = productoObj && productoObj.tipo === 'pago' ? `$${productoObj.precio}` : 'Incluido';
    const modal = document.getElementById('modal-detalle-pedido');
    const content = document.getElementById('detalle-pedido-content');
    content.innerHTML = `
        <span class="close-modal" id="close-modal-detalle">&times;</span>
        <div class="factura-header">
            <h2>Detalle del Pedido</h2>
            <p>ID: ${pedido.id}</p>
        </div>
        <table class="factura-table">
            <tr><td><strong>Producto:</strong></td><td>${premium}${pedido.producto}</td></tr>
            <tr><td><strong>Cantidad:</strong></td><td>${pedido.cantidad}</td></tr>
            <tr><td><strong>Cliente:</strong></td><td>${pedido.quien}</td></tr>
            <tr><td><strong>Bar:</strong></td><td>BAR 1</td></tr>
            <tr><td><strong>Estado:</strong></td><td>${pedido.status.toUpperCase()}</td></tr>
            <tr><td><strong>Precio:</strong></td><td>${precio}</td></tr>
            <tr><td><strong>Entrega:</strong></td><td>${pedido.tipoPedido === 'cuarto' ? 'Para llevar al cuarto' : 'En el lugar'}</td></tr>
        </table>
    `;
    modal.style.display = 'flex';

    document.getElementById('close-modal-detalle').onclick = function() {
        modal.style.display = 'none';
    };
    modal.onclick = function(e) {
        if (e.target === modal) modal.style.display = 'none';
    };
};

// Modificar pedido (solo ejemplo, puedes expandirlo)
window.modificarPedido = function(id) {
    const pedido = pedidos.find(p => p.id === id);
    if (!pedido) return;
    alert('Funcionalidad de modificar pedido pendiente de implementar.');
};

// Eliminar pedido (solo si no está completado)
window.eliminarPedido = function(id) {
    pedidos = pedidos.filter(p => p.id !== id);
    renderPedidos();
};

// Cambiar status a "preparando" (solo desde activos)
window.prepararPedido = function(id) {
    const pedido = pedidos.find(p => p.id === id);
    if (!pedido) return;
    pedido.status = 'preparando';
    renderPedidos();
};