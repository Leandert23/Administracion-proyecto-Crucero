  var ships = [];
  // Inicializar el selector al cargar la página y obtener datos del backend
  document.addEventListener('DOMContentLoaded', function() {
    fetch('/administracion/api/cruceros-dashboard/')
      .then(function(response) { return response.json(); })
      .then(function(data) {
        ships = data.ships || [];
        renderShipList();
        const selector = document.getElementById('shipSelector');
        selector.addEventListener('change', function() {
          if (selector.value === 'all') {
            renderAllShips();
          } else {
            showSingleShip(Number(selector.value));
          }
        });
        renderAllShips();
      })
      .catch(function(error) {
        console.error('Error al obtener los datos de los cruceros:', error);
        ships = [];
        renderShipList();
        renderAllShips();
      });
  });

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
  // Alertas
  const allAlerts = ships.flatMap(s => s.alerts || []);
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
  dashboard.innerHTML =
    '<div class="dashboard-box" style="max-height: 100%;">' +
      '<div class="content-box">' +
        '<h1 class="dashboard-title">' + ship.name + '</h1>' +
        alertsHtml +
      '</div>' +
      '<h2>Estado: <strong>' + ship.status + '</strong> &nbsp;|&nbsp; Precio de la gasolina: <strong>' + (ship.gasPrice || 0) + '</strong></h2>' +
      '<h3>Presupuesto por parada para compras: ' + (ship.budget || 0) + '</h3>' +
      '<hr>' +
      '<div class="flex-row">' +
        '<div class="stats-block">' +
          '<strong>Número de pasajeros actual:</strong> ' + ship.passengers + '<br>' +
          '<strong>Número de empleados actual:</strong> ' + ship.employees +
        '</div>' +
        '<div class="stats-block">' +
          '<strong>Ubicación actual:</strong> ' + ship.location + '<br>' +
          '<strong>Días en viaje:</strong> ' + ship.days + '<br>' +
          '<strong>Distancia del viaje:</strong> ' + (ship.distance || 0) +
        '</div>' +
      '</div>' +
      '<div class="flex-row">' +
        '<div class="stats-block">' +
          '<h3><strong>Costos totales</strong></h3><br>' +
          '<strong>Total:</strong> ' + ((ship.costs && ship.costs.total) ? ship.costs.total : 0) + '<br>' +
          'Distribución de costos por categorías y su cantidad<br>' +
          '<canvas id="mainChart"></canvas>' +
        '</div>' +
        '<div class="stats-block">' +
          '<h3><strong>Ganancias totales y reales</strong></h3><br>' +
          '<strong>Total:</strong> ' + ((ship.earnings && ship.earnings.total) ? ship.earnings.total : 0) + '<br>' +
          '<strong>Real:</strong> ' + ((ship.earnings && ship.earnings.real) ? ship.earnings.real : 0) + '<br>' +
          'Distribución de ganancias por categorías y su cantidad<br>' +
          '<canvas id="secondaryChart"></canvas>' +
        '</div>' +
      '</div>' +
    '</div>';
  setTimeout(function() { renderSingleShipCharts(ship); }, 0);
}

function showSingleShip(shipId) {
  renderSingleShip(shipId);
}