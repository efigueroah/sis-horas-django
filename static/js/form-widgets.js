/**
 * Enhanced Form Widgets JavaScript
 * Mejoras para widgets de fecha, hora y otros elementos de formulario
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all form enhancements
    initDateInputs();
    initTimeInputs();
    initNumberInputs();
    initColorInputs();
    initQuickDateButtons();
    initFormValidation();
    initKeyboardShortcuts();
    
    /**
     * Mejoras para inputs de fecha
     */
    function initDateInputs() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        
        dateInputs.forEach(input => {
            // Agregar placeholder visual
            if (!input.value) {
                input.classList.add('empty-date');
            }
            
            // Manejar cambios de valor
            input.addEventListener('change', function() {
                if (this.value) {
                    this.classList.remove('empty-date');
                    this.classList.add('has-value');
                } else {
                    this.classList.add('empty-date');
                    this.classList.remove('has-value');
                }
                
                // Validar fecha
                validateDateInput(this);
            });
            
            // Manejar focus
            input.addEventListener('focus', function() {
                this.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.classList.remove('focused');
            });
        });
    }
    
    /**
     * Mejoras para inputs de hora
     */
    function initTimeInputs() {
        const timeInputs = document.querySelectorAll('input[type="time"]');
        
        timeInputs.forEach(input => {
            // Establecer formato de 24 horas
            input.setAttribute('step', '1800'); // 30 minutos
            
            input.addEventListener('change', function() {
                validateTimeInput(this);
            });
        });
    }
    
    /**
     * Mejoras para inputs numéricos
     */
    function initNumberInputs() {
        const numberInputs = document.querySelectorAll('input[type="number"]');
        
        numberInputs.forEach(input => {
            // Formatear números con decimales
            input.addEventListener('blur', function() {
                if (this.value && this.step && this.step.includes('.')) {
                    const decimals = this.step.split('.')[1].length;
                    this.value = parseFloat(this.value).toFixed(decimals);
                }
            });
            
            // Validar rangos
            input.addEventListener('input', function() {
                validateNumberInput(this);
            });
        });
    }
    
    /**
     * Mejoras para inputs de color
     */
    function initColorInputs() {
        const colorInputs = document.querySelectorAll('input[type="color"]');
        
        colorInputs.forEach(input => {
            // Crear preview del color
            const preview = document.createElement('div');
            preview.className = 'color-preview';
            preview.style.cssText = `
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 2px solid #dee2e6;
                display: inline-block;
                margin-left: 0.5rem;
                vertical-align: middle;
                background-color: ${input.value};
            `;
            
            input.parentNode.appendChild(preview);
            
            input.addEventListener('change', function() {
                preview.style.backgroundColor = this.value;
            });
        });
    }
    
    /**
     * Botones de fecha rápida
     */
    function initQuickDateButtons() {
        // Crear botones de fecha rápida para inputs de fecha
        const dateInputs = document.querySelectorAll('input[type="date"]');
        
        dateInputs.forEach(input => {
            if (input.dataset.quickButtons !== 'false') {
                createQuickDateButtons(input);
            }
        });
    }
    
    function createQuickDateButtons(input) {
        const container = document.createElement('div');
        container.className = 'quick-date-buttons mt-2';
        
        const buttons = [
            { label: 'Hoy', days: 0 },
            { label: 'Ayer', days: -1 },
            { label: 'Hace 1 semana', days: -7 },
            { label: 'Inicio del mes', days: 'month-start' }
        ];
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn btn-outline-secondary btn-sm';
            button.textContent = btn.label;
            
            button.addEventListener('click', function() {
                const today = new Date();
                let targetDate;
                
                if (btn.days === 'month-start') {
                    targetDate = new Date(today.getFullYear(), today.getMonth(), 1);
                } else {
                    targetDate = new Date(today);
                    targetDate.setDate(today.getDate() + btn.days);
                }
                
                input.value = targetDate.toISOString().split('T')[0];
                input.dispatchEvent(new Event('change'));
            });
            
            container.appendChild(button);
        });
        
        input.parentNode.insertBefore(container, input.nextSibling);
    }
    
    /**
     * Validación de formularios mejorada
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }
    
    function validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (!validateInput(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    function validateInput(input) {
        let isValid = true;
        
        // Limpiar errores previos
        input.classList.remove('is-invalid');
        const existingError = input.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Validar según el tipo
        switch (input.type) {
            case 'date':
                isValid = validateDateInput(input);
                break;
            case 'time':
                isValid = validateTimeInput(input);
                break;
            case 'number':
                isValid = validateNumberInput(input);
                break;
            case 'email':
                isValid = validateEmailInput(input);
                break;
        }
        
        return isValid;
    }
    
    function validateDateInput(input) {
        if (!input.value) return true; // Opcional
        
        const date = new Date(input.value);
        const today = new Date();
        
        // Validar fecha válida
        if (isNaN(date.getTime())) {
            showInputError(input, 'Fecha inválida');
            return false;
        }
        
        // Validar rango si está especificado
        if (input.min && date < new Date(input.min)) {
            showInputError(input, `La fecha no puede ser anterior a ${input.min}`);
            return false;
        }
        
        if (input.max && date > new Date(input.max)) {
            showInputError(input, `La fecha no puede ser posterior a ${input.max}`);
            return false;
        }
        
        return true;
    }
    
    function validateTimeInput(input) {
        if (!input.value) return true; // Opcional
        
        const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
        if (!timeRegex.test(input.value)) {
            showInputError(input, 'Formato de hora inválido');
            return false;
        }
        
        return true;
    }
    
    function validateNumberInput(input) {
        if (!input.value) return true; // Opcional
        
        const value = parseFloat(input.value);
        
        if (isNaN(value)) {
            showInputError(input, 'Debe ser un número válido');
            return false;
        }
        
        if (input.min && value < parseFloat(input.min)) {
            showInputError(input, `El valor mínimo es ${input.min}`);
            return false;
        }
        
        if (input.max && value > parseFloat(input.max)) {
            showInputError(input, `El valor máximo es ${input.max}`);
            return false;
        }
        
        if (input.step && input.step !== 'any') {
            const step = parseFloat(input.step);
            const min = parseFloat(input.min) || 0;
            if ((value - min) % step !== 0) {
                showInputError(input, `El valor debe ser múltiplo de ${step}`);
                return false;
            }
        }
        
        return true;
    }
    
    function validateEmailInput(input) {
        if (!input.value) return true; // Opcional
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value)) {
            showInputError(input, 'Formato de email inválido');
            return false;
        }
        
        return true;
    }
    
    function showInputError(input, message) {
        input.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
    }
    
    /**
     * Atajos de teclado para formularios
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + S para guardar
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const submitBtn = document.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
            
            // Escape para cancelar
            if (e.key === 'Escape') {
                const cancelBtn = document.querySelector('a[href*="list"], .btn-secondary');
                if (cancelBtn) {
                    cancelBtn.click();
                }
            }
        });
    }
    
    /**
     * Utilidades adicionales
     */
    
    // Formatear fechas para mostrar
    function formatDate(dateString, locale = 'es-ES') {
        const date = new Date(dateString);
        return date.toLocaleDateString(locale, {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    
    // Calcular diferencia entre fechas
    function dateDifference(date1, date2) {
        const d1 = new Date(date1);
        const d2 = new Date(date2);
        const diffTime = Math.abs(d2 - d1);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    }
    
    // Validar rango de fechas
    function validateDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (start >= end) {
            return {
                valid: false,
                message: 'La fecha de inicio debe ser anterior a la fecha de fin'
            };
        }
        
        const diffDays = dateDifference(startDate, endDate);
        if (diffDays > 365) {
            return {
                valid: false,
                message: 'El rango no puede ser mayor a 1 año'
            };
        }
        
        return { valid: true };
    }
    
    // Exponer utilidades globalmente
    window.FormWidgets = {
        formatDate,
        dateDifference,
        validateDateRange,
        validateInput,
        showInputError
    };
});

/**
 * Plugin para autocompletar fechas comunes
 */
(function() {
    const commonDates = {
        'hoy': () => new Date(),
        'ayer': () => {
            const date = new Date();
            date.setDate(date.getDate() - 1);
            return date;
        },
        'mañana': () => {
            const date = new Date();
            date.setDate(date.getDate() + 1);
            return date;
        },
        'lunes': () => {
            const date = new Date();
            const day = date.getDay();
            const diff = date.getDate() - day + (day === 0 ? -6 : 1);
            return new Date(date.setDate(diff));
        }
    };
    
    document.addEventListener('input', function(e) {
        if (e.target.type === 'date' && e.target.dataset.autocomplete !== 'false') {
            const value = e.target.value.toLowerCase();
            
            if (commonDates[value]) {
                const date = commonDates[value]();
                e.target.value = date.toISOString().split('T')[0];
                e.target.dispatchEvent(new Event('change'));
            }
        }
    });
})();
