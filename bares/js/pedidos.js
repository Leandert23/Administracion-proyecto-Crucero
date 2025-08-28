let pedidos = []; // Aquí se guardan los pedidos activos

function renderPedidos() {
    const activosBody = document.getElementById('pedidos-activos-body');
    const pendientesBody = document.getElementById('historial-pedidos-pendientes');
    const completadosBody = document.getElementById('historial-pedidos-completados');
    activosBody.innerHTML = '';
    pendientesBody.innerHTML = '';
    completadosBody.innerHTML = '';

    let hayActivos = false;

    pedidos.forEach((pedido, idx) => {
        // Pedidos Activos (solo no completados)
        if (pedido.status !== 'completado') {
            hayActivos = true;
            activosBody.innerHTML += `
                <tr>
                    <td>${pedido.id}</td>
                    <td>${pedido.quien}</td>
                    <td>${pedido.producto} (${pedido.cantidad})</td>
                    <td>$${pedido.precio}</td>
                    <td>
                        <span class="estado ${pedido.status === 'pendiente' ? '' : 'preparando'}">${pedido.status.toUpperCase()}</span>
                    </td>
                    <td>BAR 1</td>
                    <td>${pedido.quien}</td>
                    <td>
                        <button type="button" class="btn detalles" onclick="verDetalles(${pedido.id})">Ver Detalles</button>
                        ${pedido.status === 'preparando' ? `<button type="button" class="btn completar" onclick="completarPedido(${pedido.id})">Completar</button>` : ''}
                        ${pedido.status === 'pendiente' ? `<button type="button" class="btn completar" onclick="prepararPedido(${pedido.id})">Preparar</button>` : ''}
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
                    <td>${pedido.producto} (${pedido.cantidad})</td>
                    <td>$${pedido.precio}</td>
                    <td>
                        <span class="estado ${pedido.status === 'pendiente' ? '' : 'preparando'}">${pedido.status.toUpperCase()}</span>
                    </td>
                    <td>BAR 1</td>
                    <td>${pedido.quien}</td>
                    <td>
                        <button type="button" class="btn detalles" onclick="verDetalles(${pedido.id})">Ver Detalles</button>
                        <button type="button" class="btn eliminar" onclick="eliminarPedido(${pedido.id})">Eliminar</button>
                        <button type="button" class="btn completar" onclick="modificarPedido(${pedido.id})">Modificar</button>
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
                    <td>${pedido.producto} (${pedido.cantidad})</td>
                    <td>$${pedido.precio}</td>
                    <td>
                        <span class="estado completado">${pedido.status.toUpperCase()}</span>
                    </td>
                    <td>BAR 1</td>
                    <td>${pedido.quien}</td>
                    <td>
                        <button type="button" class="btn detalles" onclick="verDetalles(${pedido.id})">Ver Detalles</button>
                    </td>
                </tr>
            `;
        }
    });

    // Si no hay pedidos activos, mostrar mensaje
    if (!hayActivos) {
        activosBody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center; color:#64748b; font-size:1.1rem; padding:32px;">
                    No hay ordenes activas
                </td>
            </tr>
        `;
    }
}

// Modal lógica para crear pedido
document.addEventListener('DOMContentLoaded', function() {
    const crearBtn = document.getElementById('crear-pedido-btn');
    const modal = document.getElementById('modal-crear-pedido');
    const closeModal = document.getElementById('close-modal');
    const form = document.getElementById('form-crear-pedido');

    crearBtn.addEventListener('click', function() {
        modal.style.display = 'flex';
    });

    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const producto = form.producto.value;
        const cantidad = form.cantidad.value;
        const quien = form.quien.value;
        const precio = form.precio.value;

        const nuevoPedido = {
            id: Date.now(),
            producto,
            cantidad,
            quien,
            precio,
            status: 'pendiente'
        };
        pedidos.push(nuevoPedido);
        renderPedidos();
        modal.style.display = 'none';
        form.reset();
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    renderPedidos();
});

// Modal para ver detalles tipo factura (igual para ordenes y pedidos)
window.verDetalles = function(id) {
    const pedido = pedidos.find(p => p.id === id);
    if (!pedido) return;
    const modal = document.getElementById('modal-detalle-pedido');
    const content = document.getElementById('detalle-pedido-content');
    content.innerHTML = `
        <span class="close-modal" id="close-modal-detalle">&times;</span>
        <div class="factura-header">
            <h2>Detalle del Pedido</h2>
            <p>ID: ${pedido.id}</p>
        </div>
        <table class="factura-table">
            <tr><td><strong>Producto:</strong></td><td>${pedido.producto}</td></tr>
            <tr><td><strong>Cantidad:</strong></td><td>${pedido.cantidad}</td></tr>
            <tr><td><strong>Cliente:</strong></td><td>${pedido.quien}</td></tr>
            <tr><td><strong>Bar:</strong></td><td>BAR 1</td></tr>
            <tr><td><strong>Estado:</strong></td><td>${pedido.status.toUpperCase()}</td></tr>
        </table>
        <div class="factura-total">Total: $${pedido.precio}</div>
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

// Cambiar status a "completado" (solo desde activos)
window.completarPedido = function(id) {
    const pedido = pedidos.find(p => p.id === id);
    if (!pedido) return;
    pedido.status = 'completado';
    renderPedidos();
};