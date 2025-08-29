/**
 * Sistema de Gestión de Horas - JavaScript Principal
 */

// Configuración global
const SisHoras = {
    config: {
        apiBase: '/api',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: 'HH:mm',
        hoursStep: 0.5,
        maxHoursPerDay: 12
    },
    
    // Estado global de la aplicación
    state: {
        currentUser: null,
        activePeriod: null,
        currentMonth: new Date().getMonth() + 1,
        currentYear: new Date().getFullYear(),
        projects: [],
        holidays: []
    }
};

// Utilidades generales
const Utils = {
    // Formatear fecha
    formatDate(date, format = 'DD/MM/YYYY') {
        if (!date) return '';
        const d = new Date(date);
        const day = d.getDate().toString().padStart(2, '0');
        const month = (d.getMonth() + 1).toString().padStart(2, '0');
        const year = d.getFullYear();
        
        switch (format) {
            case 'DD/MM/YYYY':
                return `${day}/${month}/${year}`;
            case 'YYYY-MM-DD':
                return `${year}-${month}-${day}`;
            case 'MM/DD/YYYY':
                return `${month}/${day}/${year}`;
            default:
                return `${day}/${month}/${year}`;
        }
    },
    
    // Formatear horas
    formatHours(hours) {
        return parseFloat(hours).toFixed(1) + 'h';
    },
    
    // Validar si es fin de semana
    isWeekend(date) {
        const d = new Date(date);
        return d.getDay() === 0 || d.getDay() === 6; // Domingo o Sábado
    },
    
    // Validar si es feriado
    isHoliday(date) {
        return SisHoras.state.holidays.some(holiday => holiday.fecha === date);
    },
    
    // Mostrar notificación
    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insertar en el contenedor de mensajes o crear uno temporal
        let container = document.querySelector('.messages-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'messages-container container mt-3';
            document.querySelector('main').prepend(container);
        }
        
        container.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            const alert = container.querySelector('.alert:last-child');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    },
    
    // Confirmar acción
    confirm(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    },
    
    // Debounce para búsquedas
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API Client
const API = {
    // Realizar petición HTTP
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(SisHoras.config.apiBase + url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API Error:', error);
            Utils.showNotification(`Error: ${error.message}`, 'error');
            throw error;
        }
    },
    
    // Obtener token CSRF
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    },
    
    // Métodos específicos de la API
    async getPeriods() {
        return await this.request('/periodos/');
    },
    
    async getActivePeriod() {
        return await this.request('/periodos/activo/');
    },
    
    async getProjects(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/proyectos/?${params}`);
    },
    
    async getActiveProjects() {
        return await this.request('/proyectos/activos/');
    },
    
    async getHours(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/horas/?${params}`);
    },
    
    async getHoursByDate(date) {
        return await this.request(`/horas/api/fecha/${date}/`);
    },
    
    async getDashboard() {
        return await this.request('/dashboard/');
    },
    
    async getCalendar(year, month) {
        return await this.request(`/calendario/${year}/${month}/`);
    },
    
    async getHolidays() {
        return await this.request('/feriados/');
    },
    
    // Crear registro de horas
    async createHour(data) {
        return await this.request('/horas/api/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // Actualizar registro de horas
    async updateHour(id, data) {
        return await this.request(`/horas/api/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // Eliminar registro de horas
    async deleteHour(id) {
        return await this.request(`/horas/api/${id}/`, {
            method: 'DELETE'
        });
    }
};

// Validaciones
const Validators = {
    // Validar horas
    validateHours(hours) {
        const h = parseFloat(hours);
        if (isNaN(h) || h < 0.5 || h > SisHoras.config.maxHoursPerDay) {
            return `Las horas deben estar entre 0.5 y ${SisHoras.config.maxHoursPerDay}`;
        }
        if (h % SisHoras.config.hoursStep !== 0) {
            return `Las horas deben ser múltiplos de ${SisHoras.config.hoursStep}`;
        }
        return null;
    },
    
    // Validar fecha
    validateDate(date) {
        if (!date) return 'La fecha es requerida';
        
        const d = new Date(date);
        if (isNaN(d.getTime())) return 'Fecha inválida';
        
        if (Utils.isWeekend(date)) {
            return 'No se pueden registrar horas en fines de semana';
        }
        
        if (Utils.isHoliday(date)) {
            return 'No se pueden registrar horas en días feriados';
        }
        
        return null;
    },
    
    // Validar proyecto
    validateProject(projectId) {
        if (!projectId) return 'Debe seleccionar un proyecto';
        return null;
    }
};

// Componentes UI
const UI = {
    // Inicializar componentes
    init() {
        this.initSliders();
        this.initDatePickers();
        this.initTooltips();
        this.initModals();
    },
    
    // Inicializar sliders de horas
    initSliders() {
        document.querySelectorAll('.hours-slider').forEach(slider => {
            const display = slider.nextElementSibling?.querySelector('.hours-display');
            
            slider.addEventListener('input', function() {
                const value = parseFloat(this.value).toFixed(1);
                if (display) {
                    display.textContent = value + 'h';
                }
            });
        });
    },
    
    // Inicializar date pickers
    initDatePickers() {
        document.querySelectorAll('input[type="date"]').forEach(input => {
            // Configurar fecha mínima y máxima si es necesario
            if (input.hasAttribute('data-min-date')) {
                input.min = input.getAttribute('data-min-date');
            }
            if (input.hasAttribute('data-max-date')) {
                input.max = input.getAttribute('data-max-date');
            }
        });
    },
    
    // Inicializar tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Inicializar modales
    initModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('hidden.bs.modal', function () {
                // Limpiar formularios al cerrar modales
                const forms = this.querySelectorAll('form');
                forms.forEach(form => form.reset());
            });
        });
    },
    
    // Mostrar loading
    showLoading(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
        }
    },
    
    // Ocultar loading
    hideLoading(element, content = '') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.innerHTML = content;
        }
    }
};

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes UI
    UI.init();
    
    // Cargar datos iniciales
    loadInitialData();
    
    // Configurar eventos globales
    setupGlobalEvents();
});

// Cargar datos iniciales
async function loadInitialData() {
    try {
        // Cargar período activo
        SisHoras.state.activePeriod = await API.getActivePeriod();
        
        // Cargar proyectos activos
        SisHoras.state.projects = await API.getActiveProjects();
        
        // Cargar feriados
        SisHoras.state.holidays = await API.getHolidays();
        
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
    }
}

// Configurar eventos globales
function setupGlobalEvents() {
    // Confirmar eliminaciones
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn-delete, .delete-btn')) {
            e.preventDefault();
            const message = e.target.getAttribute('data-confirm') || '¿Está seguro de eliminar este elemento?';
            Utils.confirm(message, () => {
                if (e.target.href) {
                    window.location.href = e.target.href;
                } else if (e.target.onclick) {
                    e.target.onclick();
                }
            });
        }
    });
    
    // Auto-guardar formularios (opcional)
    document.addEventListener('input', Utils.debounce(function(e) {
        if (e.target.hasAttribute('data-auto-save')) {
            // Implementar auto-guardado si es necesario
            console.log('Auto-save triggered for:', e.target.name);
        }
    }, 1000));
}

// Exportar para uso global
window.SisHoras = SisHoras;
window.Utils = Utils;
window.API = API;
window.Validators = Validators;
window.UI = UI;
