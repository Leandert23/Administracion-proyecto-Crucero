let categorias = [
    "Cafeterías",
    "Comida",
    "Postres y Dulces",
    "Bebidas y Cocteles"
];

let productos = [
    // Ejemplo gratis
    {
        id: 1,
        nombre: "Mojito",
        tipo: "gratis",
        categoria: "Bebidas y Cocteles",
        ingredientes: [
            { nombre: "Ron blanco", cantidad: "60 ml", stock: 750 },
            { nombre: "Jugo de limón fresco", cantidad: "30 ml", stock: 500 },
            { nombre: "Hojas de menta", cantidad: "10 hojas", stock: 100 },
            { nombre: "Azúcar", cantidad: "2 cucharaditas", stock: 50 },
            { nombre: "Agua con gas", cantidad: "suficiente", stock: 1000 },
            { nombre: "Hielo", cantidad: "cubos", stock: 1000 }
        ]
    },
    {
        id: 4,
        nombre: "Cuba Libre",
        tipo: "gratis",
        categoria: "Bebidas y Cocteles",
        ingredientes: [
            { nombre: "Ron oscuro", cantidad: "50 ml", stock: 750 },
            { nombre: "Refresco de cola", cantidad: "120 ml", stock: 1200 },
            { nombre: "Limón", cantidad: "1 gajo", stock: 20 },
            { nombre: "Hielo", cantidad: "cubos", stock: 1000 }
        ]
    },
    // Ejemplo premium
    {
        id: 2,
        nombre: "Piña Colada",
        tipo: "pago",
        precio: 7.5,
        categoria: "Bebidas y Cocteles",
        ingredientes: [
            { nombre: "Ron blanco", cantidad: "60 ml", stock: 750 },
            { nombre: "Jugo de piña", cantidad: "90 ml", stock: 900 },
            { nombre: "Leche de coco", cantidad: "30 ml", stock: 300 },
            { nombre: "Azúcar", cantidad: "1 cucharadita", stock: 50 },
            { nombre: "Hielo", cantidad: "cubos", stock: 1000 }
        ]
    },
    {
        id: 3,
        nombre: "Caipirinha",
        tipo: "pago",
        precio: 8.0,
        categoria: "Bebidas y Cocteles",
        ingredientes: [
            { nombre: "Cachaça", cantidad: "50 ml", stock: 500 },
            { nombre: "Azúcar", cantidad: "2 cucharaditas", stock: 50 },
            { nombre: "Lima", cantidad: "1 unidad", stock: 20 },
            { nombre: "Hielo", cantidad: "cubos", stock: 1000 }
        ]
    }
    // Elimina estos ejemplos cuando conectes la base de datos Django
];

let productoEliminarId = null;

function calcularCantidad(posible) {
    let min = Infinity;
    posible.ingredientes.forEach(ing => {
        const match = ing.cantidad.match(/(\d+)\s*ml/);
        if (match && typeof ing.stock === 'number') {
            const porProducto = parseInt(match[1]);
            const cantidad = Math.floor(ing.stock / porProducto);
            if (cantidad < min) min = cantidad;
        }
    });
    return isFinite(min) ? min : "N/A";
}

function verIngredientesProducto(id) {
    const producto = productos.find(p => p.id === id);
    if (!producto) return;
    const modal = document.getElementById('modal-detalle-pedido');
    const content = document.getElementById('detalle-pedido-content');
    content.innerHTML = `
        <span class="close-modal" id="close-modal-detalle">&times;</span>
        <div class="factura-header">
            <h2>Ingredientes de ${producto.nombre}</h2>
        </div>
        <table class="factura-table">
            <tr><td><strong>Tipo:</strong></td><td>${producto.tipo === 'pago' ? 'Premium (Pago)' : 'All Inclusive (Gratis)'}</td></tr>
            ${producto.tipo === 'pago' ? `<tr><td><strong>Precio:</strong></td><td>$${producto.precio}</td></tr>` : ''}
            <tr>
                <td colspan="2">
                    <strong>Ingredientes:</strong>
                    <ul style="margin:8px 0 0 0; padding-left:18px;">
                        ${producto.ingredientes.map(ing => `<li>${ing.nombre} (${ing.cantidad})</li>`).join('')}
                    </ul>
                </td>
            </tr>
        </table>
        <div class="factura-total">Cantidad posible: ${calcularCantidad(producto)}</div>
    `;
    modal.style.display = 'flex';

    document.getElementById('close-modal-detalle').onclick = function() {
        modal.style.display = 'none';
    };
    modal.onclick = function(e) {
        if (e.target === modal) modal.style.display = 'none';
    };
}

function renderProductos() {
    const categoriasCont = document.querySelector('.menu-categorias-caja');
    categoriasCont.innerHTML = '';
    categorias.forEach(cat => {
        // Filtra productos por categoría y tipo
        const gratis = productos.filter(p => p.categoria === cat && p.tipo === 'gratis');
        const premium = productos.filter(p => p.categoria === cat && p.tipo === 'pago');
        // Si no hay productos en ambas, no muestra la categoría
        if (gratis.length === 0 && premium.length === 0) return;

        categoriasCont.innerHTML += `
            <div class="menu-categoria-caja">
                <h3 class="menu-categoria-titulo" style="color:#22c55e;">${cat} - All Inclusive (Gratis)</h3>
                <div class="menu-productos-grid">
                    ${gratis.length > 0 ? gratis.map(producto => {
                        const cantidadMax = calcularCantidad(producto);
                        return `
                            <div class="menu-card">
                                <div class="menu-card-title">${producto.nombre}</div>
                                <div class="menu-card-cantidad">
                                    <strong>Cantidad posible:</strong> ${cantidadMax}
                                </div>
                                <div class="menu-card-actions">
                                    <button class="menu-btn-circle" title="Ver Ingredientes" onclick="verIngredientesProducto(${producto.id})">
                                        <span>🍃</span>
                                    </button>
                                    <button class="menu-btn-circle menu-btn-hammer" title="Modificar" onclick="modificarProducto(${producto.id})">
                                        <span>🔨</span>
                                    </button>
                                    <button class="menu-btn-circle menu-btn-x" title="Eliminar" onclick="confirmarEliminarProducto(${producto.id})">
                                        <span>X</span>
                                    </button>
                                </div>
                            </div>
                        `;
                    }).join('') : `<div style="text-align:center; color:#64748b; font-size:1rem; grid-column:span 4;">No hay productos en esta categoría.</div>`}
                </div>
                <h3 class="menu-categoria-titulo" style="color:#f59e42; margin-top:24px;">${cat} - Tragos Premium (Pago)</h3>
                <div class="menu-productos-grid">
                    ${premium.length > 0 ? premium.map(producto => {
                        const cantidadMax = calcularCantidad(producto);
                        return `
                            <div class="menu-card menu-premium">
                                <div class="menu-card-title">${producto.nombre}</div>
                                <div class="menu-card-cantidad">
                                    <strong>Cantidad posible:</strong> ${cantidadMax}
                                </div>
                                <div class="menu-card-precio">Precio: $${producto.precio}</div>
                                <div class="menu-card-actions">
                                    <button class="menu-btn-circle" title="Ver Ingredientes" onclick="verIngredientesProducto(${producto.id})">
                                        <span>🍃</span>
                                    </button>
                                    <button class="menu-btn-circle menu-btn-hammer" title="Modificar" onclick="modificarProducto(${producto.id})">
                                        <span>🔨</span>
                                    </button>
                                    <button class="menu-btn-circle menu-btn-x" title="Eliminar" onclick="confirmarEliminarProducto(${producto.id})">
                                        <span>X</span>
                                    </button>
                                </div>
                            </div>
                        `;
                    }).join('') : `<div style="text-align:center; color:#64748b; font-size:1rem; grid-column:span 4;">No hay productos en esta categoría.</div>`}
                </div>
            </div>
        `;
    });
}

// Modal lógica para crear producto
document.addEventListener('DOMContentLoaded', function() {
    const crearBtn = document.getElementById('crear-producto-btn');
    const modal = document.getElementById('modal-crear-producto');
    const closeModal = document.getElementById('close-modal-producto');
    const form = document.getElementById('form-crear-producto');
    const ingredientesList = document.getElementById('ingredientes-list');
    const agregarIngredienteBtn = document.getElementById('agregar-ingrediente-btn');
    const tipoProducto = document.getElementById('tipo-producto');
    const precioProductoGroup = document.getElementById('precio-producto-group');

    // Agrega select de categoría
    let categoriaGroup = document.createElement('div');
    categoriaGroup.className = "form-group";
    categoriaGroup.innerHTML = `
        <label for="categoria-producto">Categoría:</label>
        <select id="categoria-producto" name="categoria-producto" required>
            ${categorias.map(cat => `<option value="${cat}">${cat}</option>`).join('')}
        </select>
    `;
    form.querySelector('input[name="nombre-producto"]').parentNode.after(categoriaGroup);

    tipoProducto.addEventListener('change', function() {
        if (tipoProducto.value === 'pago') {
            precioProductoGroup.style.display = 'block';
        } else {
            precioProductoGroup.style.display = 'none';
        }
    });

    crearBtn.addEventListener('click', function() {
        modal.style.display = 'flex';
    });

    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    agregarIngredienteBtn.addEventListener('click', function() {
        const div = document.createElement('div');
        div.className = 'ingrediente-item';
        div.style.marginBottom = '18px'; // Espacio entre ingredientes
        div.innerHTML = `
            <input type="text" name="ingrediente-nombre[]" placeholder="Nombre" style="margin-right:12px;">
            <input type="text" name="ingrediente-cantidad[]" placeholder="Cantidad">
        `;
        ingredientesList.appendChild(div);
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const nombre = form['nombre-producto'].value;
        const tipo = form['tipo-producto'].value;
        const categoria = form['categoria-producto'].value;
        const precio = tipo === 'pago' ? parseFloat(form['precio-producto'].value) : undefined;
        const nombres = Array.from(form.querySelectorAll('input[name="ingrediente-nombre[]"]')).map(i => i.value);
        const cantidades = Array.from(form.querySelectorAll('input[name="ingrediente-cantidad[]"]')).map(i => i.value);
        const ingredientes = nombres.map((nombreIng, idx) => ({
            nombre: nombreIng,
            cantidad: cantidades[idx],
            stock: 1000 // Ejemplo, elimina esto y conecta con Django
        }));
        productos.push({
            id: Date.now(),
            nombre,
            tipo,
            categoria,
            precio,
            ingredientes
        });
        renderProductos();
        modal.style.display = 'none';
        form.reset();
        ingredientesList.innerHTML = '';
        precioProductoGroup.style.display = 'none';
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    renderProductos();
});

// Eliminar producto con advertencia
window.confirmarEliminarProducto = function(id) {
    productoEliminarId = id;
    document.getElementById('modal-eliminar-producto').style.display = 'flex';
};

document.getElementById('close-modal-eliminar').onclick = function() {
    document.getElementById('modal-eliminar-producto').style.display = 'none';
};
document.getElementById('cancelar-eliminar-producto').onclick = function() {
    document.getElementById('modal-eliminar-producto').style.display = 'none';
};
document.getElementById('modal-eliminar-producto').onclick = function(e) {
    if (e.target.id === 'modal-eliminar-producto') {
        document.getElementById('modal-eliminar-producto').style.display = 'none';
    }
};
document.getElementById('confirmar-eliminar-producto').onclick = function() {
    productos = productos.filter(p => p.id !== productoEliminarId);
    renderProductos();
    document.getElementById('modal-eliminar-producto').style.display = 'none';
};

// Modificar producto (solo ejemplo, puedes expandirlo)
window.modificarProducto = function(id) {
    alert('Funcionalidad de modificar producto pendiente de implementar.');
};

window.productos = productos;

/*
IMPORTANTE:
- Elimina todos los ejemplos del array 'productos' y los ingredientes de ejemplo en el modal cuando conectes la base de datos Django.
- Los productos y sus ingredientes deben venir de la base de datos.
- El stock debe venir de la base de datos para calcular la cantidad posible.
- El precio solo aplica para productos tipo 'pago'.
- La categoría debe venir de la base de datos.
*/