// Ventas App JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize ventas app functionality
    initializeVentasApp();
});

function initializeVentasApp() {
    // Initialize form calculations for sale details
    initializeSaleCalculations();
    
    // Initialize client search functionality
    initializeClientSearch();
    
    // Initialize form validations
    initializeFormValidations();
}

// Sale calculations functionality
function initializeSaleCalculations() {
    const detallesContainer = document.getElementById('detalles-container');
    const addDetailBtn = document.getElementById('add-detail');
    const totalGeneral = document.getElementById('total-general');
    const montoTotalDisplay = document.getElementById('monto-total-display');
    
    if (!detallesContainer || !addDetailBtn) return;
    
    // Function to calculate subtotals
    function calcularSubtotal(row) {
        const cantidad = parseFloat(row.querySelector('[name*="cantidad"]').value) || 0;
        const precio = parseFloat(row.querySelector('[name*="precio_unitario"]').value) || 0;
        const subtotal = cantidad * precio;
        const subtotalDisplay = row.querySelector('.subtotal-display');
        if (subtotalDisplay) {
            subtotalDisplay.value = subtotal.toFixed(2);
        }
        return subtotal;
    }
    
    // Function to calculate total general
    function calcularTotalGeneral() {
        let total = 0;
        document.querySelectorAll('.detalle-row').forEach(row => {
            const deleteCheckbox = row.querySelector('[name*="DELETE"]');
            if (!deleteCheckbox || !deleteCheckbox.checked) {
                total += calcularSubtotal(row);
            }
        });
        
        if (totalGeneral) {
            totalGeneral.textContent = '$' + total.toFixed(2);
        }
        if (montoTotalDisplay) {
            montoTotalDisplay.value = total.toFixed(2);
        }
        return total;
    }
    
    // Event listeners for changes in quantity and price
    detallesContainer.addEventListener('input', function(e) {
        if (e.target.name.includes('cantidad') || e.target.name.includes('precio_unitario')) {
            const row = e.target.closest('.detalle-row');
            if (row) {
                calcularSubtotal(row);
                calcularTotalGeneral();
            }
        }
    });
    
    // Add new detail
    addDetailBtn.addEventListener('click', function() {
        const formCount = parseInt(document.getElementById('id_detalles-TOTAL_FORMS').value);
        const firstRow = document.querySelector('.detalle-row');
        if (!firstRow) return;
        
        const newRow = firstRow.cloneNode(true);
        
        // Update indices
        newRow.dataset.formIndex = formCount;
        newRow.querySelectorAll('input, select').forEach(input => {
            input.name = input.name.replace(/\d+/, formCount);
            input.id = input.id.replace(/\d+/, formCount);
            input.value = '';
        });
        
        // Clear values
        const subtotalDisplay = newRow.querySelector('.subtotal-display');
        if (subtotalDisplay) {
            subtotalDisplay.value = '0.00';
        }
        
        // Add remove button
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm remove-detail';
        removeBtn.title = 'Eliminar detalle';
        removeBtn.innerHTML = '<i class="fas fa-trash"></i>';
        removeBtn.addEventListener('click', function() {
            eliminarDetalle(newRow);
        });
        
        const buttonContainer = newRow.querySelector('.form-group:last-child');
        if (buttonContainer) {
            buttonContainer.appendChild(removeBtn);
        }
        
        // Add to container
        detallesContainer.appendChild(newRow);
        document.getElementById('id_detalles-TOTAL_FORMS').value = formCount + 1;
        
        // Recalculate totals
        calcularTotalGeneral();
    });
    
    // Remove detail
    function eliminarDetalle(row) {
        const deleteCheckbox = row.querySelector('[name*="DELETE"]');
        if (deleteCheckbox) {
            deleteCheckbox.checked = true;
        }
        row.style.display = 'none';
        calcularTotalGeneral();
    }
    
    // Event listeners for existing remove buttons
    document.querySelectorAll('.remove-detail').forEach(btn => {
        btn.addEventListener('click', function() {
            eliminarDetalle(this.closest('.detalle-row'));
        });
    });
    
    // Calculate initial totals
    calcularTotalGeneral();
}

// Client search functionality
function initializeClientSearch() {
    const searchInput = document.getElementById('q');
    if (!searchInput) return;
    
    // Add search suggestions or autocomplete if needed
    searchInput.addEventListener('input', function() {
        // Implement search suggestions here if needed
        console.log('Searching for:', this.value);
    });
}

// Form validations
function initializeFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

// Form validation function
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Este campo es obligatorio');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validate email fields
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Ingrese un email válido');
            isValid = false;
        }
    });
    
    // Validate numeric fields
    const numericFields = form.querySelectorAll('input[type="number"]');
    numericFields.forEach(field => {
        if (field.value && isNaN(field.value)) {
            showFieldError(field, 'Ingrese un número válido');
            isValid = false;
        }
    });
    
    return isValid;
}

// Helper functions
function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '5px';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#dc3545';
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '';
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Utility functions for the ventas app
window.VentasApp = {
    // Calculate total for a sale
    calculateSaleTotal: function() {
        let total = 0;
        document.querySelectorAll('.detalle-row').forEach(row => {
            const deleteCheckbox = row.querySelector('[name*="DELETE"]');
            if (!deleteCheckbox || !deleteCheckbox.checked) {
                const cantidad = parseFloat(row.querySelector('[name*="cantidad"]').value) || 0;
                const precio = parseFloat(row.querySelector('[name*="precio_unitario"]').value) || 0;
                total += cantidad * precio;
            }
        });
        return total;
    },
    
    // Format currency
    formatCurrency: function(amount) {
        return '$' + parseFloat(amount).toFixed(2);
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        // Implement notification system here
        console.log(`${type.toUpperCase()}: ${message}`);
    }
};
