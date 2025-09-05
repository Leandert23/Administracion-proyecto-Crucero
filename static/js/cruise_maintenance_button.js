/**
 * Sistema de Botón Universal para Mantenimiento de Crucero
 * Permite a cualquier módulo solicitar mantenimiento específico
 */

class CruiseMaintenanceButton {
    constructor() {
        this.currentModule = this.detectCurrentModule();
        this.moduleConfigs = this.getModuleConfigurations();
        this.init();
    }

    /**
     * Detecta el módulo actual basado en la URL y contexto
     */
    detectCurrentModule() {
        const path = window.location.pathname;
        
        // Detectar por URL patterns
        if (path.includes('/mantenimiento') || path.includes('/maintenance')) {
            return 'mantenimiento';
        } else if (path.includes('/servicios-medicos') || path.includes('/medical')) {
            return 'servicios_medicos';
        } else if (path.includes('/almacen') || path.includes('/warehouse')) {
            return 'almacen';
        } else if (path.includes('/recursos-humanos') || path.includes('/hr')) {
            return 'recursos_humanos';
        } else if (path.includes('/ventas') || path.includes('/sales')) {
            return 'ventas';
        } else if (path.includes('/reservas') || path.includes('/reservations')) {
            return 'reservas';
        } else if (path.includes('/restaurante') || path.includes('/restaurant')) {
            return 'restaurante';
        } else if (path.includes('/bares') || path.includes('/bars')) {
            return 'bares';
        } else if (path.includes('/entretenimiento') || path.includes('/entertainment')) {
            return 'entretenimiento';
        } else if (path.includes('/compras') || path.includes('/purchases')) {
            return 'compras';
        }
        
        // Detectar por elementos del DOM (sidebar)
        const activeNavItem = document.querySelector('.nav-item.active .nav-text');
        if (activeNavItem) {
            const moduleName = activeNavItem.textContent.toLowerCase().trim();
            return this.normalizeModuleName(moduleName);
        }
        
        // Detectar por todos los elementos del sidebar
        const allNavItems = document.querySelectorAll('.nav-item .nav-text');
        for (let item of allNavItems) {
            const text = item.textContent.toLowerCase().trim();
            if (text.includes('mantenimiento')) return 'mantenimiento';
            if (text.includes('servicios médicos') || text.includes('servicios medicos')) return 'servicios_medicos';
            if (text.includes('almacén') || text.includes('almacen')) return 'almacen';
            if (text.includes('recursos humanos')) return 'recursos_humanos';
            if (text.includes('ventas')) return 'ventas';
            if (text.includes('reservas')) return 'reservas';
            if (text.includes('restaurante')) return 'restaurante';
            if (text.includes('bares')) return 'bares';
            if (text.includes('entretenimiento')) return 'entretenimiento';
            if (text.includes('compras')) return 'compras';
        }
        
        // Por defecto, mantenimiento
        return 'mantenimiento';
    }

    /**
     * Normaliza nombres de módulos
     */
    normalizeModuleName(name) {
        const mappings = {
            'mantenimiento': 'mantenimiento',
            'servicios medicos': 'servicios_medicos',
            'servicios médicos': 'servicios_medicos',
            'almacen': 'almacen',
            'almacén': 'almacen',
            'recursos humanos': 'recursos_humanos',
            'ventas': 'ventas',
            'reservas': 'reservas',
            'restaurante': 'restaurante',
            'bares': 'bares',
            'entretenimiento': 'entretenimiento',
            'compras': 'compras'
        };
        return mappings[name] || 'mantenimiento';
    }

    /**
     * Configuraciones específicas por módulo para mantenimiento de crucero
     */
    getModuleConfigurations() {
        return {
            mantenimiento: {
                name: 'Mantenimiento',
                icon: 'fas fa-tools',
                color: '#3b82f6',
                description: 'Sistema de mantenimiento de crucero',
                validations: {
                    canViewEquipment: true,
                    canCreateTasks: true,
                    canManageInventory: true,
                    canViewReports: true,
                    canManagePools: true,
                    canHandleIncidents: true,
                    canManageRequests: true
                },
                actions: [
                    { name: 'Ver Equipos', url: '/equipos/', icon: 'fas fa-cogs' },
                    { name: 'Crear Tarea', url: '/tareas/crear/', icon: 'fas fa-plus' },
                    { name: 'Ver Inventario', url: '/inventario/', icon: 'fas fa-boxes' },
                    { name: 'Reportar Incidente', url: '/incidentes/crear/', icon: 'fas fa-exclamation-triangle' },
                    { name: 'Ver Piscinas', url: '/piscinas/', icon: 'fas fa-swimming-pool' },
                    { name: 'Ver Reportes', url: '/reportes/', icon: 'fas fa-chart-bar' },
                    { name: 'Gestionar Solicitudes', url: '/gestionar-solicitudes/', icon: 'fas fa-clipboard-list' }
                ]
            },
            servicios_medicos: {
                name: 'Servicios Médicos',
                icon: 'fas fa-user-md',
                color: '#ef4444',
                description: 'Mantenimiento de equipos médicos del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewMedicalEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=servicios_medicos', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=servicios_medicos', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=servicios_medicos', icon: 'fas fa-clipboard-list' }
                ]
            },
            almacen: {
                name: 'Almacén',
                icon: 'fas fa-warehouse',
                color: '#f59e0b',
                description: 'Mantenimiento de equipos de almacén del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewWarehouseEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=almacen', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=almacen', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=almacen', icon: 'fas fa-clipboard-list' }
                ]
            },
            recursos_humanos: {
                name: 'Recursos Humanos',
                icon: 'fas fa-users-cog',
                color: '#8b5cf6',
                description: 'Mantenimiento de equipos de RRHH del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewHREquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=recursos_humanos', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=recursos_humanos', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=recursos_humanos', icon: 'fas fa-clipboard-list' }
                ]
            },
            ventas: {
                name: 'Ventas',
                icon: 'fas fa-shopping-bag',
                color: '#10b981',
                description: 'Mantenimiento de equipos de ventas del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewSalesEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=ventas', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=ventas', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=ventas', icon: 'fas fa-clipboard-list' }
                ]
            },
            reservas: {
                name: 'Reservas',
                icon: 'fas fa-calendar-check',
                color: '#06b6d4',
                description: 'Mantenimiento de equipos de reservas del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewReservationEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=reservas', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=reservas', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=reservas', icon: 'fas fa-clipboard-list' }
                ]
            },
            restaurante: {
                name: 'Restaurante',
                icon: 'fas fa-utensils',
                color: '#f97316',
                description: 'Mantenimiento de equipos de cocina del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewKitchenEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=restaurante', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=restaurante', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=restaurante', icon: 'fas fa-clipboard-list' }
                ]
            },
            bares: {
                name: 'Bares',
                icon: 'fas fa-cocktail',
                color: '#ec4899',
                description: 'Mantenimiento de equipos de bares del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewBarEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=bares', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=bares', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=bares', icon: 'fas fa-clipboard-list' }
                ]
            },
            entretenimiento: {
                name: 'Entretenimiento',
                icon: 'fas fa-music',
                color: '#84cc16',
                description: 'Mantenimiento de equipos de entretenimiento del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewEntertainmentEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=entretenimiento', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=entretenimiento', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=entretenimiento', icon: 'fas fa-clipboard-list' }
                ]
            },
            compras: {
                name: 'Compras',
                icon: 'fas fa-shopping-cart',
                color: '#6366f1',
                description: 'Mantenimiento de equipos de compras del crucero',
                validations: {
                    canRequestMaintenance: true,
                    canViewPurchaseEquipment: true
                },
                actions: [
                    { name: 'Mantenimiento Preventivo', url: '/solicitar-mantenimiento/preventivo/?modulo=compras', icon: 'fas fa-shield-alt' },
                    { name: 'Mantenimiento Correctivo', url: '/solicitar-mantenimiento/correctivo/?modulo=compras', icon: 'fas fa-wrench' },
                    { name: 'Mis Solicitudes', url: '/mis-solicitudes/?modulo=compras', icon: 'fas fa-clipboard-list' }
                ]
            }
        };
    }

    /**
     * Inicializa el botón
     */
    init() {
        this.createMaintenanceButton();
        this.setupEventListeners();
    }

    /**
     * Crea el botón de mantenimiento
     */
    createMaintenanceButton() {
        // Remover botón existente si existe
        const existingButton = document.getElementById('cruise-maintenance-button');
        if (existingButton) {
            existingButton.remove();
        }

        const config = this.moduleConfigs[this.currentModule];
        if (!config) return;

        const button = document.createElement('div');
        button.id = 'cruise-maintenance-button';
        button.className = 'cruise-maintenance-button';
        button.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: ${config.color};
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 20px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 200px;
            justify-content: center;
        `;

        button.innerHTML = `
            <i class="${config.icon}"></i>
            <span>Mantenimiento ${config.name}</span>
        `;

        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 6px 20px rgba(0,0,0,0.2)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        });

        button.addEventListener('click', () => {
            this.showMaintenanceModal();
        });

        document.body.appendChild(button);
    }

    /**
     * Muestra el modal de mantenimiento
     */
    showMaintenanceModal() {
        const config = this.moduleConfigs[this.currentModule];
        if (!config) return;

        // Remover modal existente
        const existingModal = document.getElementById('cruise-maintenance-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'cruise-maintenance-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            transform: translateY(-20px);
            transition: transform 0.3s ease;
        `;

        modalContent.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: ${config.color}; display: flex; align-items: center; gap: 8px;">
                    <i class="${config.icon}"></i>
                    Mantenimiento ${config.name}
                </h3>
                <button id="close-modal" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">&times;</button>
            </div>
            <p style="color: #666; margin-bottom: 20px;">${config.description}</p>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                ${config.actions.map(action => `
                    <a href="${action.url}" style="
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        padding: 12px 16px;
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        text-decoration: none;
                        color: #374151;
                        transition: all 0.2s ease;
                    " onmouseover="this.style.background='${config.color}'; this.style.color='white';" onmouseout="this.style.background='#f8fafc'; this.style.color='#374151';">
                        <i class="${action.icon}" style="color: ${config.color};"></i>
                        <span>${action.name}</span>
                    </a>
                `).join('')}
            </div>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Animar entrada
        setTimeout(() => {
            modal.style.opacity = '1';
            modalContent.style.transform = 'translateY(0)';
        }, 10);

        // Event listeners
        document.getElementById('close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    /**
     * Cierra el modal
     */
    closeModal() {
        const modal = document.getElementById('cruise-maintenance-modal');
        if (modal) {
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    }

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Escuchar cambios de URL
        window.addEventListener('popstate', () => {
            const newModule = this.detectCurrentModule();
            if (newModule !== this.currentModule) {
                this.currentModule = newModule;
                this.createMaintenanceButton();
            }
        });

        // Escuchar clics en enlaces de navegación
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nav-link')) {
                setTimeout(() => {
                    const newModule = this.detectCurrentModule();
                    if (newModule !== this.currentModule) {
                        this.currentModule = newModule;
                        this.createMaintenanceButton();
                    }
                }, 100);
            }
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.cruiseMaintenanceButton = new CruiseMaintenanceButton();
});

// También inicializar si el DOM ya está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.cruiseMaintenanceButton = new CruiseMaintenanceButton();
    });
} else {
    window.cruiseMaintenanceButton = new CruiseMaintenanceButton();
}
