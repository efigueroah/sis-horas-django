/**
 * JavaScript para el widget de horas personalizado
 */

class HoursWidget {
    constructor(input) {
        this.input = input;
        this.container = this.createContainer();
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.addFormatHints();
        this.addQuickExamples();
        this.validateOnLoad();
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.className = 'hours-field-container';
        
        // Envolver el input
        this.input.parentNode.insertBefore(container, this.input);
        container.appendChild(this.input);
        
        return container;
    }
    
    setupEventListeners() {
        // Validación en tiempo real
        this.input.addEventListener('input', (e) => {
            this.validateInput(e.target.value);
            this.showConversion(e.target.value);
        });
        
        // Validación al perder foco
        this.input.addEventListener('blur', (e) => {
            this.formatInput(e.target.value);
        });
        
        // Prevenir caracteres inválidos
        this.input.addEventListener('keypress', (e) => {
            this.filterKeypress(e);
        });
        
        // Autocompletar con Tab
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Tab' && this.input.value) {
                this.autoComplete();
            }
        });
    }
    
    addFormatHints() {
        const hints = document.createElement('div');
        hints.className = 'hours-format-hint';
        hints.innerHTML = `
            <span class="format-example decimal" data-example="1.5">Decimal: 1.5</span>
            <span class="format-example time" data-example="01:30">Tiempo: 01:30</span>
        `;
        
        this.container.appendChild(hints);
        
        // Event listeners para ejemplos
        hints.querySelectorAll('.format-example').forEach(example => {
            example.addEventListener('click', () => {
                this.input.value = example.dataset.example;
                this.input.focus();
                this.validateInput(this.input.value);
                this.showConversion(this.input.value);
            });
        });
    }
    
    addQuickExamples() {
        const examples = document.createElement('div');
        examples.className = 'quick-hours-examples';
        
        const commonHours = [
            { decimal: '0.5', time: '00:30', label: '30min' },
            { decimal: '1.0', time: '01:00', label: '1h' },
            { decimal: '1.5', time: '01:30', label: '1h30' },
            { decimal: '2.0', time: '02:00', label: '2h' },
            { decimal: '4.0', time: '04:00', label: '4h' },
            { decimal: '8.0', time: '08:00', label: '8h' }
        ];
        
        commonHours.forEach(hour => {
            const decimalBtn = document.createElement('button');
            decimalBtn.type = 'button';
            decimalBtn.className = 'quick-example decimal';
            decimalBtn.textContent = hour.decimal;
            decimalBtn.title = `${hour.label} (formato decimal)`;
            
            const timeBtn = document.createElement('button');
            timeBtn.type = 'button';
            timeBtn.className = 'quick-example time';
            timeBtn.textContent = hour.time;
            timeBtn.title = `${hour.label} (formato tiempo)`;
            
            [decimalBtn, timeBtn].forEach(btn => {
                btn.addEventListener('click', () => {
                    this.input.value = btn.textContent;
                    this.input.focus();
                    this.validateInput(this.input.value);
                    this.showConversion(this.input.value);
                });
            });
            
            examples.appendChild(decimalBtn);
            examples.appendChild(timeBtn);
        });
        
        this.container.appendChild(examples);
    }
    
    validateInput(value) {
        if (!value) {
            this.setValidationState('neutral');
            return;
        }
        
        const isValid = this.isValidFormat(value);
        this.setValidationState(isValid ? 'valid' : 'invalid');
        
        // Detectar formato
        if (this.isDecimalFormat(value)) {
            this.input.dataset.format = 'decimal';
        } else if (this.isTimeFormat(value)) {
            this.input.dataset.format = 'time';
        } else {
            delete this.input.dataset.format;
        }
    }
    
    showConversion(value) {
        let conversionDiv = this.container.querySelector('.hours-conversion');
        
        if (!conversionDiv) {
            conversionDiv = document.createElement('div');
            conversionDiv.className = 'hours-conversion';
            this.container.appendChild(conversionDiv);
        }
        
        if (!value || !this.isValidFormat(value)) {
            conversionDiv.classList.remove('show');
            return;
        }
        
        let conversionText = '';
        
        if (this.isDecimalFormat(value)) {
            const timeFormat = this.decimalToTime(parseFloat(value));
            conversionText = `💡 ${value} horas = ${timeFormat}`;
        } else if (this.isTimeFormat(value)) {
            const decimal = this.timeToDecimal(value);
            conversionText = `💡 ${value} = ${decimal} horas`;
        }
        
        if (conversionText) {
            conversionDiv.textContent = conversionText;
            conversionDiv.classList.add('show');
        } else {
            conversionDiv.classList.remove('show');
        }
    }
    
    formatInput(value) {
        if (!value || !this.isValidFormat(value)) return;
        
        // Auto-formatear tiempo a formato estándar
        if (this.isTimeFormat(value)) {
            const [hours, minutes] = value.split(':').map(Number);
            this.input.value = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        }
        
        // Auto-formatear decimal
        if (this.isDecimalFormat(value)) {
            const decimal = parseFloat(value);
            if (decimal === Math.floor(decimal)) {
                this.input.value = decimal.toFixed(1);
            }
        }
    }
    
    autoComplete() {
        const value = this.input.value.trim();
        
        // Auto-completar formato tiempo incompleto
        if (/^\d{1,2}$/.test(value)) {
            const hours = parseInt(value);
            if (hours >= 0 && hours <= 12) {
                this.input.value = `${hours.toString().padStart(2, '0')}:00`;
            }
        }
        
        // Auto-completar decimal incompleto
        if (/^\d+\.$/.test(value)) {
            this.input.value = value + '0';
        }
    }
    
    filterKeypress(e) {
        const char = e.key;
        const value = this.input.value;
        const cursorPos = this.input.selectionStart;
        
        // Permitir teclas de control
        if (e.ctrlKey || e.metaKey || ['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(char)) {
            return;
        }
        
        // Solo permitir dígitos, punto y dos puntos
        if (!/[\d.:]/.test(char)) {
            e.preventDefault();
            return;
        }
        
        // Validaciones específicas
        if (char === ':') {
            // Solo un : permitido y no al inicio
            if (value.includes(':') || cursorPos === 0) {
                e.preventDefault();
            }
        }
        
        if (char === '.') {
            // Solo un . permitido y no si ya hay :
            if (value.includes('.') || value.includes(':')) {
                e.preventDefault();
            }
        }
    }
    
    setValidationState(state) {
        this.input.classList.remove('is-valid', 'is-invalid');
        
        if (state === 'valid') {
            this.input.classList.add('is-valid');
        } else if (state === 'invalid') {
            this.input.classList.add('is-invalid');
        }
    }
    
    validateOnLoad() {
        if (this.input.value) {
            this.validateInput(this.input.value);
            this.showConversion(this.input.value);
        }
    }
    
    // Utilidades de formato
    isValidFormat(value) {
        return this.isDecimalFormat(value) || this.isTimeFormat(value);
    }
    
    isDecimalFormat(value) {
        return /^\d+(\.\d+)?$/.test(value) && parseFloat(value) >= 0.5 && parseFloat(value) <= 12;
    }
    
    isTimeFormat(value) {
        if (!/^\d{1,2}:\d{2}$/.test(value)) return false;
        
        const [hours, minutes] = value.split(':').map(Number);
        return hours >= 0 && hours <= 12 && minutes >= 0 && minutes <= 59;
    }
    
    decimalToTime(decimal) {
        const hours = Math.floor(decimal);
        const minutes = Math.round((decimal - hours) * 60);
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    }
    
    timeToDecimal(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return (hours + minutes / 60).toFixed(1);
    }
}

// Auto-inicializar widgets de horas
document.addEventListener('DOMContentLoaded', function() {
    const hoursInputs = document.querySelectorAll('.hours-input, input[name="horas"]');
    
    hoursInputs.forEach(input => {
        if (!input.hoursWidget) {
            input.hoursWidget = new HoursWidget(input);
        }
    });
});

// Exportar para uso global
window.HoursWidget = HoursWidget;
