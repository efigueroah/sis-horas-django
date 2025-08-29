"""
Campo personalizado simplificado para horas que funciona con Django
"""
from django import forms
from django.core.exceptions import ValidationError
import re
from decimal import Decimal, InvalidOperation


class HoursInput(forms.TextInput):
    """Widget simplificado para entrada de horas"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control hours-input',
            'placeholder': 'Ej: 1.5 o 01:30',
            'title': 'Ingrese horas en formato decimal (1.5) o tiempo (01:30)'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class HoursField(forms.DecimalField):
    """Campo simplificado para horas que convierte automáticamente entre formatos"""
    
    widget = HoursInput
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 4)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('min_value', 0.5)
        kwargs.setdefault('max_value', 12)
        kwargs.setdefault('help_text', 
            'Ingrese horas en formato decimal (1.5) o tiempo (01:30). Incrementos de 30 minutos'
        )
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """Convierte el valor de entrada a decimal"""
        if not value:
            return None
        
        value = str(value).strip()
        
        # Si es formato HH:MM, convertir a decimal
        if self._is_time_format(value):
            decimal_value = self._time_to_decimal(value)
            return super().to_python(decimal_value)
        
        # Si es formato decimal, usar validación normal
        return super().to_python(value)
    
    def validate(self, value):
        """Validaciones adicionales para horas"""
        super().validate(value)
        
        if value is not None:
            # Validar que sea múltiplo de 0.5
            if (float(value) * 2) % 1 != 0:
                raise ValidationError('Las horas deben ser múltiplos de 0.5 (30 minutos)')
    
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


def convert_hours_input(value):
    """Función utilitaria para convertir entrada de horas"""
    if not value:
        return None
    
    value = str(value).strip()
    
    # Si es formato HH:MM
    if re.match(r'^\d{1,2}:\d{2}$', value):
        try:
            hours, minutes = map(int, value.split(':'))
            if 0 <= hours <= 23 and 0 <= minutes <= 59:
                decimal_hours = hours + (minutes / 60.0)
                return round(decimal_hours * 2) / 2
        except ValueError:
            pass
    
    # Si es formato decimal
    try:
        return float(value)
    except ValueError:
        pass
    
    return None
