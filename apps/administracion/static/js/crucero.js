var ships = [];
var purchaseRequests = [];
var selectedShipId = null;
let mainChart = null;
let secondaryChart = null;

// Función para generar colores dinámicamente para las gráficas
function generateColors(count) {
  const baseColors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1',
    '#14B8A6', '#F43F5E', '#8B5A2B', '#059669', '#DC2626'
  ];
  
  const colors = [];
  for (let i = 0; i < count; i++) {
    if (i < baseColors.length) {
      colors.push(baseColors[i]);
    } else {
      // Generar colores adicionales si necesitamos más
      const hue = (i * 137.5) % 360; // Usar ángulo dorado para distribución
      colors.push(`hsl(${hue}, 70%, 50%)`);
    }
  }
  return colors;
}

// Asegurar disponibilidad de getCsrfToken sin depender de otros archivos
if (typeof getCsrfToken === 'undefined') {
  function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }
}

// Inicializar el selector al cargar la página y obtener datos del contexto de Django
document.addEventListener('DOMContentLoaded', function() {
  // Obtener datos del contexto de Django (inyectados desde la plantilla)
  var contextData = window.djangoContext || {};

  // Adaptación al nuevo formato de views.py: datos planos del crucero actual
  // Preferir arreglo `ships`; si no existe, construir uno a partir de claves planas
  if (Array.isArray(contextData.ships) && contextData.ships.length > 0) {
    ships = contextData.ships;
  } else if (contextData && (typeof contextData.name !== 'undefined' || typeof contextData.status !== 'undefined')) {
    var shipObject = {
      id: typeof contextData.id !== 'undefined' ? Number(contextData.id) : 0,
      name: contextData.name || '',
      status: contextData.status || '',
      passengers: Number(contextData.passengers || 0),
      employees: {
        total: contextData.employees,
        status: {
          active_employees: 0,
          inactive_employees: 0,
          de_baja_employees: 0
        }
      },
      location: contextData.location || '',
      days: Number(contextData.days || 0),
      distance: Number(contextData.distance || 0),
      budget: Number(contextData.budget || 0),
      gasPrice: Number(contextData.gasPrice || 0),
      costs: contextData.costs || { total: 0, categories: {} },
      earnings: contextData.earnings || { total: 0, real: 0, categories: {} },
      alerts: Array.isArray(contextData.alerts) ? contextData.alerts : [],
      compras_por_tipo: Array.isArray(contextData.compras_por_tipo) ? contextData.compras_por_tipo : []
    };
    ships = [shipObject];
  } else {
    ships = [];
  }

  purchaseRequests = Array.isArray(contextData.purchase_requests) ? contextData.purchase_requests : [];

  // Determinar id inicial
  var initialShipId = (ships.length > 0 && typeof ships[0].id !== 'undefined') ? Number(ships[0].id) : null;
  if (initialShipId !== null && !Number.isNaN(initialShipId)) {
    renderSingleShip(initialShipId);
  }
});

function renderPurchaseRequests() {
  const container = document.getElementById("purchaseRequests");

  if (purchaseRequests.length === 0) {
    container.innerHTML = `
      <div class="dashboard-box">
        <h2 class="dashboard-title">Solicitudes de Compra</h2>
        <p>No hay solicitudes de compra pendientes</p>
      </div>
    `;
    return;
  }

  let requestsHtml = `
    <div class="dashboard-box">
      <h2 class="dashboard-title">Solicitudes de Compra</h2>
      <p>Gestiona las solicitudes de compra del módulo de compras</p>
    </div>
  `;

  purchaseRequests.forEach(function(request) {
    const statusClass = request.status === "approved" ? "approved" : 
      request.status === "rejected" ? "rejected" : "pending";

    requestsHtml += `
      <div class="purchase-request-card ${statusClass}">
        <div class="purchase-request-title">
          <h3 style="margin: 0; color: #1e293b;">${request.ship_name}</h3>
          <span class="purchase-request-date">
            ${request.created_at}
          </span>
        </div>
        <p class="purchase-request-info"><strong>Descripción:</strong> ${request.description}</p>
        <p class="purchase-request-info"><strong>Monto:</strong> $${request.amount.toLocaleString()}</p>
        
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
            <span class="purchase-status-text" style="background: ${request.status === "approved" ? 
                "#dcfce7; color: #166534" : "#fee2e2; color: #dc2626"};">
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
    
    // Enviar signal decision_solicitud para aprobar
    sendDecisionSignal(requestId, true, "Solicitud aprobada");
  }
}

function rejectPurchaseRequest(requestId, reason) {
  const request = purchaseRequests.find(function(r) { return r.id === requestId; });
  if (request) {
    // Validar que se proporcione una razón para el rechazo
    if (!reason || reason.trim() === '') {
      alert('Debe proporcionar una razón para rechazar la solicitud');
      return;
    }
    
    request.status = "rejected";
    request.rejection_reason = reason;
    renderPurchaseRequests();
    
    // Enviar signal decision_solicitud para rechazar
    sendDecisionSignal(requestId, false, reason.trim());
  }
}

function sendDecisionSignal(requestId, aceptado, mensaje) {
  // Crear un objeto FormData para enviar los datos
  const formData = new FormData();
  formData.append('id', requestId);
  formData.append('aceptado', aceptado);
  formData.append('mensaje', mensaje);
  formData.append('csrfmiddlewaretoken', getCsrfToken());
  
  // Enviar la signal usando fetch
  fetch('/administracion/decision-solicitud/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': getCsrfToken()
    }
  })
  .then(response => {
    if (response.ok) {
      console.log('Signal decision_solicitud enviada correctamente');
    } else {
      console.error('Error al enviar signal decision_solicitud');
    }
  })
  .catch(error => {
    console.error('Error de red al enviar signal decision_solicitud:', error);
  });
}

function renderModal(){
  const myModal = document.getElementById('myModal');
  const openModalBtn = document.getElementById('open-modal-btn');
  const closeModalBtn = document.getElementById('close-modal-btn');
  
  // Función para abrir el modal con animación
  function openModal() {
    myModal.style.display = 'flex';
    myModal.style.alignItems = 'center';
    myModal.style.justifyContent = 'center';
    
    // Cambiar color del modal basado en el número de alertas
    const modalContent = myModal.querySelector('.modal-content');
    if (alertas && alertas.length > 0) {
      modalContent.style.border = '3px solid #dc2626';
      modalContent.style.boxShadow = '0 0 20px rgba(220, 38, 38, 0.3)';
    } else {
      modalContent.style.border = '3px solid #10b981';
      modalContent.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.3)';
    }

    // Animación de entrada
    modalContent.style.transform = 'scale(0.8)';
    modalContent.style.opacity = '0';
    
    setTimeout(() => {
      modalContent.style.transition = 'all 0.3s ease';
      modalContent.style.transform = 'scale(1)';
      modalContent.style.opacity = '1';
    }, 10);
  }

  // Función para cerrar el modal con animación
  function closeModal() {
    const modalContent = myModal.querySelector('.modal-content');
    modalContent.style.transition = 'all 0.3s ease';
    modalContent.style.transform = 'scale(0.8)';
    modalContent.style.opacity = '0';
    
    setTimeout(() => {
      myModal.style.display = 'none';
    }, 300);
  }

  // Event listeners para los botones
  if (openModalBtn) {
    openModalBtn.addEventListener('click', openModal);
    
    // Efecto hover para el botón
    openModalBtn.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
      this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    });
    
    openModalBtn.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    });
  }

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeModal);
    
    // Efecto hover para el botón de cerrar
    closeModalBtn.addEventListener('mouseenter', function() {
      this.style.backgroundColor = 'rgba(255,255,255,0.2)';
    });
    
    closeModalBtn.addEventListener('mouseleave', function() {
      this.style.backgroundColor = 'transparent';
    });
  }

  // Cerrar el modal al hacer clic fuera de él
  if (myModal) {
    myModal.addEventListener('click', (event) => {
      if (event.target === myModal) {
        closeModal();
      }
    });
  }

  // Cerrar el modal con la tecla Escape
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && myModal.style.display === 'flex') {
      closeModal();
    }
  });
}

// Renderiza los gráficos de un solo barco
function renderSingleShipCharts(ship) {
  // Costos por tipo de proveedor (compras)
  const ctx1 = document.getElementById('mainChart').getContext('2d');
  if (mainChart) mainChart.destroy();
  
  // Usar datos de compras por tipo si están disponibles, sino usar categorías de costos
  let chartLabels, chartData, chartTitle;
  
  if (ship.compras_por_tipo && ship.compras_por_tipo.length > 0) {
    chartLabels = ship.compras_por_tipo.map(item => item.tipo_nombre);
    chartData = ship.compras_por_tipo.map(item => item.total);
    chartTitle = 'Costos por Tipo de Proveedor';
  } else {
    chartLabels = Object.keys(ship.costs?.categories || {});
    chartData = Object.values(ship.costs?.categories || {}).map(v => v || 0);
    chartTitle = 'Costos por Categoría';
  }
  
  // Generar colores dinámicamente para mejor visualización
  const colors = generateColors(chartLabels.length);
  
  mainChart = new Chart(ctx1, {
    type: 'pie',
    data: {
      labels: chartLabels,
      datasets: [{
        label: 'Costos',
        data: chartData,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { 
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true
          }
        },
        title: {
          display: true,
          text: chartTitle,
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

function renderSingleShip(shipId) {
  selectedShipId = shipId;
  const ship = ships.find(s => s.id === shipId || Number(s.id) === Number(shipId)) || ships[0];
  const dashboard = document.getElementById('dashboard');
  let alertsHtml = '';
  if (ship.alerts && ship.alerts.length > 0) {
    alertsHtml = '<div class="alerts">' + ship.alerts.map(function(a) {
      if (typeof a === 'string') { return '<div>' + a + '</div>'; }
      var mensaje = (a && a.mensaje) ? a.mensaje : '';
      var fecha = (a && a.fecha) ? a.fecha : '';
      return '<div><div>' + mensaje + '</div>' + (fecha ? '<small class="text-muted">' + fecha + '</small>' : '') + '</div>';
    }).join('') + '</div>';
  }

  let shipImage = "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&h=200&fit=crop";
  if (ship.status === "mantenimiento" || ship.status === "En mantenimiento") {
    shipImage = "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=400&h=200&fit=crop";
  } else if (ship.status === "inactivo" || ship.status === "Embarcado") {
    shipImage = "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=200&fit=crop";
  }

  dashboard.innerHTML = `
    <div class="dashboard-box" style="max-height: 100%;">
      <div style="background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('${shipImage}'); background-size: cover; background-position: center; border-radius: 12px; padding: 30px; margin-bottom: 20px; text-align: center;">
        <h1 style="color:white">Dasboard de ${ship.name}</h1>
      </div>
      <div class="content-box">
        <h1 style="color: white; font-size: 2em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">${ship.name}</h1>
        ${alertsHtml}
      </div>
      <h2>Estado: <strong>${ship.status}</strong> &nbsp;|&nbsp; Precio de la gasolina: <strong>${ship.gasPrice || 0}</strong></h2>
      <h3>Presupuesto por parada para compras: ${ship.budget || 0}</h3>
      <strong>Ubicación actual:</strong> ${ship.location}<br>
      <strong>Días en viaje:</strong> ${ship.days}<br>
      <strong>Distancia del viaje:</strong> ${ship.distance || 0}

      <hr>
      <div class="flex-row">
        <div class="stats-block">
          <strong>Número de pasajeros actual:</strong> ${ship.passengers}<br>
          <strong>Número de empleados actual:</strong> ${ship.employees.total}
        </div>
        <div class="stats-block">
          <strong>Número de empleados activos:</strong> ${ship.employees.status.active_employees}<br>
          <strong>Número de empleados inactivos:</strong> ${ship.employees.status.inactive_employees}<br>
          <strong>Número de empleados de baja:</strong> ${ship.employees.status.de_baja_employees}
        </div>
      </div>
      <div class="flex-row">
        <div class="stats-block">
          <h3><strong>Costos totales</strong></h3><br>
          <strong>Total:</strong> ${(ship.costs && ship.costs.total) ? ship.costs.total.toLocaleString() : 0}<br>
          Distribución de costos por categorías y su cantidad<br>
          <canvas id="mainChart"></canvas>
        </div>
        <div class="stats-block">
          <h3><strong>Ganancias totales y reales</strong></h3><br>
          <strong>Total:</strong> ${(ship.earnings && ship.earnings.total) ? ship.earnings.total.toLocaleString() : 0}<br>
          <strong>Real:</strong> ${(ship.earnings && ship.earnings.real) ? ship.earnings.real.toLocaleString() : 0}<br>
          Distribución de ganancias por categorías y su cantidad<br>
          <canvas id="secondaryChart"></canvas>
        </div>
      </div>
    </div>
  `;
  setTimeout(function() { renderSingleShipCharts(ship); }, 0);
}