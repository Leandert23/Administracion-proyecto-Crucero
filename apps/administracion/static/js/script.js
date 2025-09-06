var ships = [];
// Inicializar el selector al cargar la página y obtener datos del backend
document.addEventListener('DOMContentLoaded', function() {
  fetch('dashboard/api/cruceros-dashboard/')
    .then(function(response) { return response.json(); })
    .then(function(data) {
      ships = data.ships || [];
      purchaseRequests = data.purchase_requests || [];
      renderShipList();
      const selector = document.getElementById('shipSelector');
      selector.addEventListener('change', function() {
        if (selector.value === 'all') {
          renderAllShips();
        } else {
          renderSingleShip(Number(selector.value));
        }
      });
      renderAllShips();
    })
  .catch(function(error) {
    console.error('Error al obtener los datos de los cruceros:', error);
    ships = [];
    purchaseRequests = [
      {
        id: 1,
        ship_name: "Crucero Atlántico",
        amount: 15000,
        description: "Combustible para próximo viaje",
        status: "pending",
        created_at: "2024-01-15",
      },
      {
        id: 2,
        ship_name: "Crucero Pacífico",
        amount: 8500,
        description: "Suministros de cocina",
        status: "pending",
        created_at: "2024-01-14",
      },
    ];
    renderShipList();
    const selector = document.getElementById('shipSelector');
    selector.addEventListener('change', function() {
      if (selector.value === 'all') {
        renderAllShips();
            } else {
        renderSingleShip(Number(selector.value));
      }
    });
    renderAllShips();
  });
});

function showTab(tabName) {
  currentTab = tabName;

  document.querySelectorAll(".tab-button").forEach(function(btn) {
    btn.classList.remove("active");
  });
  document.getElementById(tabName + "Tab").classList.add("active");

  if (tabName === "dashboard") {
    document.getElementById("dashboard").style.display = "block";
    document.getElementById("purchaseRequests").style.display = "none";
    document.getElementById("budgetCalculation").style.display = "none";
  } else if (tabName === "purchase") {
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("purchaseRequests").style.display = "block";
    document.getElementById("budgetCalculation").style.display = "none";
    renderPurchaseRequests();
  } else if (tabName === "budget") {
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("purchaseRequests").style.display = "none";
    document.getElementById("budgetCalculation").style.display = "block";
    renderBudgetCalculation();
  }
}

function renderPurchaseRequests() {
  const container = document.getElementById("purchaseRequests");

  if (purchaseRequests.length === 0) {
    container.innerHTML = `
      <div class="dashboard-box">
        <h2 class="dashboard-title">Solicitudes de Compra</h2>
        <p style="text-align: center; color: #64748b; margin: 40px 0;">No hay solicitudes de compra pendientes</p>
      </div>
    `;
    return;
  }

  let requestsHtml = `
    <div class="dashboard-box">
      <h2 class="dashboard-title">Solicitudes de Compra</h2>
      <p style="text-align: center; color: #64748b; margin-bottom: 30px;">
        Gestiona las solicitudes de compra del módulo de compras
      </p>
  `;

  purchaseRequests.forEach(function(request) {
    const statusClass = request.status === "approved" ? "approved" : request.status === "rejected" ? "rejected" : "";

    requestsHtml += `
      <div class="purchase-request-card ${statusClass}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
          <h3 style="margin: 0; color: #1e293b;">${request.ship_name}</h3>
          <span style="background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #475569;">
            ${request.created_at}
          </span>
        </div>
        <p style="margin: 10px 0; color: #64748b;"><strong>Descripción:</strong> ${request.description}</p>
        <p style="margin: 10px 0; color: #1e293b; font-size: 18px;"><strong>Monto:</strong> $${request.amount.toLocaleString()}</p>
        
        ${request.status === "pending" ? `
          <div class="purchase-actions">
            <button class="btn-approve" onclick="approvePurchaseRequest(${request.id})">
              Aprobar
            </button>
            <button class="btn-reject" onclick="showRejectModal(${request.id})">
              Rechazar
            </button>
          </div>
        ` : `
          <div style="margin-top: 15px;">
            <span style="padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: bold; 
                         background: ${request.status === "approved" ? "#dcfce7; color: #166534" : "#fee2e2; color: #dc2626"};">
              ${request.status === "approved" ? "APROBADA" : "RECHAZADA"}
            </span>
            ${request.rejection_reason ? `<p style="margin-top: 10px; color: #dc2626;"><strong>Razón:</strong> ${request.rejection_reason}</p>` : ""}
          </div>
        `}
      </div>
    </div>`;
  });

  container.innerHTML = requestsHtml;
}

function showRejectModal(requestId) {
  const reason = prompt("Ingrese la razón del rechazo:");
  if (reason && reason.trim()) {
    rejectPurchaseRequest(requestId, reason.trim());
  }
}

function approvePurchaseRequest(requestId) {
  const request = purchaseRequests.find(function(r) { return r.id === requestId; });
  if (request) {
    request.status = "approved";
    renderPurchaseRequests();

    fetch("/administracion/api/purchase-requests/" + requestId + "/approve/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
    }).catch(function(error) { console.error("Error approving request:", error); });
  }
}

function rejectPurchaseRequest(requestId, reason) {
  const request = purchaseRequests.find(function(r) { return r.id === requestId; });
  if (request) {
    request.status = "rejected";
    request.rejection_reason = reason;
    renderPurchaseRequests();

    fetch("/administracion/api/purchase-requests/" + requestId + "/reject/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ reason: reason }),
    }).catch(function(error) { console.error("Error rejecting request:", error); });
  }
}

function renderBudgetCalculation() {
  const container = document.getElementById("budgetCalculation");

  /* Valores por defecto */
  const ticketPrice = 1500;
  const nonIncludedEstimate = 500;
  const capacity = 2000;
  const occupancyRate = 0.6;
  
  const estimatedBudget = ((ticketPrice + nonIncludedEstimate) * 0.9) * (capacity * occupancyRate);
  const totalCosts = 850000;
  const remainingBudget = estimatedBudget - totalCosts;
  
  container.innerHTML = `
    <div class="dashboard-box">
      <h1 class="dashboard-title">Cálculo de Presupuesto</h1>
      
      <div class="budget-calculation">
        <h3>Fórmula de cálculo:</h3>
        <p>[(Precio de los boletos + Estimado de los no incluidos) - Total*10%] * Capacidad del barco al 60%</p>
        
        <h3>Valores actuales:</h3>
        <ul>
          <li>Precio de boletos: $${ticketPrice}</li>
          <li>Estimado de servicios no incluidos: $${nonIncludedEstimate}</li>
          <li>Capacidad del barco: ${capacity} pasajeros</li>
          <li>Porcentaje de ocupación: ${occupancyRate * 100}%</li>
        </ul>
        
        <h3>Resultados:</h3>
        <ul>
          <li><strong>Presupuesto estimado:</strong> $${estimatedBudget.toLocaleString()}</li>
          <li><strong>Costos totales:</strong> $${totalCosts.toLocaleString()}</li>
          <li><strong>Presupuesto restante:</strong> $${remainingBudget.toLocaleString()}</li>
        </ul>
      </div>
      
      <div style="margin-top: 20px;">
        <canvas id="budgetChart" width="400" height="200"></canvas>
      </div>
    </div>
  `;
  
  setTimeout(function() {
    const ctx = document.getElementById("budgetChart").getContext("2d");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Presupuesto utilizado", "Presupuesto restante"],
        datasets: [{
          data: [totalCosts, remainingBudget],
          backgroundColor: ["#f44336", "#4caf50"]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
          title: {
            display: true,
            text: "Distribución del Presupuesto"
          }
        }
      }
    });
  }, 100);
}

function getCsrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
}

// Variables globales para los graficos
let mainChart = null;
let secondaryChart = null;
let selectedShipId = null;

// Renderiza el dashboard de todos los barcos
function renderAllShips() {
  const dashboard = document.getElementById('dashboard');
  // Calcular totales
  const active = ships.filter(s => s.status === 'activo' || s.status === 'Navegando' || s.status === 'viaje').length;
  const inactive = ships.filter(s => s.status === 'inactivo' || s.status === 'Embarcado').length;
  const maintenance = ships.filter(s => s.status === 'mantenimiento' || s.status === 'En mantenimiento').length;
  const totalCosts = ships.reduce((acc, s) => acc + (s.costs?.total || 0), 0);
  const totalEarnings = ships.reduce((acc, s) => acc + (s.earnings?.total || 0), 0);
  const realEarnings = ships.reduce((acc, s) => acc + (s.earnings?.real || 0), 0);
  const allAlerts = ships.flatMap(s => s.alerts || []);
  const shipsLocations = (ships.flatMap(s => [s.location, s.name] || [])).map(
    (locate, index) => {
    if (index%2 === 0){
      return `<span>${locate}, </span>`
    } else{
      return `<span">${locate}</span><br>`
    }}).join('');
  let alertsHtml = '';
  let numberAlerts = '';
  if (allAlerts.length > 0) {
    alertsHtml = `<div>${allAlerts.map(a => `<div>${a}</div>`).join('')}</div>`;
    numberAlerts = `<strong>(${allAlerts.length})</strong>`;
  } else{
    alertsHtml = `<div>No hay alertas</div>`;
  }
  dashboard.innerHTML = `
    <div class="dashboard-box">
      <div style="background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&h=300&fit=crop'); 
                  background-size: cover; background-position: center; border-radius: 12px; padding: 40px; margin-bottom: 20px; text-align: center;">
        <h1 style="color: white; font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">Dashboard de Cruceros</h1>
        <p style="color: white; font-size: 1.2em; margin: 10px 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.7);">Sistema de gestión integral de flota</p>
      </div>
      <div class="content-box">
        <div>
          <h2 style="color: #2196f3; margin-bottom: 15px;">Estado de la Flota</h2>
          <ul style="padding-left: 20px; padding-top: 10px;">
            <li>🚢 Barcos activos: ${active}</li>
            <li>⚓ Barcos inactivos: ${inactive}</li>
            <li>🔧 Barcos en mantenimiento: ${maintenance}</li>
            <li>🌊 Barcos en viaje: ${active}</li>
          </ul>
        </div>
        <button id="open-modal-btn" class="open-modal-btn">Ver Alertas${numberAlerts}</button>
        <div id="myModal" style="display: none;" class="modal-overlay">
          <div class="modal-content">
            <h2>Ventana de Alertas</h2>
            ${alertsHtml}
            <button id="close-modal-btn" class="close-button">&times;</button>
          </div>
        </div>
      </div>
      <div class="budget-calculator">
        <h3 style="color: #1e40af; margin-bottom: 15px; text-align: center;">📊 Calculadora de Presupuesto</h3>
        <div class="budget-input-group">
          <div class="budget-input">
            <label>Pasajeros:</label>
            <input type="number" id="budgetPassengers" placeholder="Número de pasajeros" value="100">
          </div>
          <div class="budget-input">
            <label>Empleados:</label>
            <input type="number" id="budgetEmployees" placeholder="Número de empleados" value="50">
          </div>
          <div class="budget-input">
            <label>Días de viaje:</label>
            <input type="number" id="budgetDays" placeholder="Días de viaje" value="7">
          </div>
          <div class="budget-input">
            <label>Distancia (km):</label>
            <input type="number" id="budgetDistance" placeholder="Distancia en km" value="1000">
          </div>
        </div>
        <button onclick="calculateBudget()" style="background: #1e40af; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%;">
          Calcular Presupuesto
        </button>
        <div id="budgetResult" class="budget-result" style="display: none;"></div>
      </div>

      <hr>
      <div class="flex-row">
        <div class="nav-link">
          <div class="dashboard-subtitle">Distribución por barcos</div>
          <canvas id="mainChart" style="max-width:600px; margin:auto;"></canvas>
        </div>
      </div>
      <div class="flex-row">
        <div class="stats-block">
          <strong>💰 Costos totales:</strong> $${totalCosts.toLocaleString()}<br>
          <strong>📈 Ganancias totales:</strong> $${totalEarnings.toLocaleString()}
        </div>
        <div class="stats-block">
          <strong>💵 Ganancias reales:</strong> $${realEarnings.toLocaleString()}
        </div>
        <div class="stats-block">
          <strong>Ubicación de los cruceros:</strong>
          <div>
            ${shipsLocations}
          </div>
        </div>
      </div>
    </div>
  `;
  setTimeout(renderAllShipsCharts, 0);
  renderModal();
}

function renderModal(allAlerts){
  const myModal = document.getElementById('myModal');
  const openModalBtn = document.getElementById('open-modal-btn');
  const closeModalBtn = document.getElementById('close-modal-btn');
  
  // Función para abrir el modal
  function openModal() {
    myModal.style.display = 'flex'; // Usa 'flex' para centrar el contenido
  }

  // Función para cerrar el modal
  function closeModal() {
    myModal.style.display = 'none';
  }

  // Event listeners para los botones
  openModalBtn.addEventListener('click', openModal);
  closeModalBtn.addEventListener('click', closeModal);

  // Opcional: Cerrar el modal al hacer clic fuera de él
  window.addEventListener('click', (event) => {
    if (event.target === myModal) {
      closeModal();
    }
  });
}

// Renderiza los gráficos de todos los barcos
function renderAllShipsCharts() {
  const ctx = document.getElementById('mainChart').getContext('2d');
  if (mainChart) mainChart.destroy();
  mainChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ships.map(s => s.name),
      datasets: [
        {
          label: 'Costos totales',
          data: ships.map(s => (s.costs?.total || 0)),
          backgroundColor: '#b3dafe',
        },
        {
          label: 'Ganancias totales',
          data: ships.map(s => (s.earnings?.total || 0)),
          backgroundColor: '#aaf2b2',
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title: {
          display: true,
          text: 'Costos y Ganancias por Barco',
          font: { size: 18 }
        }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

// Renderiza los gráficos de un solo barco
function renderSingleShipCharts(ship) {
  // Costos por categoría
  const ctx1 = document.getElementById('mainChart').getContext('2d');
  if (mainChart) mainChart.destroy();
  mainChart = new Chart(ctx1, {
    type: 'pie',
    data: {
      labels: Object.keys(ship.costs?.categories || {}),
      datasets: [{
        label: 'Costos',
        data: Object.values(ship.costs?.categories || {}).map(v => v || 0),
        backgroundColor: ['#b3dafe', '#aaf2b2', '#f9c2c2'],
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title: {
          display: true,
          text: 'Costos por Categoría',
          font: { size: 16 }
        }
      }
    }
  });
  // Ganancias por categoría
  const ctx2 = document.getElementById('secondaryChart').getContext('2d');
  if (secondaryChart) secondaryChart.destroy();
  secondaryChart = new Chart(ctx2, {
    type: 'pie',
    data: {
      labels: Object.keys(ship.earnings?.categories || {}),
      datasets: [{
        label: 'Ganancias',
        data: Object.values(ship.earnings?.categories || {}).map(v => v || 0),
        backgroundColor: ['#b3dafe', '#aaf2b2', '#f9c2c2'],
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        title: {
          display: true,
          text: 'Ganancias por Categoría',
          font: { size: 16 }
        }
      }
    }
  });
}

function renderShipList() {
  const selector = document.getElementById('shipSelector');
  selector.innerHTML = '';
  const optAll = document.createElement('option');
  optAll.value = 'all';
  optAll.textContent = 'Todos los barcos';
  selector.appendChild(optAll);
  ships.forEach(ship => {
    const opt = document.createElement('option');
    opt.value = ship.id;
    opt.textContent = ship.name;
    selector.appendChild(opt);
  });
}

function renderSingleShip(shipId) {
  selectedShipId = shipId;
  const ship = ships.find(s => s.id === shipId);
  const dashboard = document.getElementById('dashboard');
  let alertsHtml = '';
  if (ship.alerts && ship.alerts.length > 0) {
    alertsHtml = '<div class="alerts">' + ship.alerts.map(function(a) { return '<div>' + a + '</div>'; }).join('') + '</div>';
  }

  let shipImage = "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&h=200&fit=crop";
  if (ship.status === "mantenimiento" || ship.status === "En mantenimiento") {
    shipImage = "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=400&h=200&fit=crop";
  } else if (ship.status === "inactivo" || ship.status === "Embarcado") {
    shipImage = "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=200&fit=crop";
  }

  dashboard.innerHTML =
    '<div class="dashboard-box" style="max-height: 100%;">' +
      "<div style=\"background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('" +
    shipImage +
    "'); background-size: cover; background-position: center; border-radius: 12px; padding: 30px; margin-bottom: 20px; text-align: center;\"></div>" +
      '<div class="content-box">' +
        '<h1 style="color: white; font-size: 2em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">' +
          ship.name +
        "</h1>" +
        alertsHtml +
      '</div>' +
      '<h2>Estado: <strong>' + ship.status + '</strong> &nbsp;|&nbsp; Precio de la gasolina: <strong>' + (ship.gasPrice || 0) + '</strong></h2>' +
      '<h3>Presupuesto por parada para compras: ' + (ship.budget || 0) + '</h3>' +
      '<strong>Ubicación actual:</strong> ' + ship.location + '<br>' +
      '<strong>Días en viaje:</strong> ' + ship.days + '<br>' +
      '<strong>Distancia del viaje:</strong> ' + (ship.distance || 0) +
      '<button onclick="calculateShipBudget()" style="background: #1e40af; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%;">' +
      "Calcular Presupuesto para " +
        ship.name +
      "</button>" +
      '<div id="shipBudgetResult" class="budget-result" style="display: none;"></div>' +
      "</div>" +

      '<hr>' +
      '<div class="flex-row">' +
        '<div class="stats-block">' +
          '<strong>Número de pasajeros actual:</strong> ' + ship.passengers + '<br>' +
          '<strong>Número de empleados actual:</strong> ' + ship.employees.total +
        '</div>' +
        '<div class="stats-block">' +
          '<strong>Número de empleados activos:</strong> ' + ship.employees.status.active_employees + '<br>' +
          '<strong>Número de empleados inactivos:</strong> ' + ship.employees.status.inactive_employees + '<br>'+
          '<strong>Número de empleados de baja:</strong> ' + ship.employees.status.de_baja_employees +
        '</div>' +
        '<div class="stats-block">' +
          '<h4>Distribución de los empleados en el barco: </h4>'+
          '<strong>Número de empleados en los restaurantes:</strong> ' + ship.employees.work_site.restaurante + '<br>' +
          '<strong>Número de empleados en los bares:</strong> ' + ship.employees.work_site.bares + '<br>' +
          '<strong>Número de empleados en el mantenimiento:</strong> ' + ship.employees.work_site.mantenimiento + '<br>' +
          '<strong>Número de empleados en servicio médico:</strong> ' + ship.employees.work_site.servicio_medico + '<br>' +
          '<strong>Número de empleados en entretenimiento:</strong> ' + ship.employees.work_site.entretenimiento + '<br>' +
          '<strong>Número de empleados en el almacen:</strong> ' + ship.employees.work_site.almacen + '<br>' +
          '<strong>Número de empleados en las ventas:</strong> ' + ship.employees.work_site.ventas + '<br>' +
          '<strong>Número de empleados en las compras:</strong> ' + ship.employees.work_site.compras + '<br>' +
          '<strong>Número de empleados en la administración:</strong> ' + ship.employees.work_site.administracion + 
        '</div>' +
      '</div>' +
      '<div class="flex-row">' +
        '<div class="stats-block">' +
          '<h3><strong>Costos totales</strong></h3><br>' +
          '<strong>Total:</strong> ' + ((ship.costs && ship.costs.total) ? ship.costs.total.toLocaleString() : 0) + '<br>' +
          'Distribución de costos por categorías y su cantidad<br>' +
          '<canvas id="mainChart"></canvas>' +
        '</div>' +
        '<div class="stats-block">' +
          '<h3><strong>Ganancias totales y reales</strong></h3><br>' +
          '<strong>Total:</strong> ' + ((ship.earnings && ship.earnings.total) ? ship.earnings.total.toLocaleString() : 0) + '<br>' +
          '<strong>Real:</strong> ' + ((ship.earnings && ship.earnings.real) ? ship.earnings.real.toLocaleString() : 0) + '<br>' +
          'Distribución de ganancias por categorías y su cantidad<br>' +
          '<canvas id="secondaryChart"></canvas>' +
        '</div>' +
      '</div>' +
    '</div>';
  setTimeout(function() { renderSingleShipCharts(ship); }, 0);
}

function calculateBudget() {
  const passengers = Number.parseInt(document.getElementById("budgetPassengers").value) || 0;
  const employees = Number.parseInt(document.getElementById("budgetEmployees").value) || 0;
  const days = Number.parseInt(document.getElementById("budgetDays").value) || 0;
  const distance = Number.parseInt(document.getElementById("budgetDistance").value) || 0;

  const fuelCost = distance * 2.5;
  const foodCost = (passengers + employees) * days * 45;
  const maintenanceCost = days * 1200;
  const operationalCost = employees * days * 80;

  const totalBudget = fuelCost + foodCost + maintenanceCost + operationalCost;

  const resultDiv = document.getElementById("budgetResult");
  resultDiv.style.display = "block";
  resultDiv.innerHTML = `
    <div>Presupuesto Total: $${totalBudget.toLocaleString()}</div>
    <div style="font-size: 14px; margin-top: 10px; opacity: 0.9;">
      Combustible: $${fuelCost.toLocaleString()} | 
      Comida: $${foodCost.toLocaleString()} | 
      Mantenimiento: $${maintenanceCost.toLocaleString()} | 
      Operacional: $${operationalCost.toLocaleString()}
    </div>
  `;
}

function calculateShipBudget() {
  const passengers = Number.parseInt(document.getElementById("shipBudgetPassengers").value) || 0;
  const employees = Number.parseInt(document.getElementById("shipBudgetEmployees").value) || 0;
  const days = Number.parseInt(document.getElementById("shipBudgetDays").value) || 0;
  const distance = Number.parseInt(document.getElementById("shipBudgetDistance").value) || 0;

  const fuelCost = distance * 2.5;
  const foodCost = (passengers + employees) * days * 45;
  const maintenanceCost = days * 1200;
  const operationalCost = employees * days * 80;

  const totalBudget = fuelCost + foodCost + maintenanceCost + operationalCost;

  const resultDiv = document.getElementById("shipBudgetResult");
  resultDiv.style.display = "block";
  resultDiv.innerHTML = `
    <div>Presupuesto Total: $${totalBudget.toLocaleString()}</div>
    <div style="font-size: 14px; margin-top: 10px; opacity: 0.9;">
      Combustible: $${fuelCost.toLocaleString()} | 
      Comida: $${foodCost.toLocaleString()} | 
      Mantenimiento: $${maintenanceCost.toLocaleString()} | 
      Operacional: $${operationalCost.toLocaleString()}
    </div>
  `;
}