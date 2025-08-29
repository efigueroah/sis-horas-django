from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from datetime import date, timedelta
from decimal import Decimal
from django_select2.forms import Select2Widget
from .models import RegistroHora
from .fields import HoursField, HoursInput, convert_hours_input
from apps.proyectos.models import Proyecto
from apps.core.models import Periodo


class ProyectoSelect2Widget(Select2Widget):
    """Widget Select2 para proyectos con búsqueda"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        attrs = kwargs.get('attrs', {})
        attrs.update({
            'data-placeholder': 'Buscar proyecto...',
            'data-allow-clear': 'false',
            'data-width': '100%'
        })
        kwargs['attrs'] = attrs
        super().__init__(*args, **kwargs)


class RegistroHoraForm(forms.ModelForm):
    """Formulario para registro de horas con widgets apropiados"""
    
    # Campo de horas simplificado
    horas = forms.DecimalField(
        label='Horas trabajadas',
        help_text='Ingrese horas en formato decimal (ej: 1.5 para 1 hora y 30 minutos)',
        max_digits=4,
        decimal_places=2,
        min_value=0.5,
        max_value=12.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '0.5',
            'max': '12.0'
        })
    )
    
    class Meta:
        model = RegistroHora
        fields = ['fecha', 'proyecto', 'horas', 'descripcion', 'tipo_tarea']
        widgets = {
            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': date.today().isoformat(),  # No permitir fechas futuras
                }
            ),
            'proyecto': ProyectoSelect2Widget(attrs={
                'class': 'form-select',
                'data-placeholder': 'Buscar proyecto...'
            }),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe las actividades realizadas...'
                }
            ),
            'tipo_tarea': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            )
        }
        labels = {
            'fecha': 'Fecha de trabajo',
            'proyecto': 'Proyecto',
            'descripcion': 'Descripción de actividades',
            'tipo_tarea': 'Tipo de tarea'
        }
        help_texts = {
            'fecha': 'Seleccione la fecha en que realizó el trabajo',
            'descripcion': 'Opcional: Describa las actividades realizadas',
            'tipo_tarea': 'Seleccione el tipo de actividad realizada'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar proyectos solo del usuario actual
        if self.user:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(
                usuario=self.user,
                activo=True
            ).order_by('nombre')
        
        # Configurar fecha por defecto (hoy)
        if not self.instance.pk:
            self.fields['fecha'].initial = date.today()
        
        # Agregar clases CSS adicionales
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-field-enhanced'
            else:
                field.widget.attrs['class'] = 'form-field-enhanced'

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        
        if not fecha:
            raise ValidationError("La fecha es requerida")
        
        # No permitir fechas futuras
        if fecha > date.today():
            raise ValidationError("No se pueden registrar horas en fechas futuras")
        
        # No permitir fechas muy antiguas (más de 1 año)
        hace_un_año = date.today() - timedelta(days=365)
        if fecha < hace_un_año:
            raise ValidationError("No se pueden registrar horas de hace más de un año")
        
        return fecha

    def clean_horas(self):
        horas = self.cleaned_data.get('horas')
        
        if not horas:
            raise ValidationError("Las horas son requeridas")
        
        # El campo HoursField ya maneja la conversión y validaciones básicas
        # Solo necesitamos validar que sea múltiplo de 0.5
        if (float(horas) * 2) % 1 != 0:
            raise ValidationError("Las horas deben ser múltiplos de 0.5 (30 minutos)")
        
        return horas

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        proyecto = cleaned_data.get('proyecto')
        horas = cleaned_data.get('horas')
        
        if fecha and self.user:
            # Validar que no sea fin de semana
            if fecha.weekday() >= 5:  # 5=sábado, 6=domingo
                raise ValidationError("No se pueden registrar horas en fines de semana")
            
            # Validar que no sea día feriado
            from apps.core.models import DiaFeriado
            if DiaFeriado.objects.filter(fecha=fecha, usuario=self.user).exists():
                raise ValidationError("No se pueden registrar horas en días feriados")
            
            # Validar horas máximas por día
            if horas:
                total_horas_dia = RegistroHora.objects.filter(
                    fecha=fecha,
                    usuario=self.user
                ).exclude(pk=self.instance.pk if self.instance else None).aggregate(
                    total=models.Sum('horas')
                )['total'] or 0
                
                # Obtener límite de horas del período activo o perfil
                periodo_activo = Periodo.objects.filter(
                    usuario=self.user,
                    activo=True
                ).first()
                
                horas_max = 8  # Default
                if periodo_activo:
                    horas_max = periodo_activo.horas_max_dia
                elif hasattr(self.user, 'profile'):
                    horas_max = self.user.profile.horas_max_dia
                
                # Convertir horas a Decimal para la comparación
                horas_decimal = Decimal(str(horas))
                
                if total_horas_dia + horas_decimal > horas_max:
                    raise ValidationError(
                        f"Excede el máximo de {horas_max} horas por día. "
                        f"Ya tienes {total_horas_dia}h registradas."
                    )
        
        # Validar que el proyecto pertenezca al usuario
        if proyecto and self.user and proyecto.usuario != self.user:
            raise ValidationError("El proyecto seleccionado no es válido")
        
        return cleaned_data


class FiltroHorasForm(forms.Form):
    """Formulario para filtrar registros de horas"""
    
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fecha de inicio'
    )
    
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fecha de fin'
    )
    
    proyecto = forms.ModelChoiceField(
        queryset=Proyecto.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Proyecto',
        empty_label='Todos los proyectos'
    )
    
    tipo_tarea = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + RegistroHora.TIPO_TAREA_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Tipo de tarea'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(
                usuario=user
            ).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin")
        
        return cleaned_data


# ============================================================================
# FORMULARIOS PARA CARGA EN BLOQUE Y VISTA COMPLETA DE DÍA
# ============================================================================

class RegistroHoraBloqueForm(forms.Form):
    """Formulario para registro de horas en bloque (múltiples fechas)"""
    
    # Información básica de la tarea
    proyecto = forms.ModelChoiceField(
        queryset=Proyecto.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Proyecto',
        help_text='Proyecto al que se asignarán todas las horas'
    )
    
    horas = forms.DecimalField(
        max_digits=4,
        decimal_places=1,
        min_value=0.5,
        max_value=12,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '0.5',
            'max': '12',
            'placeholder': 'Ej: 0.5, 1.0, 2.0'
        }),
        label='Horas por sesión',
        help_text='Horas que se registrarán en cada fecha seleccionada (múltiplos de 0.5)'
    )
    
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ej: Reunión semanal de seguimiento del proyecto...'
        }),
        label='Descripción',
        help_text='Descripción que se aplicará a todos los registros'
    )
    
    tipo_tarea = forms.ChoiceField(
        choices=RegistroHora.TIPO_TAREA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de tarea'
    )
    
    # Selección de fechas
    PATRON_CHOICES = [
        ('manual', 'Selección manual de fechas'),
        ('semanal', 'Patrón semanal (mismo día cada semana)'),
        ('quincenal', 'Patrón quincenal (cada 15 días)'),
        ('mensual', 'Patrón mensual (mismo día cada mes)'),
    ]
    
    patron_repeticion = forms.ChoiceField(
        choices=PATRON_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Patrón de repetición',
        initial='manual'
    )
    
    # Para selección manual
    fechas_manuales = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        label='Fechas seleccionadas'
    )
    
    # Para patrones automáticos
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label='Fecha de inicio'
    )
    
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False,
        label='Fecha de fin'
    )
    
    # Para patrón semanal
    dia_semana = forms.ChoiceField(
        choices=[
            (0, 'Lunes'),
            (1, 'Martes'),
            (2, 'Miércoles'),
            (3, 'Jueves'),
            (4, 'Viernes'),
            (5, 'Sábado'),
            (6, 'Domingo'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Día de la semana'
    )
    
    # Para patrón mensual
    dia_mes = forms.IntegerField(
        min_value=1,
        max_value=31,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 15 (día 15 de cada mes)'
        }),
        required=False,
        label='Día del mes'
    )
    
    # Opciones adicionales
    omitir_feriados = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Omitir días feriados',
        help_text='No crear registros en días feriados'
    )
    
    omitir_fines_semana = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Omitir fines de semana',
        help_text='No crear registros en sábados y domingos'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(
                usuario=self.user,
                activo=True
            ).order_by('nombre')
            
            # Configurar parámetros de horas según el perfil del usuario
            profile = getattr(self.user, 'profile', None)
            if profile:
                incremento = float(profile.incremento_horas)
                minimo = float(profile.horas_minimas)
                maximo = float(profile.horas_maximas)
            else:
                incremento = 0.5
                minimo = 0.5
                maximo = 12.0
            
            # Actualizar campo de horas con configuración del usuario
            self.fields['horas'].min_value = minimo
            self.fields['horas'].max_value = maximo
            self.fields['horas'].widget.attrs.update({
                'step': str(incremento),
                'min': str(minimo),
                'max': str(maximo),
                'placeholder': f'Ej: {minimo}, {minimo + incremento}, {minimo + (incremento * 2)}'
            })
            self.fields['horas'].help_text = f'Horas que se registrarán en cada fecha seleccionada (múltiplos de {incremento})'
            
            # Obtener período activo para limitar fechas
            try:
                periodo_activo = Periodo.objects.get(usuario=self.user, activo=True)
                # Configurar límites de fecha según el período activo
                self.fields['fecha_inicio'].widget.attrs.update({
                    'min': periodo_activo.fecha_inicio.isoformat(),
                    'max': periodo_activo.fecha_fin.isoformat()
                })
                self.fields['fecha_fin'].widget.attrs.update({
                    'min': periodo_activo.fecha_inicio.isoformat(),
                    'max': periodo_activo.fecha_fin.isoformat()
                })
            except Periodo.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        patron = cleaned_data.get('patron_repeticion')
        
        # Validar que existe período activo
        if self.user:
            try:
                periodo_activo = Periodo.objects.get(usuario=self.user, activo=True)
            except Periodo.DoesNotExist:
                raise ValidationError('No hay un período activo configurado.')
        
        if patron == 'manual':
            fechas_manuales = cleaned_data.get('fechas_manuales')
            if not fechas_manuales:
                raise ValidationError('Debe seleccionar al menos una fecha para el patrón manual.')
            
            # Validar fechas manuales están dentro del período
            if self.user:
                from datetime import datetime
                for fecha_str in fechas_manuales.split(','):
                    try:
                        fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d').date()
                        if fecha < periodo_activo.fecha_inicio or fecha > periodo_activo.fecha_fin:
                            raise ValidationError(f'La fecha {fecha.strftime("%d/%m/%Y")} está fuera del período activo.')
                    except ValueError:
                        continue
        else:
            fecha_inicio = cleaned_data.get('fecha_inicio')
            fecha_fin = cleaned_data.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                raise ValidationError('Debe especificar fecha de inicio y fin para patrones automáticos.')
            
            if fecha_inicio >= fecha_fin:
                raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')
            
            # Validar fechas están dentro del período activo
            if self.user:
                if fecha_inicio < periodo_activo.fecha_inicio or fecha_fin > periodo_activo.fecha_fin:
                    raise ValidationError(f'Las fechas deben estar dentro del período activo ({periodo_activo.fecha_inicio.strftime("%d/%m/%Y")} - {periodo_activo.fecha_fin.strftime("%d/%m/%Y")}).')
            
            # Validaciones específicas por patrón
            if patron == 'semanal' and cleaned_data.get('dia_semana') is None:
                raise ValidationError('Debe seleccionar el día de la semana.')
            
            if patron == 'mensual' and not cleaned_data.get('dia_mes'):
                raise ValidationError('Debe especificar el día del mes.')
        
        return cleaned_data
    
    def generar_fechas(self):
        """Genera la lista de fechas según el patrón seleccionado"""
        from datetime import datetime
        from apps.core.models import DiaFeriado
        
        patron = self.cleaned_data['patron_repeticion']
        fechas = []
        
        if patron == 'manual':
            # Parsear fechas manuales desde el campo hidden
            fechas_str = self.cleaned_data['fechas_manuales']
            if fechas_str:
                for fecha_str in fechas_str.split(','):
                    try:
                        fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d').date()
                        fechas.append(fecha)
                    except ValueError:
                        continue
        
        else:
            fecha_inicio = self.cleaned_data['fecha_inicio']
            fecha_fin = self.cleaned_data['fecha_fin']
            
            if patron == 'semanal':
                dia_semana = int(self.cleaned_data['dia_semana'])
                fecha_actual = fecha_inicio
                
                # Encontrar el primer día de la semana especificada
                while fecha_actual.weekday() != dia_semana:
                    fecha_actual += timedelta(days=1)
                
                # Generar fechas semanales
                while fecha_actual <= fecha_fin:
                    fechas.append(fecha_actual)
                    fecha_actual += timedelta(weeks=1)
            
            elif patron == 'quincenal':
                fecha_actual = fecha_inicio
                while fecha_actual <= fecha_fin:
                    fechas.append(fecha_actual)
                    fecha_actual += timedelta(days=15)
            
            elif patron == 'mensual':
                dia_mes = self.cleaned_data['dia_mes']
                fecha_actual = fecha_inicio.replace(day=min(dia_mes, 28))  # Evitar errores con días > 28
                
                while fecha_actual <= fecha_fin:
                    # Ajustar el día del mes si es necesario
                    try:
                        fecha_mes = fecha_actual.replace(day=dia_mes)
                        if fecha_mes <= fecha_fin:
                            fechas.append(fecha_mes)
                    except ValueError:
                        # Día no válido para este mes (ej: 31 en febrero)
                        pass
                    
                    # Avanzar al siguiente mes
                    if fecha_actual.month == 12:
                        fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
                    else:
                        fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)
        
        # Filtrar fechas según opciones y período activo
        fechas_filtradas = []
        feriados = set()
        periodo_activo = None
        
        if self.user:
            try:
                periodo_activo = Periodo.objects.get(usuario=self.user, activo=True)
            except Periodo.DoesNotExist:
                pass
        
        if self.cleaned_data.get('omitir_feriados') and self.user:
            feriados = set(
                DiaFeriado.objects.filter(usuario=self.user)
                .values_list('fecha', flat=True)
            )
        
        for fecha in fechas:
            # Validar que está dentro del período activo
            if periodo_activo:
                if fecha < periodo_activo.fecha_inicio or fecha > periodo_activo.fecha_fin:
                    continue
            
            # Omitir fines de semana si está marcado
            if self.cleaned_data.get('omitir_fines_semana') and fecha.weekday() >= 5:
                continue
            
            # Omitir feriados (siempre, no opcional)
            if fecha in feriados:
                continue
            
            fechas_filtradas.append(fecha)
        
        return sorted(fechas_filtradas)


class VistaCompletaDiaForm(forms.Form):
    """Formulario para ver todas las tareas de un día específico"""
    
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Fecha',
        help_text='Seleccione la fecha para ver todas las tareas'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Establecer fecha actual por defecto
        if not self.is_bound:
            self.fields['fecha'].initial = timezone.now().date()
