from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import Periodo, DiaFeriado


class PeriodoForm(forms.ModelForm):
    """Formulario para períodos con widgets de fecha apropiados"""
    
    class Meta:
        model = Periodo
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'horas_objetivo', 'horas_max_dia']
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Enero 2024, Q1 2024, Proyecto ABC'
                }
            ),
            'fecha_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'fecha_fin': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'horas_objetivo': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'max': '2000',
                    'placeholder': 'Ej: 160'
                }
            ),
            'horas_max_dia': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0.5',
                    'max': '24',
                    'step': '0.5',
                    'value': '8.0',
                    'placeholder': 'Ej: 7.5, 8.0'
                }
            )
        }
        labels = {
            'nombre': 'Nombre del período',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de finalización',
            'horas_objetivo': 'Horas objetivo',
            'horas_max_dia': 'Máximo horas por día'
        }
        help_texts = {
            'nombre': 'Nombre descriptivo para identificar el período',
            'fecha_inicio': 'Fecha en que inicia el período de trabajo',
            'fecha_fin': 'Fecha en que finaliza el período de trabajo',
            'horas_objetivo': 'Total de horas que planea trabajar en este período',
            'horas_max_dia': 'Máximo de horas que puede registrar por día'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Asegurar que las fechas se muestren correctamente en edición
        if self.instance and self.instance.pk:
            if self.instance.fecha_inicio:
                self.fields['fecha_inicio'].initial = self.instance.fecha_inicio
            if self.instance.fecha_fin:
                self.fields['fecha_fin'].initial = self.instance.fecha_fin

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            # Validar que fecha_fin sea posterior a fecha_inicio
            if fecha_fin <= fecha_inicio:
                raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
            
            # Validar que el período no sea demasiado largo (más de 2 años)
            if (fecha_fin - fecha_inicio).days > 730:
                raise ValidationError("El período no puede ser mayor a 2 años")
            
            # Validar que el período no sea demasiado corto (menos de 1 día)
            if (fecha_fin - fecha_inicio).days < 1:
                raise ValidationError("El período debe ser de al menos 1 día")
        
        return cleaned_data

    def clean_horas_objetivo(self):
        horas_objetivo = self.cleaned_data.get('horas_objetivo')
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        fecha_fin = self.cleaned_data.get('fecha_fin')
        horas_max_dia = self.cleaned_data.get('horas_max_dia', 8)
        
        if horas_objetivo and fecha_inicio and fecha_fin:
            dias_periodo = (fecha_fin - fecha_inicio).days + 1
            # Calcular días laborables (excluyendo fines de semana)
            dias_laborables = sum(1 for i in range(dias_periodo) 
                                if (fecha_inicio + timedelta(days=i)).weekday() < 5)
            
            horas_maximas_teoricas = dias_laborables * horas_max_dia
            
            if horas_objetivo > horas_maximas_teoricas:
                raise ValidationError(
                    f"Las horas objetivo ({horas_objetivo}) exceden el máximo teórico "
                    f"de {horas_maximas_teoricas} horas para {dias_laborables} días laborables "
                    f"con {horas_max_dia} horas máximas por día"
                )
        
        return horas_objetivo


class DiaFeriadoForm(forms.ModelForm):
    """Formulario para días feriados con widget de fecha apropiado"""
    
    class Meta:
        model = DiaFeriado
        fields = ['nombre', 'fecha', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Día de la Independencia, Navidad, Vacaciones'
                }
            ),
            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Descripción opcional del feriado...'
                }
            )
        }
        labels = {
            'nombre': 'Nombre del feriado',
            'fecha': 'Fecha del feriado',
            'descripcion': 'Descripción'
        }
        help_texts = {
            'nombre': 'Nombre descriptivo del feriado o día no laborable',
            'fecha': 'Seleccione la fecha del día feriado',
            'descripcion': 'Descripción opcional del día feriado'
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        
        if not fecha:
            raise ValidationError("La fecha es requerida")
        
        # Permitir fechas pasadas solo si es para edición
        if not self.instance.pk and fecha < date.today():
            raise ValidationError("No se pueden crear feriados en fechas pasadas")
        
        # No permitir fechas muy lejanas (más de 2 años)
        fecha_limite = date.today() + timedelta(days=730)
        if fecha > fecha_limite:
            raise ValidationError("No se pueden crear feriados con más de 2 años de anticipación")
        
        return fecha

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del feriado es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres")
        
        return nombre.strip()


class CalendarioFiltroForm(forms.Form):
    """Formulario para filtros del calendario"""
    
    año = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'type': 'number',
                'class': 'form-control',
                'min': '2020',
                'max': str(date.today().year + 2)
            }
        ),
        initial=date.today().year,
        label='Año'
    )
    
    mes = forms.ChoiceField(
        choices=[
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
            (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
            (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        initial=date.today().month,
        label='Mes'
    )

    def clean_año(self):
        año = self.cleaned_data.get('año')
        
        if año < 2020:
            raise ValidationError("No se pueden consultar años anteriores a 2020")
        
        if año > date.today().year + 2:
            raise ValidationError("No se pueden consultar años muy futuros")
        
        return año


class RangoFechasForm(forms.Form):
    """Formulario genérico para selección de rango de fechas"""
    
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fecha de inicio',
        help_text='Fecha de inicio del rango'
    )
    
    fecha_fin = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fecha de fin',
        help_text='Fecha de fin del rango'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer valores por defecto (mes actual)
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1)
        
        if not self.data:
            self.fields['fecha_inicio'].initial = primer_dia_mes
            self.fields['fecha_fin'].initial = hoy

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin")
            
            # Validar que el rango no sea demasiado amplio (más de 1 año)
            if (fecha_fin - fecha_inicio).days > 365:
                raise ValidationError("El rango de fechas no puede ser mayor a 1 año")
        
        return cleaned_data
