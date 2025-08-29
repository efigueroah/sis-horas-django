/**
 * Modern Calendar Widget using FullCalendar
 * Widget profesional y probado para calendarios
 */

class ModernCalendarWidget {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.calendar = null;
        this.options = {
            locale: 'es',
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listWeek'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                list: 'Lista'
            },
            height: 'auto',
            ...options
        };
        
        this.init();
    }
    
    async init() {
        // Cargar FullCalendar si no está disponible
        if (typeof FullCalendar === 'undefined') {
            await this.loadFullCalendar();
        }
        
        this.createCalendar();
        await this.loadEvents();
    }
    
    async loadFullCalendar() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    createCalendar() {
        const calendarEl = document.getElementById(this.containerId);
        
        this.calendar = new FullCalendar.Calendar(calendarEl, {
            ...this.options,
            events: this.loadEventsFromAPI.bind(this),
            eventClick: this.handleEventClick.bind(this),
            dateClick: this.handleDateClick.bind(this),
            eventDidMount: this.styleEvent.bind(this)
        });
        
        this.calendar.render();
    }
    
    async loadEventsFromAPI(info, successCallback, failureCallback) {
        try {
            const start = info.start.toISOString().split('T')[0];
            const end = info.end.toISOString().split('T')[0];
            
            const response = await fetch(`/api/horas/?fecha_inicio=${start}&fecha_fin=${end}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            const events = this.transformDataToEvents(data);
            
            successCallback(events);
        } catch (error) {
            console.error('Error loading calendar events:', error);
            failureCallback(error);
        }
    }
    
    transformDataToEvents(horasData) {
        const events = [];
        const horasPorFecha = {};
        
        // Agrupar horas por fecha
        horasData.forEach(hora => {
            if (!horasPorFecha[hora.fecha]) {
                horasPorFecha[hora.fecha] = {
                    fecha: hora.fecha,
                    totalHoras: 0,
                    registros: []
                };
            }
            
            horasPorFecha[hora.fecha].totalHoras += parseFloat(hora.horas);
            horasPorFecha[hora.fecha].registros.push(hora);
        });
        
        // Crear eventos para el calendario
        Object.values(horasPorFecha).forEach(dia => {
            events.push({
                id: `day-${dia.fecha}`,
                title: `${dia.totalHoras}h`,
                start: dia.fecha,
                allDay: true,
                backgroundColor: this.getColorByHours(dia.totalHoras),
                borderColor: this.getColorByHours(dia.totalHoras),
                extendedProps: {
                    totalHoras: dia.totalHoras,
                    registros: dia.registros
                }
            });
        });
        
        return events;
    }
    
    getColorByHours(horas) {
        if (horas >= 8) return '#28a745'; // Verde - día completo
        if (horas >= 4) return '#ffc107'; // Amarillo - medio día
        if (horas > 0) return '#17a2b8';  // Azul - pocas horas
        return '#6c757d'; // Gris - sin horas
    }
    
    styleEvent(info) {
        const event = info.event;
        const totalHoras = event.extendedProps.totalHoras;
        
        // Agregar clases CSS personalizadas
        info.el.classList.add('calendar-event');
        
        if (totalHoras >= 8) {
            info.el.classList.add('full-day');
        } else if (totalHoras >= 4) {
            info.el.classList.add('half-day');
        } else if (totalHoras > 0) {
            info.el.classList.add('partial-day');
        }
        
        // Agregar tooltip
        info.el.title = `${totalHoras} horas trabajadas`;
    }
    
    handleEventClick(info) {
        const event = info.event;
        const registros = event.extendedProps.registros;
        
        // Mostrar modal con detalles del día
        this.showDayDetails(event.start, registros);
    }
    
    handleDateClick(info) {
        // Navegar a formulario de registro de horas para esa fecha
        const fecha = info.dateStr;
        window.location.href = `/horas/registrar/?fecha=${fecha}`;
    }
    
    showDayDetails(fecha, registros) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-calendar-day me-2"></i>
                            Detalles del ${fecha.toLocaleDateString('es-ES')}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${this.renderDayDetailsContent(registros)}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <a href="/horas/registrar/?fecha=${fecha.toISOString().split('T')[0]}" class="btn btn-primary">
                            <i class="fas fa-plus me-1"></i>Agregar Horas
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Limpiar modal al cerrar
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    renderDayDetailsContent(registros) {
        if (!registros || registros.length === 0) {
            return '<p class="text-muted">No hay registros de horas para este día.</p>';
        }
        
        let html = '<div class="list-group">';
        let totalHoras = 0;
        
        registros.forEach(registro => {
            totalHoras += parseFloat(registro.horas);
            html += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${registro.proyecto_nombre}</h6>
                        <small class="badge bg-primary">${registro.horas}h</small>
                    </div>
                    <p class="mb-1">${registro.descripcion || 'Sin descripción'}</p>
                    <small class="text-muted">
                        <i class="fas fa-${registro.tipo_tarea === 'reunion' ? 'users' : 'tasks'} me-1"></i>
                        ${registro.tipo_tarea}
                    </small>
                </div>
            `;
        });
        
        html += '</div>';
        html += `
            <div class="mt-3 p-3 bg-light rounded">
                <strong>Total del día: ${totalHoras} horas</strong>
            </div>
        `;
        
        return html;
    }
    
    // Métodos públicos para controlar el calendario
    refresh() {
        if (this.calendar) {
            this.calendar.refetchEvents();
        }
    }
    
    goToDate(date) {
        if (this.calendar) {
            this.calendar.gotoDate(date);
        }
    }
    
    changeView(viewName) {
        if (this.calendar) {
            this.calendar.changeView(viewName);
        }
    }
    
    destroy() {
        if (this.calendar) {
            this.calendar.destroy();
        }
    }
}

// Widget de calendario simple usando input type="month"
class SimpleCalendarWidget {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            showWeekNumbers: false,
            highlightToday: true,
            ...options
        };
        
        this.init();
    }
    
    init() {
        const container = document.getElementById(this.containerId);
        
        container.innerHTML = `
            <div class="simple-calendar-widget">
                <div class="calendar-header">
                    <input type="month" class="form-control" id="month-selector" value="${this.getCurrentMonth()}">
                    <button type="button" class="btn btn-outline-primary btn-sm ms-2" id="today-btn">
                        <i class="fas fa-calendar-day me-1"></i>Hoy
                    </button>
                </div>
                <div class="calendar-grid mt-3" id="calendar-grid">
                    <!-- Grid se genera dinámicamente -->
                </div>
            </div>
        `;
        
        this.bindEvents();
        this.loadMonth();
    }
    
    bindEvents() {
        const monthSelector = document.getElementById('month-selector');
        const todayBtn = document.getElementById('today-btn');
        
        monthSelector.addEventListener('change', () => {
            this.loadMonth();
        });
        
        todayBtn.addEventListener('click', () => {
            monthSelector.value = this.getCurrentMonth();
            this.loadMonth();
        });
    }
    
    getCurrentMonth() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    }
    
    async loadMonth() {
        const monthSelector = document.getElementById('month-selector');
        const [year, month] = monthSelector.value.split('-');
        
        try {
            const response = await fetch(`/api/calendario/${year}/${month}/`);
            const data = await response.json();
            
            if (data.success) {
                this.renderCalendar(data.calendario);
            } else {
                this.renderBasicCalendar(parseInt(year), parseInt(month));
            }
        } catch (error) {
            console.error('Error loading calendar:', error);
            this.renderBasicCalendar(parseInt(year), parseInt(month));
        }
    }
    
    renderCalendar(calendarData) {
        const grid = document.getElementById('calendar-grid');
        
        let html = `
            <div class="calendar-weekdays">
                <div class="weekday">Dom</div>
                <div class="weekday">Lun</div>
                <div class="weekday">Mar</div>
                <div class="weekday">Mié</div>
                <div class="weekday">Jue</div>
                <div class="weekday">Vie</div>
                <div class="weekday">Sáb</div>
            </div>
            <div class="calendar-days">
        `;
        
        calendarData.forEach(week => {
            week.forEach(day => {
                const dayClass = this.getDayClass(day);
                html += `
                    <div class="calendar-day ${dayClass}" data-date="${day.fecha || ''}">
                        <span class="day-number">${day.dia || ''}</span>
                        ${day.horas ? `<span class="day-hours">${day.horas}h</span>` : ''}
                    </div>
                `;
            });
        });
        
        html += '</div>';
        grid.innerHTML = html;
        
        // Agregar event listeners a los días
        grid.querySelectorAll('.calendar-day[data-date]').forEach(dayEl => {
            dayEl.addEventListener('click', (e) => {
                const fecha = e.currentTarget.dataset.date;
                if (fecha) {
                    window.location.href = `/horas/registrar/?fecha=${fecha}`;
                }
            });
        });
    }
    
    getDayClass(day) {
        const classes = [];
        
        if (!day.dia) {
            classes.push('empty-day');
        } else {
            classes.push('active-day');
            
            if (day.es_hoy) classes.push('today');
            if (day.es_fin_semana) classes.push('weekend');
            if (day.es_feriado) classes.push('holiday');
            if (day.estado === 'completo') classes.push('complete-day');
            if (day.estado === 'parcial') classes.push('partial-day');
        }
        
        return classes.join(' ');
    }
    
    renderBasicCalendar(year, month) {
        // Fallback para calendario básico
        const grid = document.getElementById('calendar-grid');
        grid.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No se pudo cargar el calendario. Mostrando vista básica.
            </div>
        `;
    }
}

// Exponer widgets globalmente
window.CalendarWidgets = {
    ModernCalendarWidget,
    SimpleCalendarWidget
};
