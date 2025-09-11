var totalCostos = 0;
var costosPorCrucero = [];
var totalGanancias = 0;
var gananciasPorCrucero = [];
var ubicacionesCruceros = [];
var alertas = [];
var conteoCrucerosPorEstado = {};

// Inicializar el selector al cargar la página y obtener datos del contexto de Django
document.addEventListener('DOMContentLoaded', function() {
  // Obtener datos del contexto de Django
  const contextData = window.djangoContext || {};
  
  totalCostos = contextData.total_costos || 0;
  costosPorCrucero = contextData.costos_por_crucero || [];
  totalGanancias = contextData.total_ganancias || 0;
  gananciasPorCrucero = contextData.ganancias_por_crucero || [];
  ubicacionesCruceros = contextData.ubicaciones_cruceros || [];
  alertas = contextData.alertas || [];
  conteoCrucerosPorEstado = contextData.conteo_cruceros_por_estado || {};
  
  renderAllShips();
});

function getCsrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
}

// Variables globales para los graficos
let mainChart = null;

// Renderiza el dashboard de todos los barcos
function renderAllShips() {
  const dashboard = document.getElementById('dashboard');
  // Usar datos del contexto de Django
  const active = conteoCrucerosPorEstado.activo || 0;
  const inactive = conteoCrucerosPorEstado.inactivo || 0;
  const maintenance = conteoCrucerosPorEstado.mantenimiento || 0;
  const viaje = conteoCrucerosPorEstado.viaje || 0;
  const totalCosts = totalCostos;
  const totalEarnings = totalGanancias;
  const realEarnings = totalGanancias - totalCostos; 

  // Procesar alertas del contexto
  let alertsHtml = '';
  let numberAlerts = '';
  if (alertas && alertas.length > 0) {
    alertsHtml = `
      <div>
        <h3 style="color: #dc2626; margin-bottom: 15px; text-align: center;">
          <i class="fas fa-exclamation-triangle"></i> Alertas del Sistema
        </h3>
        <div>
          ${alertas.map(a => `
            <div class="alert-item" style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 8px 0; border-radius: 4px;">
              <div style="font-weight: bold; color: #92400e; margin-bottom: 4px;">
                ${a.crucero__nombre || 'Sistema'}
              </div>
              <div style="color: #78350f; margin-bottom: 4px;">
                ${a.mensaje}
              </div>
              <small style="color: #a16207;">
                <i class="fas fa-clock"></i> ${new Date(a.fecha).toLocaleDateString('es-ES', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </small>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    numberAlerts = `<span style="background: #dc2626; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px; margin-left: 5px;">${alertas.length}</span>`;
  } else {
    alertsHtml = `
      <div class="no-alerts" style="text-align: center; padding: 40px; color: #6b7280;">
        <i class="fas fa-check-circle" style="font-size: 48px; color: #10b981; margin-bottom: 16px;"></i>
        <h3 style="color: #374151; margin-bottom: 8px;">¡Todo en orden!</h3>
        <p>No hay alertas pendientes en el sistema.</p>
      </div>
    `;
  }
  
  // Procesar ubicaciones de cruceros
  const shipsLocations = ubicacionesCruceros.map((crucero, index) => {
    if (index % 2 === 0) {
      return `<span>${crucero.puerto_base}, </span>`;
    } else {
      return `<span>${crucero.puerto_base}</span><br>`;
    }
  }).join('');
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
            <li>🌊 Barcos en viaje: ${viaje}</li>
          </ul>
        </div>
        <button id="open-modal-btn" class="open-modal-btn" style="background: #dc2626; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s ease;">
          <i class="fas fa-bell"></i> Ver Alertas${numberAlerts}
        </button>
        <div id="myModal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); backdrop-filter: blur(2px);" class="modal-overlay">
          <div class="modal-content" style="background-color: white; margin: 5% auto; padding: 0; border-radius: 12px; width: 80%; max-width: 600px; max-height: 80vh; overflow-y: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative;">
            <div style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 20px; border-radius: 12px 12px 0 0; position: relative;">
              <h2 style="margin: 0; font-size: 24px; text-align: center;">
                <i class="fas fa-exclamation-triangle"></i> Centro de Alertas
              </h2>
              <button id="close-modal-btn" class="close-button" style="position: absolute; top: 15px; right: 20px; background: none; border: none; color: white; font-size: 28px; cursor: pointer; padding: 0; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: background-color 0.3s ease;">&times;</button>
            </div>
            <div style="padding: 20px;">
              ${alertsHtml}
            </div>
          </div>
        </div>
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

function renderModal(){
  const myModal = document.getElementById('myModal');
  const openModalBtn = document.getElementById('open-modal-btn');
  const closeModalBtn = document.getElementById('close-modal-btn');
  
  // Función para abrir el modal con animación
  function openModal() {
    myModal.style.display = 'flex';
    myModal.style.alignItems = 'center';
    myModal.style.justifyContent = 'center';
    
    // Animación de entrada
    const modalContent = myModal.querySelector('.modal-content');
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

// Renderiza los gráficos de todos los barcos
function renderAllShipsCharts() {
  const ctx = document.getElementById('mainChart').getContext('2d');
  if (mainChart) mainChart.destroy();
  
  // Crear datos para el gráfico usando ubicacionesCruceros
  const chartLabels = ubicacionesCruceros.map(crucero => `${crucero.nombre} (${crucero.estado_operativo})`);
  const chartCosts = costosPorCrucero;
  const chartEarnings = gananciasPorCrucero;
  
  mainChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartLabels,
      datasets: [
        {
          label: 'Costos totales',
          data: chartCosts,
          backgroundColor: '#b3dafe',
        },
        {
          label: 'Ganancias totales',
          data: chartEarnings,
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

