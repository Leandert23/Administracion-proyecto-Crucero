// Sistema de validaciones optimizado

class ValidationSystem {
    constructor() {
        this.init();
    }
    
    init() {
        this.enableTooltips();
        this.preventDoubleSubmit();
        this.setupFieldValidations();
        this.setupAutoUpdate();
    }
    
    enableTooltips() {
        // Tooltips de Bootstrap optimizado
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    }
    
    preventDoubleSubmit() {
        // Prevenir doble envío optimizado
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.dataset.submitting === 'true') {
                e.preventDefault();
                return false;
            }
            
            form.dataset.submitting = 'true';
            this.disableSubmitButtons(form);
        });
    }
    
    disableSubmitButtons(form) {
        const buttons = form.querySelectorAll('button[type="submit"]');
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
        });
    }

    setupFieldValidations() {
        // Configurar validaciones de campos específicos
        this.setupPiscinaValidations();
        this.setupInventarioValidations();
        this.setupEquipoValidations();
        this.setupDateValidations();
        this.setupDeleteConfirmations();
    }
    
    setupPiscinaValidations() {
        const phInput = document.querySelector('input[name="ph"]');
        const cloroInput = document.querySelector('input[name="cloro_mg_l"]');
        
        if (phInput) {
            phInput.addEventListener('blur', () => this.validatePH(phInput));
        }
        if (cloroInput) {
            cloroInput.addEventListener('blur', () => this.validateCloro(cloroInput));
        }
    }
    
    setupInventarioValidations() {
        const stockInputs = document.querySelectorAll('input[name*="stock"]');
        stockInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateStock());
        });
    }
    
    setupEquipoValidations() {
        const codigoInput = document.querySelector('input[name="codigo"]');
        if (codigoInput) {
            codigoInput.addEventListener('input', (e) => {
                e.target.value = e.target.value.toUpperCase();
            });
            codigoInput.addEventListener('blur', () => this.validateCodigoEquipo(codigoInput));
        }
    }
    
    setupDateValidations() {
        const fechaInputs = document.querySelectorAll('input[type="datetime-local"], input[type="date"]');
        fechaInputs.forEach(input => {
            input.addEventListener('change', () => this.validateDate(input));
        });
    }
    
    setupDeleteConfirmations() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-danger, .btn-delete') || 
                e.target.closest('form')?.querySelector('button[type="submit"]')?.textContent.includes('Eliminar')) {
                if (!confirm('¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.')) {
                    e.preventDefault();
                }
            }
        });
    }
    
    setupAutoUpdate() {
        // Sistema de actualización automática optimizado
        if (window.location.pathname === '/') {
            this.startDashboardUpdates();
        } else if (window.location.pathname.includes('/piscinas/') && window.location.pathname.includes('/tendencias/')) {
            this.startPiscinaUpdates();
        }
    }
    
    startDashboardUpdates() {
        setInterval(() => {
            fetch('/api/dashboard-update/')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.updateDashboardCharts(data.data);
                        this.updateStats(data.data.stats);
                    }
                })
                .catch(console.error);
        }, 30000);
    }
    
    startPiscinaUpdates() {
        const piscinaId = window.location.pathname.split('/')[2];
        setInterval(() => {
            fetch(`/api/piscinas/${piscinaId}/update/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.updatePiscinaCharts(data.data);
                    }
                })
                .catch(console.error);
        }, 60000);
    }

    // Métodos de validación optimizados
    validatePH(input) {
        const value = parseFloat(input.value);
        if (isNaN(value)) return;
        
        const feedback = this.getOrCreateFeedback(input);
        this.clearValidationClasses(input, feedback);
        
        if (value < 0 || value > 14) {
            this.setValidationState(input, feedback, 'invalid', 'El pH debe estar entre 0 y 14');
        } else if (value < 6.8 || value > 8.2) {
            this.setValidationState(input, feedback, 'invalid', '⚠️ pH CRÍTICO: Requiere acción inmediata');
        } else if (value < 7.2 || value > 7.8) {
            this.setValidationState(input, feedback, 'warning', 'pH fuera del rango ideal (7.2-7.8)');
        } else {
            this.setValidationState(input, feedback, 'valid', 'pH en rango ideal ✓');
        }
    }
    
    validateCloro(input) {
        const value = parseFloat(input.value);
        if (isNaN(value)) return;
        
        const feedback = this.getOrCreateFeedback(input);
        this.clearValidationClasses(input, feedback);
        
        if (value < 0 || value > 10) {
            this.setValidationState(input, feedback, 'invalid', 'El cloro debe estar entre 0 y 10 mg/L');
        } else if (value < 0.5 || value > 5) {
            this.setValidationState(input, feedback, 'invalid', '⚠️ CLORO CRÍTICO: Requiere acción inmediata');
        } else if (value < 1 || value > 3) {
            this.setValidationState(input, feedback, 'warning', 'Cloro fuera del rango ideal (1-3 mg/L)');
        } else {
            this.setValidationState(input, feedback, 'valid', 'Cloro en rango ideal ✓');
        }
    }
    
    validateStock() {
        const stockActual = parseFloat(document.querySelector('input[name="stock_actual"]')?.value);
        const stockMinimo = parseFloat(document.querySelector('input[name="stock_minimo"]')?.value);
        
        if (!isNaN(stockActual) && !isNaN(stockMinimo) && stockActual <= stockMinimo) {
            this.showAlert('warning', `⚠️ Stock bajo: ${stockActual} ≤ ${stockMinimo}`);
        }
    }
    
    validateCodigoEquipo(input) {
        const pattern = /^[A-Z]{2,3}-[A-Z]{2,4}-\d{4}$/;
        const feedback = this.getOrCreateFeedback(input);
        
        if (!pattern.test(input.value)) {
            this.setValidationState(input, feedback, 'invalid', 'Formato: XX-XXXX-0000');
        } else {
            this.setValidationState(input, feedback, 'valid', 'Formato correcto ✓');
        }
    }
    
    validateDate(input) {
        const date = new Date(input.value);
        const now = new Date();
        const feedback = this.getOrCreateFeedback(input);
        
        if (date < now) {
            this.setValidationState(input, feedback, 'invalid', 'La fecha no puede estar en el pasado');
        } else {
            this.clearValidationClasses(input, feedback);
        }
    }
    
    // Métodos auxiliares optimizados
    getOrCreateFeedback(input) {
        let feedback = input.nextElementSibling;
        if (!feedback?.classList.contains('feedback')) {
            feedback = document.createElement('div');
            feedback.classList.add('feedback');
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        return feedback;
    }
    
    clearValidationClasses(input, feedback) {
        input.classList.remove('is-invalid', 'is-warning', 'is-valid');
        feedback.classList.remove('invalid-feedback', 'warning-feedback', 'valid-feedback');
    }
    
    setValidationState(input, feedback, state, message) {
        input.classList.add(`is-${state}`);
        feedback.classList.add(`${state}-feedback`);
        feedback.textContent = message;
        
        if (state === 'warning') {
            feedback.style.color = '#ff9800';
        }
    }
    
    showAlert(type, message) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        alert.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.body.appendChild(alert);
        
        setTimeout(() => alert.remove(), 5000);
    }
    
    updateDashboardCharts(data) {
        if (window.tareasChart && data.tareas_chart_data) {
            window.tareasChart.data.datasets[0].data = data.tareas_chart_data;
            window.tareasChart.update('none');
        }
        
        if (window.cruceroChart && data.preventivo_counts && data.correctivo_counts) {
            window.cruceroChart.data.datasets[0].data = data.preventivo_counts;
            window.cruceroChart.data.datasets[1].data = data.correctivo_counts;
            window.cruceroChart.update('none');
        }
    }
    
    updateStats(stats) {
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    updatePiscinaCharts(data) {
        if (window.phChart && data.fechas) {
            window.phChart.data.labels = data.fechas;
            window.phChart.data.datasets[0].data = data.ph_values;
            window.phChart.update('none');
        }
        
        if (window.cloroChart && data.fechas) {
            window.cloroChart.data.labels = data.fechas;
            window.cloroChart.data.datasets[0].data = data.cloro_values;
            window.cloroChart.update('none');
        }
    }
}

// Inicializar sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ValidationSystem();
});

// Validación en tiempo real optimizada
document.addEventListener('input', (e) => {
    if (e.target.type === 'number') {
        const min = parseFloat(e.target.min);
        const max = parseFloat(e.target.max);
        const value = parseFloat(e.target.value);
        
        if (!isNaN(min) && value < min) {
            e.target.setCustomValidity(`El valor mínimo es ${min}`);
        } else if (!isNaN(max) && value > max) {
            e.target.setCustomValidity(`El valor máximo es ${max}`);
        } else {
            e.target.setCustomValidity('');
        }
    }
});

// Indicadores de campos obligatorios
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[required], select[required], textarea[required]').forEach(field => {
        const label = document.querySelector(`label[for="${field.id}"]`);
        if (label && !label.innerHTML.includes('*')) {
            label.innerHTML += ' <span class="text-danger">*</span>';
        }
    });
});
