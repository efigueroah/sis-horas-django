"""
Widgets personalizados para el manejo de horas
"""
from django import forms
from django.core.exceptions import ValidationError
import re
from decimal import Decimal, InvalidOperation


class HoursWidget(forms.TextInput):
    """
    Widget personalizado para entrada de horas que soporta múltiples formatos:
    - Formato decimal: 1.5, 2.0, 0.5
    - Formato HH:MM: 01:30, 02:00, 00:30
    - Formato H:MM: 1:30, 2:00, 0:30
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control hours-input',
            'placeholder': 'Ej: 1.5 o 01:30',
            'pattern': r'^(\d+(\.\d+)?|\d{1,2}:\d{2})$',
            'title': 'Ingrese horas en formato decimal (1.5) o tiempo (01:30)'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    class Media:
        css = {
            'all': ('css/hours-widget.css',)
        }
        js = ('js/hours-widget.js',)


class HoursField(forms.CharField):
    """
    Campo personalizado para horas que convierte automáticamente entre formatos
    """
    
    widget = HoursWidget
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', 
            'Ingrese horas en formato decimal (1.5) o tiempo (01:30). '
            'Incrementos de 30 minutos (0.5h)'
        )
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """Convierte el valor de entrada a decimal"""
        if not value:
            return None
        
        value = str(value).strip()
        
        # Si ya es formato decimal, validar y retornar
        if self._is_decimal_format(value):
            try:
                decimal_value = float(Decimal(value))
                self._validate_hours_value(decimal_value)
                return decimal_value
            except (ValueError, InvalidOperation):
                raise ValidationError('Formato de horas inválido')
        
        # Si es formato HH:MM, convertir a decimal
        if self._is_time_format(value):
            decimal_value = self._time_to_decimal(value)
            self._validate_hours_value(decimal_value)
            return decimal_value
        
        # Formato no reconocido
        raise ValidationError(
            'Formato de horas inválido. Use formato decimal (1.5) o tiempo (01:30)'
        )
    
    def _validate_hours_value(self, value):
        """Validar el valor de horas convertido"""
        if value < 0.5:
            raise ValidationError('El mínimo es 0.5 horas (30 minutos)')
        
        if value > 12:
            raise ValidationError('El máximo es 12 horas por registro')
        
        # Validar que sea múltiplo de 0.5
        if (value * 2) % 1 != 0:
            raise ValidationError('Las horas deben ser múltiplos de 0.5 (30 minutos)')
    
    def _is_decimal_format(self, value):
        """Verifica si el valor está en formato decimal"""
        decimal_pattern = r'^\d+(\.\d+)?$'
        return re.match(decimal_pattern, value) is not None
    
    def _is_time_format(self, value):
        """Verifica si el valor está en formato HH:MM"""
        time_pattern = r'^\d{1,2}:\d{2}$'
        return re.match(time_pattern, value) is not None
    
    def _time_to_decimal(self, time_str):
        """Convierte formato HH:MM a decimal"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            
            # Validar rangos
            if hours < 0 or hours > 23:
                raise ValidationError('Las horas deben estar entre 0 y 23')
            
            if minutes < 0 or minutes > 59:
                raise ValidationError('Los minutos deben estar entre 0 y 59')
            
            # Convertir a decimal
            decimal_hours = hours + (minutes / 60.0)
            
            # Redondear a incrementos de 0.5 (30 minutos)
            return round(decimal_hours * 2) / 2
            
        except ValueError:
            raise ValidationError('Formato de tiempo inválido')
    
    def validate(self, value):
        """Validaciones adicionales para horas"""
        super().validate(value)
        
        if value is not None:
            # Validar rango mínimo y máximo
            if value < 0.5:
                raise ValidationError('El mínimo es 0.5 horas (30 minutos)')
            
            if value > 12:
                raise ValidationError('El máximo es 12 horas por registro')
            
            # Validar que sea múltiplo de 0.5
            if (value * 2) % 1 != 0:
                raise ValidationError('Las horas deben ser múltiplos de 0.5 (30 minutos)')


def decimal_to_time_format(decimal_hours):
    """
    Convierte horas decimales a formato HH:MM para mostrar
    """
    if decimal_hours is None:
        return ''
    
    try:
        hours = int(decimal_hours)
        minutes = int((decimal_hours - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"
    except (ValueError, TypeError):
        return str(decimal_hours)


def time_format_to_decimal(time_str):
    """
    Convierte formato HH:MM a decimal
    """
    if not time_str:
        return None
    
    try:
        if ':' in time_str:
            hours, minutes = map(int, time_str.split(':'))
            return hours + (minutes / 60.0)
        else:
            return float(time_str)
    except (ValueError, TypeError):
        return None
