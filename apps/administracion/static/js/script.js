  const ships = [
    {
      id: 1,
      name: "Crucero Atlántico",
      status: "Navegando",
      gasPrice: 1200,
      passengers: 320,
      employees: 80,
      location: "Mar Caribe",
      days: 12,
      distance: 1800,
      budget: 50000,
      costs: {
        total: 120000,
        categories: {
          Combustible: 60000,
          Mantenimiento: 30000,
          Provisiones: 30000
        }
      },
      earnings: {
        total: 200000,
        real: 180000,
        categories: {
          Pasajes: 150000,
          Tiendas: 20000,
          Excursiones: 10000
        }
      },
      alerts: [
        "Nivel de combustible bajo",
        "Revisión de motor pendiente"
      ]
    },
    {
      id: 2,
      name: "Crucero Pacífico",
      status: "Embarcado",
      gasPrice: 1150,
      passengers: 280,
      employees: 70,
      location: "Puerto de Valparaíso",
      days: 0,
      distance: 0,
      budget: 40000,
      costs: {
        total: 100000,
        real: 95000,
        categories: {
          Combustible: 50000,
          Mantenimiento: 25000,
          Provisiones: 25000
        }
      },
      earnings: {
        total: 170000,
        real: 160000,
        categories: {
          Pasajes: 120000,
          Tiendas: 30000,
          Excursiones: 10000
        }
      },
      alerts: [
        "Inspección sanitaria requerida"
      ]
    },
    {
      id: 3,
      name: "Crucero Mediterráneo",
      status: "Navegando",
      gasPrice: 1300,
      passengers: 400,
      employees: 100,
      location: "Costa de Italia",
      days: 7,
      distance: 1200,
      budget: 60000,
      costs: {
        total: 150000,
        categories: {
          Combustible: 80000,
          Mantenimiento: 40000,
          Provisiones: 30000
        }
      },
      earnings: {
        total: 250000,
        real: 230000,
        categories: {
          Pasajes: 180000,
          Tiendas: 40000,
          Excursiones: 10000
        }
      },
      alerts: []
    }
  ];
  // Inicializar el selector al cargar la página
  document.addEventListener('DOMContentLoaded', function() {
    renderShipList();
    const selector = document.getElementById('shipSelector');
    selector.addEventListener('change', function() {
      if (selector.value === 'all') {
        renderAllShips();
      } else {
        showSingleShip(Number(selector.value));
      }
    });
    // Mostrar todos los barcos por defecto
    renderAllShips();
  });

// Variables globales para los graficos
let mainChart = null;
let secondaryChart = null;
let selectedShipId = null;

// Renderiza el dashboard de todos los barcos
function renderAllShips() {
  const dashboard = document.getElementById('dashboard');
  // Calcular totales
  const active = ships.filter(s => s.status === 'Navegando').length;
  const inactive = ships.filter(s => s.status !== 'Navegando').length;
  const maintenance = ships.filter(s => (s.status === 'En mantenimiento') || (s.status === 'mantenimiento')).length;
  const totalCosts = ships.reduce((acc, s) => acc + s.costs.total, 0);
  const totalEarnings = ships.reduce((acc, s) => acc + s.earnings.total, 0);
  const realEarnings = ships.reduce((acc, s) => acc + s.earnings.real, 0);
  // Alertas
  const allAlerts = ships.flatMap(s => s.alerts);
  let alertsHtml = '';
  if (allAlerts.length > 0) {
    alertsHtml = `<div class='alerts'>${allAlerts.map(a => `<div>${a}</div>`).join('')}</div>`;
    alertsHtml = `<div class='alerts' style='position:absolute; right:20px; top:20px; max-width:300px; background:#f9c2c2; color:#333; border-radius:12px; padding:12px;'>${alertsHtml.replace("class='alerts'",'')}</div>`;
  }
  dashboard.innerHTML = `
    <div class="dashboard-box">
      <div class="content-box">
        <div>
          <h1 class="dashboard-title">Dashboard</h1><span style="color:#5e5e5e">Sistema de gestión de barcos</span>
          <ul style="padding-left: 20px; padding-top: 10px;">
            <li>Barcos activos: ${active}</li>
            <li>Barcos inactivos: ${inactive}</li>
            <li>Barcos en mantenimiento: ${maintenance}</li>
            <li>Barcos en viaje: ${active}</li>
          </ul>
        </div>
        ${alertsHtml}
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
          <strong>Costos totales:</strong> ${totalCosts}<br>
          <strong>Ganancias totales:</strong> ${totalEarnings}
        </div>
        <div class="stats-block">
          <strong>Ganancias reales:</strong> ${realEarnings}
        </div>
      </div>
    </div>
  `;
  setTimeout(renderAllShipsCharts, 0);
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
          data: ships.map(s => s.costs.total),
          backgroundColor: '#b3dafe',
        },
        {
          label: 'Ganancias totales',
          data: ships.map(s => s.earnings.total),
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
      labels: Object.keys(ship.costs.categories),
      datasets: [{
        label: 'Costos',
        data: Object.values(ship.costs.categories),
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
      labels: Object.keys(ship.earnings.categories),
      datasets: [{
        label: 'Ganancias',
        data: Object.values(ship.earnings.categories),
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
    alertsHtml = `<div class="alerts">${ship.alerts.map(a => `<div>${a}</div>`).join('')}</div>`;
  }
  dashboard.innerHTML = `
    <div class="dashboard-box" style="max-height: 100%;">
      <div class="content-box">
        <h1 class="dashboard-title">${ship.name}</h1>
        ${alertsHtml}
      </div>
      <h2>Estado: <strong>${ship.status}</strong> &nbsp;|&nbsp; Precio de la gasolina: <strong>${ship.gasPrice}</strong></h2>
      <h3>Presupuesto por parada para compras: ${ship.budget}</h3>
      <hr>
      <div class="flex-row">
        <div class="stats-block">
          <strong>Número de pasajeros actual:</strong> ${ship.passengers}<br>
          <strong>Número de empleados actual:</strong> ${ship.employees}
        </div>
        <div class="stats-block">
          <strong>Ubicación actual:</strong> ${ship.location}<br>
          <strong>Días en viaje:</strong> ${ship.days}<br>
          <strong>Distancia del viaje:</strong> ${ship.distance}
        </div>
      </div>
      <div class="flex-row">
        <div class="stats-block">
          <h3><strong>Costos totales</strong></h3><br>
          <strong>Total:</strong> ${ship.costs.total}<br>
          Distribución de costos por categorías y su cantidad<br>
          <canvas id="mainChart"></canvas>
        </div>
        <div class="stats-block">
          <h3><strong>Ganancias totales y reales</strong></h3><br>
          <strong>Total:</strong> ${ship.earnings.total}<br> 
          <strong>Real:</strong> ${ship.earnings.real}<br>
          Distribución de ganancias por categorías y su cantidad<br>
          <canvas id="secondaryChart"></canvas>
        </div>
      </div>
    </div>
  `;
  setTimeout(function() { renderSingleShipCharts(ship); }, 0);
}

function showSingleShip(shipId) {
  renderSingleShip(shipId);
}