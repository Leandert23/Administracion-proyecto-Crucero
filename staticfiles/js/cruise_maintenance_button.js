/**
 * SISTEMA UNIVERSAL DE BOTÓN PARA GESTIÓN DE TAREAS - CRUCERO
 * Permite a cualquier módulo crear tareas directamente en el sistema de mantenimiento
 */

class UniversalTaskButton {
    constructor() {
        this.currentModule = this.detectCurrentModule();
        this.taskQueue = [];
        this.isProcessing = false;
        this.apiBaseUrl = '/api/tasks/';
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
     * Verifica si el botón debe mostrarse en la página actual
     */
    shouldShowButton() {
        const path = window.location.pathname;
        const currentModule = this.detectCurrentModule();
        
        // Páginas donde NO mostrar el botón
        const hiddenPages = [
            '/tareas/crear/',  // Página de crear tareas
            '/tareas/',        // Lista de tareas
            '/admin/',         // Panel de administración
            '/login/',         // Página de login
            '/logout/'         // Página de logout
        ];
        
        // Verificar si estamos en una página donde no mostrar el botón
        for (const hiddenPage of hiddenPages) {
            if (path.includes(hiddenPage)) {
                console.log(`🚫 Botón oculto en página: ${path}`);
                return false;
            }
        }
        
        // Módulos donde NO mostrar el botón
        const hiddenModules = [
            'mantenimiento'  // No mostrar en el módulo de mantenimiento
        ];
        
        if (hiddenModules.includes(currentModule)) {
            console.log(`🚫 Botón oculto en módulo: ${currentModule}`);
            return false;
        }
        
        // Verificar si hay un atributo data-hide-button en el body
        const body = document.body;
        if (body && body.getAttribute('data-hide-button') === 'true') {
            console.log('🚫 Botón oculto por atributo data-hide-button');
            return false;
        }
        
        console.log(`✅ Botón visible en módulo: ${currentModule}, página: ${path}`);
        return true;
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
     * Inicializa el botón universal
     */
    init() {
        // Verificar si debe mostrar el botón
        if (this.shouldShowButton()) {
            this.createUniversalButton();
            this.setupEventListeners();
            this.setupTaskQueueProcessor();
            console.log(`🚀 UniversalTaskButton inicializado para módulo: ${this.currentModule}`);
            
            // Función de debug para detectar superposiciones
            this.debugOverlaps();
        } else {
            console.log(`🚫 UniversalTaskButton no se mostrará en esta página/módulo`);
        }
    }

    /**
     * Detecta otros elementos flotantes para evitar superposiciones
     */
    detectFloatingElements() {
        const floatingElements = [];
        
        // Buscar elementos específicos que comúnmente causan superposiciones
        const commonFloatingSelectors = [
            '.floating-button',
            '.fixed-button',
            '.bottom-right-button',
            '.chat-button',
            '.help-button',
            '.support-button',
            '.feedback-button',
            '.green-message',
            '.notification',
            '.alert',
            '.toast',
            '[style*="position: fixed"]',
            '[style*="position: absolute"]'
        ];
        
        // Buscar por selectores específicos primero
        commonFloatingSelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    const rect = element.getBoundingClientRect();
                    if (rect.bottom > window.innerHeight - 200 && rect.right > window.innerWidth - 300) {
                        const style = window.getComputedStyle(element);
                        floatingElements.push({
                            element: element,
                            rect: rect,
                            zIndex: parseInt(style.zIndex) || 0,
                            selector: selector
                        });
                    }
                });
            } catch (e) {
                // Ignorar selectores inválidos
            }
        });
        
        // Buscar elementos con position fixed o absolute que puedan estar en la esquina inferior derecha
        const allElements = document.querySelectorAll('*');
        
        allElements.forEach(element => {
            // Evitar procesar nuestro propio botón
            if (element.id === 'universal-task-button' || element.classList.contains('universal-task-button')) {
                return;
            }
            
            const style = window.getComputedStyle(element);
            const rect = element.getBoundingClientRect();
            
            // Verificar si es un elemento flotante en la esquina inferior derecha
            if ((style.position === 'fixed' || style.position === 'absolute') &&
                rect.bottom > window.innerHeight - 200 && // Cerca del fondo
                rect.right > window.innerWidth - 300 && // Cerca del lado derecho
                rect.width > 50 && rect.height > 20) { // Tamaño mínimo para ser considerado
                
                // Verificar si ya está en la lista
                const alreadyExists = floatingElements.some(item => item.element === element);
                if (!alreadyExists) {
                    floatingElements.push({
                        element: element,
                        rect: rect,
                        zIndex: parseInt(style.zIndex) || 0,
                        selector: 'auto-detected'
                    });
                }
            }
        });
        
        return floatingElements.sort((a, b) => b.zIndex - a.zIndex);
    }

    /**
     * Calcula la posición óptima para el botón (justo arriba del mensaje verde)
     */
    calculateOptimalPosition() {
        const floatingElements = this.detectFloatingElements();
        const baseBottom = 30;
        const baseRight = 30;
        let adjustedBottom = baseBottom;
        let adjustedRight = baseRight;
        
        console.log('🔍 Elementos flotantes detectados:', floatingElements.length);
        
        // Buscar específicamente el mensaje verde (elemento más bajo)
        let greenMessageBottom = 0;
        let greenMessageHeight = 0;
        let greenMessageElement = null;
        
        floatingElements.forEach((floating, index) => {
            const elementHeight = floating.rect.height;
            const elementWidth = floating.rect.width;
            const elementBottom = window.innerHeight - floating.rect.bottom;
            const elementRight = window.innerWidth - floating.rect.right;
            
            console.log(`📦 Elemento ${index + 1}:`, {
                selector: floating.selector,
                height: elementHeight,
                width: elementWidth,
                bottom: elementBottom,
                right: elementRight,
                zIndex: floating.zIndex
            });
            
            // Si el elemento está en el área donde queremos colocar nuestro botón
            if (elementBottom < 200 && floating.rect.right > window.innerWidth - 300) {
                // Verificar si es un elemento verde (por color de fondo o clase)
                const style = window.getComputedStyle(floating.element);
                const backgroundColor = style.backgroundColor;
                const isGreen = backgroundColor.includes('rgb(16, 185, 129)') || // #10b981
                               backgroundColor.includes('rgb(34, 197, 94)') ||  // #22c55e
                               backgroundColor.includes('rgb(22, 163, 74)') ||  // #16a34a
                               backgroundColor.includes('green') ||
                               floating.selector.includes('green') ||
                               floating.element.classList.contains('green') ||
                               floating.element.classList.contains('success');
                
                // Encontrar el elemento más bajo (mensaje verde)
                if (elementBottom > greenMessageBottom) {
                    greenMessageBottom = elementBottom;
                    greenMessageHeight = elementHeight;
                    greenMessageElement = floating.element;
                    
                    if (isGreen) {
                        console.log('🟢 Elemento verde detectado:', {
                            selector: floating.selector,
                            backgroundColor: backgroundColor,
                            bottom: elementBottom,
                            height: elementHeight
                        });
                    }
                }
            }
        });
        
        // Si encontramos el mensaje verde, posicionar justo arriba
        if (greenMessageBottom > 0) {
            adjustedBottom = greenMessageBottom + greenMessageHeight + 15; // 15px de separación
            adjustedRight = baseRight; // Mantener alineación horizontal
            console.log('📍 Posicionando justo arriba del mensaje verde:', {
                greenMessageBottom: greenMessageBottom,
                greenMessageHeight: greenMessageHeight,
                adjustedBottom: adjustedBottom
            });
        } else {
            // Si no hay mensaje verde, usar posición por defecto
            adjustedBottom = baseBottom;
            adjustedRight = baseRight;
        }
        
        // Asegurar que no se salga de la pantalla
        const maxBottom = window.innerHeight - 100; // Dejar margen
        const maxRight = window.innerWidth - 100; // Dejar margen
        
        adjustedBottom = Math.min(adjustedBottom, maxBottom);
        adjustedRight = Math.min(adjustedRight, maxRight);
        
        console.log('📍 Posición calculada:', {
            bottom: adjustedBottom,
            right: adjustedRight
        });
        
        return {
            bottom: adjustedBottom,
            right: adjustedRight
        };
    }

    /**
     * Crea el botón universal de tareas
     */
    createUniversalButton() {
        // Remover botón existente si existe
        const existingButton = document.getElementById('universal-task-button');
        if (existingButton) {
            existingButton.remove();
        }

        const moduleConfig = this.getModuleConfig(this.currentModule);
        const position = this.calculateOptimalPosition();

        const button = document.createElement('div');
        button.id = 'universal-task-button';
        button.className = 'universal-task-button';
        button.style.cssText = `
            position: fixed;
            bottom: ${position.bottom}px;
            right: ${position.right}px;
            z-index: 10000;
            background: ${moduleConfig.color};
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 18px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 160px;
            justify-content: center;
            transform: scale(0.9);
        `;

        button.innerHTML = `
            <i class="${moduleConfig.icon}"></i>
            <span>Crear Tarea</span>
            <span id="task-count" style="display: none; background: rgba(255,255,255,0.2); border-radius: 50%; padding: 2px 8px; font-size: 12px;">0</span>
        `;

        // Efectos hover - crecer suavemente
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px) scale(1.1)';
            button.style.boxShadow = '0 8px 25px rgba(0,0,0,0.3)';
            button.style.padding = '14px 22px';
            button.style.fontSize = '14px';
            button.style.minWidth = '180px';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0) scale(0.9)';
            button.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
            button.style.padding = '12px 18px';
            button.style.fontSize = '13px';
            button.style.minWidth = '160px';
        });

        button.addEventListener('click', () => {
            this.showTaskCreationModal();
        });

        document.body.appendChild(button);

        // Actualizar contador de tareas pendientes
        this.updateTaskCount();
    }

    /**
     * Obtiene configuración del módulo actual
     */
    getModuleConfig(module) {
        const configs = {
            mantenimiento: { name: 'Mantenimiento', icon: 'fas fa-tools', color: '#3b82f6' },
            servicios_medicos: { name: 'Servicios Médicos', icon: 'fas fa-user-md', color: '#ef4444' },
            almacen: { name: 'Almacén', icon: 'fas fa-warehouse', color: '#f59e0b' },
            recursos_humanos: { name: 'RRHH', icon: 'fas fa-users-cog', color: '#8b5cf6' },
            ventas: { name: 'Ventas', icon: 'fas fa-shopping-bag', color: '#10b981' },
            reservas: { name: 'Reservas', icon: 'fas fa-calendar-check', color: '#06b6d4' },
            restaurante: { name: 'Restaurante', icon: 'fas fa-utensils', color: '#f97316' },
            bares: { name: 'Bares', icon: 'fas fa-cocktail', color: '#ec4899' },
            entretenimiento: { name: 'Entretenimiento', icon: 'fas fa-music', color: '#84cc16' },
            compras: { name: 'Compras', icon: 'fas fa-shopping-cart', color: '#6366f1' }
        };
        return configs[module] || configs.mantenimiento;
    }

    /**
     * Muestra modal para crear tarea
     */
    showTaskCreationModal() {
        const moduleConfig = this.getModuleConfig(this.currentModule);

        // Remover modal existente
        const existingModal = document.getElementById('task-creation-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'task-creation-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 16px;
            padding: 32px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            transform: translateY(-20px) scale(0.95);
            transition: transform 0.3s ease;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        `;

        modalContent.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: ${moduleConfig.color}; display: flex; align-items: center; justify-content: center;">
                        <i class="${moduleConfig.icon}" style="color: white; font-size: 20px;"></i>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #1f2937; font-size: 20px; font-weight: 600;">
                            Crear Tarea - ${moduleConfig.name}
                        </h3>
                        <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">
                            Esta tarea será enviada al departamento de mantenimiento
                        </p>
                    </div>
                </div>
                <button id="close-task-modal" style="background: none; border: none; font-size: 28px; cursor: pointer; color: #9ca3af; padding: 4px; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.background='#f3f4f6'; this.style.color='#374151';" onmouseout="this.style.background='none'; this.style.color='#9ca3af';">&times;</button>
            </div>

            <form id="task-creation-form">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                        <i class="fas fa-heading" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                        Título de la tarea *
                    </label>
                    <input type="text" id="task-title" required
                        style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.2s;"
                        placeholder="Ej: Reparar equipo de refrigeración"
                        onfocus="this.style.borderColor='${moduleConfig.color}';"
                        onblur="this.style.borderColor='#e5e7eb';">
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                        <i class="fas fa-align-left" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                        Descripción detallada *
                    </label>
                    <textarea id="task-description" required rows="4"
                        style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; resize: vertical; transition: border-color 0.2s;"
                        placeholder="Describe detalladamente qué necesita mantenimiento y por qué..."
                        onfocus="this.style.borderColor='${moduleConfig.color}';"
                        onblur="this.style.borderColor='#e5e7eb';"></textarea>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                    <div>
                        <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                            <i class="fas fa-exclamation-triangle" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                            Prioridad
                        </label>
                        <select id="task-priority"
                            style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.2s;"
                            onfocus="this.style.borderColor='${moduleConfig.color}';"
                            onblur="this.style.borderColor='#e5e7eb';">
                            <option value="baja">Baja</option>
                            <option value="media" selected>Media</option>
                            <option value="alta">Alta</option>
                            <option value="critica">Crítica</option>
                            <option value="emergencia">Emergencia</option>
                        </select>
                    </div>

                    <div>
                        <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                            <i class="fas fa-tools" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                            Tipo
                        </label>
                        <select id="task-type"
                            style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.2s;"
                            onfocus="this.style.borderColor='${moduleConfig.color}';"
                            onblur="this.style.borderColor='#e5e7eb';">
                            <option value="correctivo" selected>Mantenimiento Correctivo</option>
                            <option value="preventivo">Mantenimiento Preventivo</option>
                            <option value="emergencia">Emergencia</option>
                            <option value="inspeccion">Inspección</option>
                            <option value="limpieza">Limpieza</option>
                            <option value="reparacion">Reparación</option>
                        </select>
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                        <i class="fas fa-map-marker-alt" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                        Ubicación específica
                    </label>
                    <input type="text" id="task-location"
                        style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.2s;"
                        placeholder="Ej: Cubierta 5 - Cocina Principal"
                        onfocus="this.style.borderColor='${moduleConfig.color}';"
                        onblur="this.style.borderColor='#e5e7eb';">
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                        <i class="fas fa-cogs" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                        Equipo afectado
                    </label>
                    <input type="text" id="task-equipment"
                        style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.2s;"
                        placeholder="Ej: Refrigerador industrial, Equipo médico..."
                        onfocus="this.style.borderColor='${moduleConfig.color}';"
                        onblur="this.style.borderColor='#e5e7eb';">
                </div>

                <div style="margin-bottom: 24px;">
                    <label style="display: block; font-weight: 500; color: #374151; margin-bottom: 8px;">
                        <i class="fas fa-clock" style="margin-right: 8px; color: ${moduleConfig.color};"></i>
                        Tiempo estimado (horas)
                    </label>
                    <input type="number" id="task-time" min="0.5" max="24" step="0.5" value="1.0"
                        style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; transition: border-color 0.2s;"
                        onfocus="this.style.borderColor='${moduleConfig.color}';"
                        onblur="this.style.borderColor='#e5e7eb';">
                </div>

                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button type="button" id="cancel-task-btn"
                        style="padding: 12px 24px; border: 2px solid #d1d5db; background: white; color: #6b7280; border-radius: 8px; font-weight: 500; cursor: pointer; transition: all 0.2s;"
                        onmouseover="this.style.borderColor='#9ca3af'; this.style.color='#374151';"
                        onmouseout="this.style.borderColor='#d1d5db'; this.style.color='#6b7280';">
                        Cancelar
                    </button>
                    <button type="submit" id="submit-task-btn"
                        style="padding: 12px 24px; border: none; background: ${moduleConfig.color}; color: white; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px;"
                        onmouseover="this.style.background='${this.darkenColor(moduleConfig.color)}'; this.style.transform='translateY(-1px)';"
                        onmouseout="this.style.background='${moduleConfig.color}'; this.style.transform='translateY(0)';">
                        <i class="fas fa-paper-plane"></i>
                        <span>Enviar a Mantenimiento</span>
                    </button>
                </div>
            </form>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Animar entrada
        setTimeout(() => {
            modal.style.opacity = '1';
            modalContent.style.transform = 'translateY(0) scale(1)';
        }, 10);

        // Event listeners
        document.getElementById('close-task-modal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('cancel-task-btn').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('task-creation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitTask();
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
     * Oscurece un color para efectos hover
     */
    darkenColor(color) {
        // Función simple para oscurecer colores hex
        if (color.startsWith('#')) {
            const hex = color.substring(1);
            const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - 40);
            const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - 40);
            const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - 40);
            return `rgb(${r}, ${g}, ${b})`;
        }
        return color;
    }

    /**
     * Envía la tarea al sistema de mantenimiento
     */
    async submitTask() {
        const formData = {
            titulo: document.getElementById('task-title').value.trim(),
            descripcion: document.getElementById('task-description').value.trim(),
            prioridad: document.getElementById('task-priority').value,
            tipo: document.getElementById('task-type').value,
            ubicacion_solicitud: document.getElementById('task-location').value.trim(),
            equipo_afectado: document.getElementById('task-equipment').value.trim(),
            tiempo_estimado: document.getElementById('task-time').value,
            modulo_origen: this.currentModule,
            origen_url: window.location.href
        };

        // Validación básica
        if (!formData.titulo || !formData.descripcion) {
            this.showNotification('Por favor complete título y descripción', 'error');
            return;
        }

        // Mostrar loading
        const submitBtn = document.getElementById('submit-task-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Enviando...</span>';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/tasks/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('✅ Tarea enviada exitosamente a mantenimiento', 'success');
                this.closeModal();
                this.updateTaskCount();
                // Recargar página para mostrar cambios si es necesario
                setTimeout(() => window.location.reload(), 2000);
            } else {
                throw new Error(result.error || 'Error al enviar tarea');
            }
        } catch (error) {
            console.error('Error al enviar tarea:', error);
            this.showNotification('❌ Error al enviar tarea: ' + error.message, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Obtiene el token CSRF
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /**
     * Muestra notificaciones
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 16px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10002;
            max-width: 400px;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Animar entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Auto-remover
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    /**
     * Actualiza el contador de tareas pendientes
     */
    async updateTaskCount() {
        try {
            const response = await fetch('/api/tasks/count/');
            const data = await response.json();
            const countElement = document.getElementById('task-count');

            if (countElement && data.count > 0) {
                countElement.textContent = data.count;
                countElement.style.display = 'inline';
            } else if (countElement) {
                countElement.style.display = 'none';
            }
        } catch (error) {
            console.warn('Error al actualizar contador de tareas:', error);
        }
    }

    /**
     * Cierra el modal
     */
    closeModal() {
        const modal = document.getElementById('task-creation-modal');
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
                // Verificar si debe mostrar el botón en la nueva página
                if (this.shouldShowButton()) {
                    this.createUniversalButton();
                } else {
                    // Remover botón si no debe mostrarse
                    const existingButton = document.getElementById('universal-task-button');
                    if (existingButton) {
                        existingButton.remove();
                    }
                }
            }
        });

        // Escuchar clics en enlaces de navegación
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nav-link')) {
                setTimeout(() => {
                    const newModule = this.detectCurrentModule();
                    if (newModule !== this.currentModule) {
                        this.currentModule = newModule;
                        // Verificar si debe mostrar el botón en la nueva página
                        if (this.shouldShowButton()) {
                            this.createUniversalButton();
                        } else {
                            // Remover botón si no debe mostrarse
                            const existingButton = document.getElementById('universal-task-button');
                            if (existingButton) {
                                existingButton.remove();
                            }
                        }
                    }
                }, 100);
            }
        });

        // Escuchar cambios de visibilidad para actualizar contador
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.updateTaskCount();
            }
        });

        // Escuchar cambios de tamaño de ventana para reajustar posición
        window.addEventListener('resize', () => {
            setTimeout(() => {
                this.createUniversalButton();
            }, 100);
        });

        // Escuchar cambios en el DOM para detectar nuevos elementos flotantes
        const observer = new MutationObserver(() => {
            setTimeout(() => {
                this.createUniversalButton();
            }, 500);
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });
    }

    /**
     * Función de debug para detectar superposiciones
     */
    debugOverlaps() {
        setTimeout(() => {
            const ourButton = document.getElementById('universal-task-button');
            if (!ourButton) return;
            
            const ourRect = ourButton.getBoundingClientRect();
            const floatingElements = this.detectFloatingElements();
            
            console.log('🔍 DEBUG - Verificando superposiciones:');
            console.log('📍 Nuestro botón:', {
                id: ourButton.id,
                bottom: ourRect.bottom,
                right: ourRect.right,
                width: ourRect.width,
                height: ourRect.height
            });
            
            floatingElements.forEach((element, index) => {
                const rect = element.rect;
                const overlaps = !(ourRect.right < rect.left || 
                                 ourRect.left > rect.right || 
                                 ourRect.bottom < rect.top || 
                                 ourRect.top > rect.bottom);
                
                console.log(`📦 Elemento ${index + 1} (${element.selector}):`, {
                    overlaps: overlaps,
                    bottom: rect.bottom,
                    right: rect.right,
                    width: rect.width,
                    height: rect.height,
                    zIndex: element.zIndex
                });
                
                if (overlaps) {
                    console.warn(`⚠️ SUPERPOSICIÓN DETECTADA con elemento: ${element.selector}`);
                }
            });
        }, 1000);
    }

    /**
     * Oculta el botón manualmente
     */
    hideButton() {
        const existingButton = document.getElementById('universal-task-button');
        if (existingButton) {
            existingButton.remove();
            console.log('🚫 Botón oculto manualmente');
        }
    }

    /**
     * Muestra el botón manualmente (si debe mostrarse)
     */
    showButton() {
        if (this.shouldShowButton()) {
            this.createUniversalButton();
            console.log('✅ Botón mostrado manualmente');
        } else {
            console.log('🚫 No se puede mostrar el botón en esta página/módulo');
        }
    }

    /**
     * Configura el procesador de cola de tareas
     */
    setupTaskQueueProcessor() {
        // Procesar tareas pendientes cada 30 segundos
        setInterval(() => {
            if (!this.isProcessing && this.taskQueue.length > 0) {
                this.processTaskQueue();
            }
        }, 30000);
    }

    /**
     * Procesa la cola de tareas pendientes
     */
    async processTaskQueue() {
        if (this.isProcessing || this.taskQueue.length === 0) return;

        this.isProcessing = true;

        try {
            while (this.taskQueue.length > 0) {
                const task = this.taskQueue.shift();
                await this.submitTaskToAPI(task);
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Envía tarea a la API
     */
    async submitTaskToAPI(taskData) {
        try {
            const response = await fetch('/api/tasks/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(taskData)
            });

            const result = await response.json();

            if (result.success) {
                console.log('✅ Tarea procesada exitosamente:', result.task_id);
            } else {
                console.error('❌ Error al procesar tarea:', result.error);
                // Re-enviar a la cola si falla
                this.taskQueue.unshift(taskData);
            }
        } catch (error) {
            console.error('❌ Error de red al procesar tarea:', error);
            // Re-enviar a la cola si falla
            this.taskQueue.unshift(taskData);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.universalTaskButton = new UniversalTaskButton();
    
    // Funciones globales para control manual
    window.hideTaskButton = () => {
        if (window.universalTaskButton) {
            window.universalTaskButton.hideButton();
        }
    };
    
    window.showTaskButton = () => {
        if (window.universalTaskButton) {
            window.universalTaskButton.showButton();
        }
    };
    
    window.toggleTaskButton = () => {
        if (window.universalTaskButton) {
            const existingButton = document.getElementById('universal-task-button');
            if (existingButton) {
                window.universalTaskButton.hideButton();
            } else {
                window.universalTaskButton.showButton();
            }
        }
    };
});

// También inicializar si el DOM ya está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.universalTaskButton = new UniversalTaskButton();
        
        // Funciones globales para control manual
        window.hideTaskButton = () => {
            if (window.universalTaskButton) {
                window.universalTaskButton.hideButton();
            }
        };
        
        window.showTaskButton = () => {
            if (window.universalTaskButton) {
                window.universalTaskButton.showButton();
            }
        };
        
        window.toggleTaskButton = () => {
            if (window.universalTaskButton) {
                const existingButton = document.getElementById('universal-task-button');
                if (existingButton) {
                    window.universalTaskButton.hideButton();
                } else {
                    window.universalTaskButton.showButton();
                }
            }
        };
    });
} else {
    window.universalTaskButton = new UniversalTaskButton();
    
    // Funciones globales para control manual
    window.hideTaskButton = () => {
        if (window.universalTaskButton) {
            window.universalTaskButton.hideButton();
        }
    };
    
    window.showTaskButton = () => {
        if (window.universalTaskButton) {
            window.universalTaskButton.showButton();
        }
    };
    
    window.toggleTaskButton = () => {
        if (window.universalTaskButton) {
            const existingButton = document.getElementById('universal-task-button');
            if (existingButton) {
                window.universalTaskButton.hideButton();
            } else {
                window.universalTaskButton.showButton();
            }
        }
    };
}
