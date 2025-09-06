// --- FUSIÓN DE script.js Y script-frontend.js ---

// Botón devolver para proveedores.html
function devolverDashboard() {
    // Redirigir a la sección de compras (index)
    window.location.href = '/';
}
let paises = [];

let materiales = [];

function addPais() {
    const input = document.getElementById('pais-input');
    const value = input.value.trim();
    if (value && !paises.includes(value)) {
        paises.push(value);
        updatePaisList();
        input.value = '';
    }
}
function removePais(index) {
    paises.splice(index, 1);
    updatePaisList();
}
function updatePaisList() {
    const ul = document.getElementById('pais-list');
    ul.innerHTML = '';
    paises.forEach((pais, idx) => {
        const li = document.createElement('li');
        li.textContent = pais + ' ';
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = 'Eliminar';
        btn.onclick = () => removePais(idx);
        li.appendChild(btn);
        ul.appendChild(li);
    });
    const paisesJson = document.getElementById('paises-json');
    if (paisesJson) paisesJson.value = JSON.stringify(paises);
}

function addMaterial() {
    const input = document.getElementById('material-input');
    const costoInput = document.getElementById('costo-material-input');
    const nombre = input.value.trim();
    const costo = costoInput.value.trim();
    if (nombre && costo && !materiales.some(m => m.nombre === nombre)) {
        materiales.push({ nombre, costo });
        updateMaterialList();
        input.value = '';
        costoInput.value = '';
    }
}

function updateMaterialList() {
    const ul = document.getElementById('material-list');
    ul.innerHTML = '';
    materiales.forEach((mat, idx) => {
        const li = document.createElement('li');
        li.textContent = `${mat.nombre} (Costo: $${mat.costo}) `;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = 'Eliminar';
        btn.onclick = () => removeMaterial(idx);
        li.appendChild(btn);
        ul.appendChild(li);
    });
    const materialesJson = document.getElementById('materiales-json');
    if (materialesJson) materialesJson.value = JSON.stringify(materiales);
}

function devolverDashboard() {
    const proveedoresContent = document.getElementById('proveedores-content');
    const comprasContent = document.getElementById('compras-content');
    if (proveedoresContent && comprasContent) {
        proveedoresContent.style.display = 'none';
        comprasContent.style.display = 'block';
    }
    const pageTitle = document.querySelector('.page-title');
    const pageSubtitle = document.querySelector('.page-subtitle');
    if (pageTitle) pageTitle.textContent = 'Compras';
    if (pageSubtitle) pageSubtitle.textContent = 'Gestión de compras, proveedores y solicitudes';
}

function actualizarTablaProveedores(proveedores) {
    const tbody = document.getElementById('proveedores-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    proveedores.forEach(prov => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prov.name}</td>
            <td>${prov.service_or_product}</td>
            <td>${prov.categorie}</td>
            <td>${prov.contact}</td>
            <td>${Array.isArray(prov.countries) ? prov.countries.join(', ') : prov.countries}</td>
            <td>${prov.sucursal}</td>
            <td>${Array.isArray(prov.materiales) ? prov.materiales.join(', ') : prov.materiales}</td>
        `;
        tbody.appendChild(tr);
    });
    agregarEventosEliminarProveedor();
}

document.addEventListener('DOMContentLoaded', function() {
    // Solo lógica de inicialización, sin AJAX para registrar proveedores
});
