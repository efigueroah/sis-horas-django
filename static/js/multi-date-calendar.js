/**
 * Widget de Calendario para Selección Múltiple de Fechas
 * Permite seleccionar múltiples fechas de forma visual e intuitiva
 */

class MultiDateCalendar {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.selectedDates = new Set();
        this.currentDate = new Date();
        this.options = {
            minDate: options.minDate || null,
            maxDate: options.maxDate || null,
            disabledDates: options.disabledDates || [],
            disableWeekends: options.disableWeekends || false,
            disableHolidays: options.disableHolidays || false,
            holidays: options.holidays || [],
            onDateSelect: options.onDateSelect || null,
            onDateDeselect: options.onDateDeselect || null,
            onChange: options.onChange || null,
            locale: options.locale || 'es-ES'
        };
        
        this.monthNames = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        
        this.dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        
        this.init();
    }
    
    init() {
        this.container.innerHTML = this.createCalendarHTML();
        this.bindEvents();
        this.render();
    }
    
    createCalendarHTML() {
        return `
            <div class="multi-date-calendar">
                <div class="calendar-header">
                    <button type="button" class="btn btn-sm btn-outline-secondary" id="prevMonth">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <h6 class="calendar-title mb-0" id="calendarTitle"></h6>
                    <button type="button" class="btn btn-sm btn-outline-secondary" id="nextMonth">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                <div class="calendar-grid">
                    <div class="calendar-days-header">
                        ${this.dayNames.map(day => `<div class="day-header">${day}</div>`).join('')}
                    </div>
                    <div class="calendar-days" id="calendarDays"></div>
                </div>
                <div class="calendar-footer">
                    <div class="selected-count">
                        <small class="text-muted">
                            <i class="fas fa-calendar-check me-1"></i>
                            <span id="selectedCount">0</span> fechas seleccionadas
                        </small>
                    </div>
                    <div class="calendar-actions">
                        <button type="button" class="btn btn-sm btn-outline-danger" id="clearAll">
                            <i class="fas fa-times me-1"></i>Limpiar Todo
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info" id="selectWeekdays">
                            <i class="fas fa-business-time me-1"></i>Días Laborales
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Navegación de meses
        this.container.querySelector('#prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.render();
        });
        
        this.container.querySelector('#nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.render();
        });
        
        // Acciones rápidas
        this.container.querySelector('#clearAll').addEventListener('click', () => {
            this.clearAllDates();
        });
        
        this.container.querySelector('#selectWeekdays').addEventListener('click', () => {
            this.selectWeekdaysInMonth();
        });
        
        // Delegación de eventos para días del calendario
        this.container.querySelector('#calendarDays').addEventListener('click', (e) => {
            if (e.target.classList.contains('calendar-day') && !e.target.classList.contains('disabled')) {
                const dateStr = e.target.dataset.date;
                this.toggleDate(dateStr);
            }
        });
    }
    
    render() {
        this.renderTitle();
        this.renderDays();
        this.updateSelectedCount();
    }
    
    renderTitle() {
        const title = `${this.monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
        this.container.querySelector('#calendarTitle').textContent = title;
    }
    
    renderDays() {
        const daysContainer = this.container.querySelector('#calendarDays');
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Primer día del mes y último día del mes
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // Días del mes anterior para completar la primera semana
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        // Generar 42 días (6 semanas)
        let html = '';
        const currentDate = new Date(startDate);
        
        for (let i = 0; i < 42; i++) {
            const dateStr = this.formatDate(currentDate);
            const isCurrentMonth = currentDate.getMonth() === month;
            const isToday = this.isToday(currentDate);
            const isSelected = this.selectedDates.has(dateStr);
            const isDisabled = this.isDateDisabled(currentDate);
            const isWeekend = currentDate.getDay() === 0 || currentDate.getDay() === 6;
            const isHoliday = this.isHoliday(currentDate);
            
            let classes = ['calendar-day'];
            if (!isCurrentMonth) classes.push('other-month');
            if (isToday) classes.push('today');
            if (isSelected) classes.push('selected');
            if (isDisabled) classes.push('disabled');
            if (isWeekend) classes.push('weekend');
            if (isHoliday) classes.push('holiday');
            
            html += `
                <div class="${classes.join(' ')}" 
                     data-date="${dateStr}"
                     title="${this.getDateTitle(currentDate, isHoliday, isWeekend)}">
                    <span class="day-number">${currentDate.getDate()}</span>
                    ${isSelected ? '<i class="fas fa-check selected-icon"></i>' : ''}
                    ${isHoliday ? '<i class="fas fa-star holiday-icon"></i>' : ''}
                </div>
            `;
            
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        daysContainer.innerHTML = html;
    }
    
    toggleDate(dateStr) {
        if (this.selectedDates.has(dateStr)) {
            this.selectedDates.delete(dateStr);
            if (this.options.onDateDeselect) {
                this.options.onDateDeselect(dateStr);
            }
        } else {
            this.selectedDates.add(dateStr);
            if (this.options.onDateSelect) {
                this.options.onDateSelect(dateStr);
            }
        }
        
        this.render();
        
        if (this.options.onChange) {
            this.options.onChange(Array.from(this.selectedDates));
        }
    }
    
    clearAllDates() {
        this.selectedDates.clear();
        this.render();
        
        if (this.options.onChange) {
            this.options.onChange([]);
        }
    }
    
    selectWeekdaysInMonth() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const lastDay = new Date(year, month + 1, 0).getDate();
        
        for (let day = 1; day <= lastDay; day++) {
            const date = new Date(year, month, day);
            const dayOfWeek = date.getDay();
            
            // Solo días laborales (lunes a viernes)
            if (dayOfWeek >= 1 && dayOfWeek <= 5 && !this.isDateDisabled(date)) {
                const dateStr = this.formatDate(date);
                this.selectedDates.add(dateStr);
            }
        }
        
        this.render();
        
        if (this.options.onChange) {
            this.options.onChange(Array.from(this.selectedDates));
        }
    }
    
    isDateDisabled(date) {
        // Verificar fecha mínima
        if (this.options.minDate && date < this.options.minDate) {
            return true;
        }
        
        // Verificar fecha máxima
        if (this.options.maxDate && date > this.options.maxDate) {
            return true;
        }
        
        // Verificar fines de semana
        if (this.options.disableWeekends && (date.getDay() === 0 || date.getDay() === 6)) {
            return true;
        }
        
        // Verificar fechas deshabilitadas específicas
        const dateStr = this.formatDate(date);
        if (this.options.disabledDates.includes(dateStr)) {
            return true;
        }
        
        return false;
    }
    
    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }
    
    isHoliday(date) {
        const dateStr = this.formatDate(date);
        return this.options.holidays.includes(dateStr);
    }
    
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    getDateTitle(date, isHoliday, isWeekend) {
        let title = date.toLocaleDateString(this.options.locale, {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        if (isHoliday) title += ' (Feriado)';
        if (isWeekend) title += ' (Fin de semana)';
        
        return title;
    }
    
    updateSelectedCount() {
        const count = this.selectedDates.size;
        this.container.querySelector('#selectedCount').textContent = count;
    }
    
    // Métodos públicos
    getSelectedDates() {
        return Array.from(this.selectedDates).sort();
    }
    
    setSelectedDates(dates) {
        this.selectedDates = new Set(dates);
        this.render();
    }
    
    addDate(dateStr) {
        this.selectedDates.add(dateStr);
        this.render();
    }
    
    removeDate(dateStr) {
        this.selectedDates.delete(dateStr);
        this.render();
    }
    
    goToMonth(year, month) {
        this.currentDate = new Date(year, month, 1);
        this.render();
    }
    
    goToToday() {
        this.currentDate = new Date();
        this.render();
    }
}

// Exportar para uso global
window.MultiDateCalendar = MultiDateCalendar;
