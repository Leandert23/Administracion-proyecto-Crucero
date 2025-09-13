var totalCostos = 0;
var costosPorCrucero = [];
var totalGanancias = 0;
var gananciasPorCrucero = [];
var ubicacionesCruceros = [];
var alertas = [];
var conteoCrucerosPorEstado = {};

function getCsrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
}

// Variables globales para los graficos
let mainChart = null;

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

