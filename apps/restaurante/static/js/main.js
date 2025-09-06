// CSRF Token handling for Django
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

const csrftoken = getCookie('csrftoken');

// Global AJAX setup
const ajaxSetup = {
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
    }
};

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
    
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    messagesContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(container, mainContent.firstChild);
    return container;
}

// Form validation
function validateForm(formData, requiredFields) {
    for (const field of requiredFields) {
        if (!formData.get(field) || formData.get(field).trim() === '') {
            showAlert(`El campo ${field} es requerido`, 'error');
            return false;
        }
    }
    return true;
}

// Number validation
function validatePositiveNumber(value, fieldName) {
    const num = parseFloat(value);
    if (isNaN(num) || num < 0) {
        showAlert(`${fieldName} debe ser un número positivo`, 'error');
        return false;
    }
    return true;
}

function validateInteger(value, fieldName) {
    const num = parseInt(value);
    if (isNaN(num) || num < 0 || !Number.isInteger(parseFloat(value))) {
        showAlert(`${fieldName} debe ser un número entero positivo`, 'error');
        return false;
    }
    return true;
}

// Stock management functions
function updateMenuItems(restaurantId) {
    if (!restaurantId) return;
    
    const itemSelect = document.getElementById('consumptionItem');
    if (!itemSelect) return;
    
    // Show loading state
    itemSelect.innerHTML = '<option value="">Cargando...</option>';
    itemSelect.disabled = true;
    
    fetch(`/ajax/get-menu-items/?restaurant_id=${restaurantId}`)
        .then(response => response.json())
        .then(data => {
            itemSelect.innerHTML = '<option value="">Seleccionar Item</option>';
            data.items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = `${item.name} (Stock: ${item.quantity})`;
                option.dataset.stock = item.quantity;
                option.dataset.price = item.price;
                option.dataset.included = item.included;
                itemSelect.appendChild(option);
            });
            itemSelect.disabled = false;
        })
        .catch(error => {
            console.error('Error fetching menu items:', error);
            showAlert('Error al cargar los items del menú', 'error');
            itemSelect.innerHTML = '<option value="">Error al cargar items</option>';
            itemSelect.disabled = false;
        });
}

// Consumption validation
function validateConsumption(menuItemId, quantity) {
    const select = document.getElementById('consumptionItem');
    const selectedOption = select.querySelector(`option[value="${menuItemId}"]`);
    
    if (!selectedOption) {
        showAlert('Por favor seleccione un item válido', 'error');
        return false;
    }
    
    const availableStock = parseInt(selectedOption.dataset.stock);
    const requestedQuantity = parseInt(quantity);
    
    if (requestedQuantity > availableStock) {
        showAlert(`Stock insuficiente. Solo hay ${availableStock} unidades disponibles`, 'error');
        return false;
    }
    
    return true;
}

// Loading state management
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Generic data submission function
function submitData(url, data, successMessage, form = null) {
    const submitButton = form ? form.querySelector('button[type="submit"]') : null;
    
    if (submitButton) {
        setLoadingState(submitButton, true);
    }
    
    return fetch(url, {
        method: 'POST',
        headers: ajaxSetup.headers,
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(responseData => {
        if (responseData.success) {
            showAlert(successMessage || responseData.message, 'success');
            if (form) {
                form.reset();
                // Trigger any necessary updates
                const event = new Event('formReset');
                form.dispatchEvent(event);
            }
            return responseData;
        } else {
            throw new Error(responseData.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error: ' + error.message, 'error');
        throw error;
    })
    .finally(() => {
        if (submitButton) {
            setLoadingState(submitButton, false);
        }
    });
}

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Restaurant selection change handler
    const restaurantSelects = document.querySelectorAll('select[name="restaurant"], #restaurantSelect, #consumptionRestaurant');
    restaurantSelects.forEach(select => {
        select.addEventListener('change', function() {
            updateMenuItems(this.value);
        });
    });
    
    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[type="number"]');
    quantityInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
                showAlert('La cantidad no puede ser negativa', 'error');
            }
            
            // Prevent decimal values for quantity fields
            if (this.name === 'quantity' && this.value.includes('.')) {
                this.value = Math.floor(this.value);
                showAlert('La cantidad debe ser un número entero', 'error');
            }
        });
        
        // Prevent negative values on keydown
        input.addEventListener('keydown', function(e) {
            if (e.key === '-' || e.key === 'e' || e.key === 'E') {
                e.preventDefault();
            }
        });
    });
    
    // Form submission handlers
    const forms = document.querySelectorAll('form[id]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    });
    
    // Auto-hide alerts after some time
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => {
        setTimeout(() => {
            alert.remove();
        }, 5000);
    });
});

// Generic form submission handler
function handleFormSubmission(form) {
    const formData = new FormData(form);
    const formId = form.id;
    
    // Form-specific validation and processing
    switch(formId) {
        case 'addItemForm':
            handleAddItemForm(formData, form);
            break;
        case 'addEmployeeForm':
            handleAddEmployeeForm(formData, form);
            break;
        case 'addMaintenanceForm':
            handleAddMaintenanceForm(formData, form);
            break;
        case 'consumptionForm':
            handleConsumptionForm(formData, form);
            break;
        default:
            console.log('Unknown form:', formId);
    }
}

function handleAddItemForm(formData, form) {
    if (!validateForm(formData, ['name', 'restaurant_id', 'quantity'])) return;
    if (!validateInteger(formData.get('quantity'), 'Cantidad')) return;
    
    const price = formData.get('price');
    if (price && !validatePositiveNumber(price, 'Precio')) return;
    
    const data = {
        name: formData.get('name'),
        restaurant_id: formData.get('restaurant_id'),
        quantity: formData.get('quantity'),
        price: formData.get('price') || 0,
        included: formData.get('included') === 'true',
        description: formData.get('description') || ''
    };
    
    submitData('/ajax/add-item/', data, 'Item agregado exitosamente', form)
        .then(() => {
            // Reload page to show new item
            setTimeout(() => location.reload(), 1000);
        })
        .catch(() => {});
}

function handleAddEmployeeForm(formData, form) {
    if (!validateForm(formData, ['name', 'position', 'shift', 'restaurant_id'])) return;
    
    const data = {
        name: formData.get('name'),
        position: formData.get('position'),
        shift: formData.get('shift'),
        restaurant_id: formData.get('restaurant_id'),
        phone: formData.get('phone') || '',
        email: formData.get('email') || ''
    };
    
    submitData('/ajax/add-employee/', data, 'Empleado agregado exitosamente', form)
        .then(() => {
            // Reload page to show new employee
            setTimeout(() => location.reload(), 1000);
        })
        .catch(() => {});
}

function handleAddMaintenanceForm(formData, form) {
    if (!validateForm(formData, ['area', 'description', 'priority', 'restaurant_id'])) return;
    
    const data = {
        area: formData.get('area'),
        description: formData.get('description'),
        priority: formData.get('priority'),
        restaurant_id: formData.get('restaurant_id'),
        reported_by: formData.get('reported_by') || 'Sistema'
    };
    
    submitData('/ajax/add-maintenance/', data, 'Problema de mantenimiento reportado exitosamente', form)
        .then(() => {
            // Reload page to show new maintenance item
            setTimeout(() => location.reload(), 1000);
        })
        .catch(() => {});
}

function handleConsumptionForm(formData, form) {
    if (!validateForm(formData, ['menu_item_id', 'cruise_day', 'quantity'])) return;
    if (!validateInteger(formData.get('quantity'), 'Cantidad')) return;
    
    const menuItemId = formData.get('menu_item_id');
    const quantity = formData.get('quantity');
    
    if (!validateConsumption(menuItemId, quantity)) return;
    
    const data = {
        menu_item_id: menuItemId,
        cruise_day: formData.get('cruise_day'),
        quantity: quantity
    };
    
    submitData('/ajax/register-consumption/', data, 'Consumo registrado exitosamente', form)
        .then((responseData) => {
            // Update stock display
            const select = document.getElementById('consumptionItem');
            const selectedOption = select.querySelector(`option[value="${menuItemId}"]`);
            if (selectedOption) {
                selectedOption.dataset.stock = responseData.new_stock;
                selectedOption.textContent = selectedOption.textContent.replace(/Stock: \\d+/, `Stock: ${responseData.new_stock}`);
                
                // Update item info display
                const stockDisplay = document.getElementById('availableStock');
                if (stockDisplay) {
                    stockDisplay.textContent = responseData.new_stock;
                }
            }
            
            // Hide item info
            const itemInfo = document.getElementById('itemInfo');
            if (itemInfo) {
                itemInfo.style.display = 'none';
            }
        })
        .catch(() => {});
}

// Utility function for confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Export functions for global use
window.restaurantApp = {
    showAlert,
    validateForm,
    validatePositiveNumber,
    validateInteger,
    updateMenuItems,
    validateConsumption,
    submitData,
    confirmAction
};
