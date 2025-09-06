var ships = [];
// Inicializar el selector al cargar la página y obtener datos del backend
document.addEventListener('DOMContentLoaded', function() {
  fetch('/dashboard/api/cruceros-dashboard/')
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

// Función para renderizar la lista de cruceros en el selector
function renderShipList() {
  const selector = document.getElementById('shipSelector');
  if (!selector) return;
  
  // Limpiar opciones existentes excepto la primera
  while (selector.children.length > 1) {
    selector.removeChild(selector.lastChild);
  }
  
  // Agregar opciones para cada crucero
  ships.forEach(function(ship) {
    const option = document.createElement('option');
    option.value = ship.id;
    option.textContent = `🚢 ${ship.name} (${ship.status})`;
    selector.appendChild(option);
  });
}

// Función para renderizar todos los cruceros
function renderAllShips() {
  const dashboard = document.getElementById('dashboard');
  if (!dashboard) return;
  
  dashboard.innerHTML = `
    <div class="dashboard-box">
      <h2 class="dashboard-title">🏢 Dashboard de la Empresa</h2>
      <p class="dashboard-subtitle">Vista general de todos los cruceros</p>
      
      <div class="flex-row">
        ${ships.map(function(ship) {
          return `
            <div class="stats-block" onclick="renderSingleShip(${ship.id})" style="cursor: pointer;">
              <h3>${ship.name}</h3>
              <p><strong>Estado:</strong> ${ship.status}</p>
              <p><strong>Pasajeros:</strong> ${ship.passengers}</p>
              <p><strong>Empleados:</strong> ${ship.employees.total}</p>
              <p><strong>Ubicación:</strong> ${ship.location}</p>
              <p><strong>Presupuesto:</strong> $${ship.budget.toLocaleString()}</p>
            </div>
          `;
        }).join('')}
      </div>
      
      <div id="mainChart" style="height: 400px;">
        <canvas id="shipsChart"></canvas>
      </div>
    </div>
  `;
  
  // Actualizar el indicador de vista actual
  const currentView = document.getElementById('currentView');
  if (currentView) {
    currentView.textContent = 'Vista: Dashboard de la Empresa';
  }
  
  // Crear gráfico de cruceros
  createShipsChart();
}

// Función para renderizar un crucero específico
function renderSingleShip(shipId) {
  const ship = ships.find(function(s) { return s.id === shipId; });
  if (!ship) return;
  
  const dashboard = document.getElementById('dashboard');
  if (!dashboard) return;
  
  dashboard.innerHTML = `
    <div class="dashboard-box">
      <h2 class="dashboard-title">🚢 ${ship.name}</h2>
      <p class="dashboard-subtitle">${ship.status} - ${ship.location}</p>
      
      <div class="flex-row">
        <div class="stats-block">
          <h3>📊 Información General</h3>
          <p><strong>Estado:</strong> ${ship.status}</p>
          <p><strong>Pasajeros:</strong> ${ship.passengers}</p>
          <p><strong>Empleados:</strong> ${ship.employees.total}</p>
          <p><strong>Ubicación:</strong> ${ship.location}</p>
          <p><strong>Días en viaje:</strong> ${ship.days}</p>
          <p><strong>Distancia:</strong> ${ship.distance} km</p>
        </div>
        
        <div class="stats-block">
          <h3>💰 Finanzas</h3>
          <p><strong>Presupuesto:</strong> $${ship.budget.toLocaleString()}</p>
          <p><strong>Costos Totales:</strong> $${ship.costs.total.toLocaleString()}</p>
          <p><strong>Ganancias:</strong> $${ship.earnings.total.toLocaleString()}</p>
          <p><strong>Ganancias Reales:</strong> $${ship.earnings.real.toLocaleString()}</p>
          <p><strong>Precio Combustible:</strong> $${ship.gasPrice}/L</p>
        </div>
        
        <div class="stats-block">
          <h3>👥 Empleados por Área</h3>
          <p><strong>Restaurante:</strong> ${ship.employees.work_site.restaurante}</p>
          <p><strong>Bares:</strong> ${ship.employees.work_site.bares}</p>
          <p><strong>Mantenimiento:</strong> ${ship.employees.work_site.mantenimiento}</p>
          <p><strong>Servicio Médico:</strong> ${ship.employees.work_site.servicio_medico}</p>
          <p><strong>Entretenimiento:</strong> ${ship.employees.work_site.entretenimiento}</p>
          <p><strong>Almacén:</strong> ${ship.employees.work_site.almacen}</p>
        </div>
      </div>
      
      <div id="mainChart" style="height: 400px;">
        <canvas id="shipChart"></canvas>
      </div>
      
      <div id="secondaryChart" style="height: 300px;">
        <canvas id="costsChart"></canvas>
      </div>
    </div>
  `;
  
  // Actualizar el indicador de vista actual
  const currentView = document.getElementById('currentView');
  if (currentView) {
    currentView.textContent = `Vista: ${ship.name}`;
  }
  
  // Crear gráficos específicos del crucero
  createShipChart(ship);
  createCostsChart(ship);
}

// Función para crear el gráfico de cruceros
function createShipsChart() {
  const ctx = document.getElementById('shipsChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ships.map(function(ship) { return ship.name; }),
      datasets: [{
        label: 'Presupuesto',
        data: ships.map(function(ship) { return ship.budget; }),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }, {
        label: 'Ganancias',
        data: ships.map(function(ship) { return ship.earnings.total; }),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }, {
        label: 'Costos',
        data: ships.map(function(ship) { return ship.costs.total; }),
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Comparación Financiera de Cruceros'
        }
      }
    }
  });
}

// Función para crear el gráfico específico del crucero
function createShipChart(ship) {
  const ctx = document.getElementById('shipChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Ganancias Reales', 'Costos Totales', 'Presupuesto Restante'],
      datasets: [{
        data: [
          ship.earnings.real,
          ship.costs.total,
          ship.budget - ship.costs.total
        ],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)'
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        },
        title: {
          display: true,
          text: `Distribución Financiera - ${ship.name}`
        }
      }
    }
  });
}

// Función para crear el gráfico de costos
function createCostsChart(ship) {
  const ctx = document.getElementById('costsChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Combustible', 'Comida', 'Mantenimiento', 'Personal'],
      datasets: [{
        label: 'Costos por Categoría',
        data: [
          ship.costs.categories.combustible,
          ship.costs.categories.comida,
          ship.costs.categories.mantenimiento,
          ship.costs.categories.personal
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 205, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 205, 86, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Desglose de Costos'
        }
      }
    }
  });
}

// Función para renderizar solicitudes de compra
function renderPurchaseRequests() {
  const container = document.getElementById('purchaseRequests');
  if (!container) return;
  
  container.innerHTML = `
    <div class="purchase-requests">
      <h3>📋 Solicitudes de Compra</h3>
      ${purchaseRequests.map(function(request) {
        const statusClass = request.status === 'approved' ? 'approved' : 
                           request.status === 'rejected' ? 'rejected' : '';
        const statusText = request.status === 'approved' ? 'Aprobada' :
                          request.status === 'rejected' ? 'Rechazada' : 'Pendiente';
        const statusColor = request.status === 'approved' ? '#10b981' :
                           request.status === 'rejected' ? '#ef4444' : '#fbbf24';
        
        return `
          <div class="purchase-request-card ${statusClass}">
            <div class="request-details">
              <h4>${request.ship_name}</h4>
              <p><strong>Monto:</strong> $${request.amount.toLocaleString()}</p>
              <p><strong>Descripción:</strong> ${request.description}</p>
              <p><strong>Estado:</strong> <span style="color: ${statusColor}; font-weight: bold;">${statusText}</span></p>
              <p><strong>Fecha:</strong> ${request.created_at}</p>
              ${request.rejection_reason ? `<p><strong>Razón de Rechazo:</strong> ${request.rejection_reason}</p>` : ''}
            </div>
            <div class="request-actions">
              ${request.status === 'pending' ? `
                <button class="btn-approve" onclick="approveRequest(${request.id})">Aprobar</button>
                <button class="btn-reject" onclick="rejectRequest(${request.id})">Rechazar</button>
              ` : ''}
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

// Función para renderizar calculadora de presupuesto
function renderBudgetCalculation() {
  const container = document.getElementById('budgetCalculation');
  if (!container) return;
  
  container.innerHTML = `
    <div class="budget-calculator">
      <h3>🧮 Calculadora de Presupuesto</h3>
      <div class="budget-input-group">
        <div class="budget-input">
          <label for="passengers">Pasajeros:</label>
          <input type="number" id="passengers" value="150" min="1">
        </div>
        <div class="budget-input">
          <label for="employees">Empleados:</label>
          <input type="number" id="employees" value="50" min="1">
        </div>
        <div class="budget-input">
          <label for="days">Días:</label>
          <input type="number" id="days" value="7" min="1">
        </div>
        <div class="budget-input">
          <label for="distance">Distancia (km):</label>
          <input type="number" id="distance" value="1000" min="1">
        </div>
      </div>
      <button onclick="calculateBudget()" style="background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 16px;">
        Calcular Presupuesto
      </button>
      <div id="budgetResult" class="budget-result" style="display: none;">
        <div id="budgetAmount"></div>
      </div>
    </div>
  `;
}

// Función para calcular presupuesto
function calculateBudget() {
  const passengers = parseInt(document.getElementById('passengers').value) || 0;
  const employees = parseInt(document.getElementById('employees').value) || 0;
  const days = parseInt(document.getElementById('days').value) || 0;
  const distance = parseInt(document.getElementById('distance').value) || 0;
  
  // Fórmula de presupuesto
  const costoCombustible = distance * 2.5;
  const costoComida = (passengers + employees) * days * 45;
  const costoMantenimiento = days * 1200;
  const costoOperacional = employees * days * 80;
  
  const totalBudget = costoCombustible + costoComida + costoMantenimiento + costoOperacional;
  
  const resultDiv = document.getElementById('budgetResult');
  const amountDiv = document.getElementById('budgetAmount');
  
  amountDiv.innerHTML = `
    <div>Presupuesto Estimado: $${totalBudget.toLocaleString()}</div>
    <div style="font-size: 14px; margin-top: 10px;">
      <div>Combustible: $${costoCombustible.toLocaleString()}</div>
      <div>Comida: $${costoComida.toLocaleString()}</div>
      <div>Mantenimiento: $${costoMantenimiento.toLocaleString()}</div>
      <div>Operacional: $${costoOperacional.toLocaleString()}</div>
    </div>
  `;
  
  resultDiv.style.display = 'block';
}

// Función para aprobar solicitud
function approveRequest(requestId) {
  fetch(`/dashboard/api/purchase-requests/${requestId}/approve/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
  .then(function(response) { return response.json(); })
  .then(function(data) {
    if (data.status === 'success') {
      // Actualizar la solicitud en el array local
      const request = purchaseRequests.find(function(r) { return r.id === requestId; });
      if (request) {
        request.status = 'approved';
        request.rejection_reason = null;
      }
      // Re-renderizar las solicitudes
      renderPurchaseRequests();
      alert('Solicitud aprobada exitosamente');
    } else {
      alert('Error al aprobar la solicitud');
    }
  })
  .catch(function(error) {
    console.error('Error:', error);
    alert('Error al aprobar la solicitud');
  });
}

// Función para rechazar solicitud
function rejectRequest(requestId) {
  const reason = prompt('Ingresa la razón del rechazo:');
  if (!reason) return;
  
  fetch(`/dashboard/api/purchase-requests/${requestId}/reject/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ reason: reason })
  })
  .then(function(response) { return response.json(); })
  .then(function(data) {
    if (data.status === 'success') {
      // Actualizar la solicitud en el array local
      const request = purchaseRequests.find(function(r) { return r.id === requestId; });
      if (request) {
        request.status = 'rejected';
        request.rejection_reason = reason;
      }
      // Re-renderizar las solicitudes
      renderPurchaseRequests();
      alert('Solicitud rechazada exitosamente');
    } else {
      alert('Error al rechazar la solicitud');
    }
  })
  .catch(function(error) {
    console.error('Error:', error);
    alert('Error al rechazar la solicitud');
  });
}

// Función auxiliar para obtener cookie CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
