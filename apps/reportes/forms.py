from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from apps.proyectos.models import Proyecto
from apps.core.models import Periodo
from .models import ConfiguracionReporte


class ExportarReporteForm(forms.Form):
    """Formulario para exportar reportes con widgets de fecha apropiados"""
    
    FORMATO_CHOICES = [
        ('csv', 'CSV (Comma Separated Values)'),
        ('xlsx', 'Excel (XLSX)'),
        ('pdf', 'PDF')
    ]
    
    SEPARADOR_CHOICES = [
        (',', 'Coma (,)'),
        (';', 'Punto y coma (;)'),
        ('|', 'Pipe (|)')
    ]
    
    # Filtros de fecha
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fecha de inicio',
        help_text='Fecha de inicio del período a exportar'
    )
    
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Fecha de fin',
        help_text='Fecha de fin del período a exportar'
    )
    
    # Filtros de contenido
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Período',
        empty_label='Todos los períodos'
    )
    
    proyectos = forms.ModelMultipleChoiceField(
        queryset=Proyecto.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select',
                'size': '5'
            }
        ),
        label='Proyectos',
        help_text='Mantén presionado Ctrl (Cmd en Mac) para seleccionar múltiples proyectos'
    )
    
    # Opciones de formato
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='csv',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Formato de archivo'
    )
    
    separador = forms.ChoiceField(
        choices=SEPARADOR_CHOICES,
        initial=',',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Separador CSV',
        help_text='Solo aplica para formato CSV'
    )
    
    # Opciones de contenido
    incluir_totales = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Incluir totales por proyecto'
    )
    
    agrupar_por_fecha = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Agrupar por fecha'
    )
    
    incluir_descripcion = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Incluir descripciones'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar períodos y proyectos del usuario
            self.fields['periodo'].queryset = Periodo.objects.filter(
                usuario=user
            ).order_by('-fecha_inicio')
            
            self.fields['proyectos'].queryset = Proyecto.objects.filter(
                usuario=user
            ).order_by('nombre')
        
        # Establecer fechas por defecto (mes actual)
        if not self.data:
            hoy = date.today()
            primer_dia_mes = hoy.replace(day=1)
            self.fields['fecha_inicio'].initial = primer_dia_mes
            self.fields['fecha_fin'].initial = hoy

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        periodo = cleaned_data.get('periodo')
        
        # Validar rango de fechas
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin")
            
            # Validar que el rango no sea demasiado amplio (más de 2 años)
            if (fecha_fin - fecha_inicio).days > 730:
                raise ValidationError("El rango de fechas no puede ser mayor a 2 años")
        
        # Si se selecciona un período, las fechas son opcionales
        if not periodo and not (fecha_inicio and fecha_fin):
            raise ValidationError("Debe seleccionar un período o especificar un rango de fechas")
        
        return cleaned_data


class ConfiguracionReporteForm(forms.Form):
    """Formulario para configuración de reportes"""
    
    FORMATO_CHOICES = [
        ('csv', 'CSV (Comma Separated Values)'),
        ('xlsx', 'Excel (XLSX)'),
        ('pdf', 'PDF')
    ]
    
    SEPARADOR_CHOICES = [
        (',', 'Coma (,)'),
        (';', 'Punto y coma (;)'),
        ('|', 'Pipe (|)')
    ]
    
    DECIMAL_CHOICES = [
        ('.', 'Punto (.) - Formato internacional'),
        (',', 'Coma (,) - Formato europeo/español')
    ]
    
    COLUMNA_CHOICES = [
        ('fecha', 'Fecha'),
        ('proyecto', 'Proyecto'),
        ('horas', 'Horas'),
        ('tipo_tarea', 'Tipo de Tarea'),
        ('descripcion', 'Descripción'),
        ('cliente', 'Cliente')
    ]
    
    # Configuración de exportación
    formato_exportacion = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='csv',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Formato de exportación por defecto'
    )
    
    separador_csv = forms.ChoiceField(
        choices=SEPARADOR_CHOICES,
        initial=',',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Separador CSV por defecto'
    )
    
    separador_decimal = forms.ChoiceField(
        choices=DECIMAL_CHOICES,
        initial='.',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Separador decimal'
    )
    
    incluir_encabezados = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Incluir encabezados en exportación'
    )
    
    # Filtros por defecto
    periodo_defecto = forms.ModelChoiceField(
        queryset=Periodo.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Período por defecto',
        empty_label='Seleccionar período...'
    )
    
    proyectos_defecto = forms.ModelMultipleChoiceField(
        queryset=Proyecto.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select',
                'size': '4'
            }
        ),
        label='Proyectos por defecto'
    )
    
    solo_activos = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Solo incluir proyectos activos por defecto'
    )
    
    # Columnas a incluir
    columnas = forms.MultipleChoiceField(
        choices=COLUMNA_CHOICES,
        initial=['fecha', 'proyecto', 'horas'],
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Columnas a incluir por defecto'
    )

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        user = kwargs.pop('user', None) or self.usuario
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar períodos y proyectos del usuario
            self.fields['periodo_defecto'].queryset = Periodo.objects.filter(
                usuario=user
            ).order_by('-fecha_inicio')
            
            self.fields['proyectos_defecto'].queryset = Proyecto.objects.filter(
                usuario=user
            ).order_by('nombre')
            
            # Cargar configuración existente
            try:
                config = ConfiguracionReporte.objects.get(usuario=user)
                self.initial = {
                    'formato_exportacion': config.formato_exportacion,
                    'separador_csv': config.separador_csv,
                    'separador_decimal': getattr(config, 'separador_decimal', '.'),
                    'incluir_encabezados': config.incluir_encabezados,
                    'periodo_defecto': config.periodo_defecto,
                    'proyectos_defecto': config.proyectos_defecto.all(),
                    'solo_activos': config.solo_activos,
                    'columnas': config.columnas
                }
            except ConfiguracionReporte.DoesNotExist:
                pass

    def save(self):
        """Guardar la configuración"""
        if not self.usuario:
            raise ValueError("Usuario requerido para guardar configuración")
            
        config, created = ConfiguracionReporte.objects.get_or_create(
            usuario=self.usuario,
            defaults={}
        )
        
        # Actualizar campos
        config.formato_exportacion = self.cleaned_data['formato_exportacion']
        config.separador_csv = self.cleaned_data['separador_csv']
        config.separador_decimal = self.cleaned_data['separador_decimal']
        config.incluir_encabezados = self.cleaned_data['incluir_encabezados']
        config.periodo_defecto = self.cleaned_data['periodo_defecto']
        config.solo_activos = self.cleaned_data['solo_activos']
        config.columnas = self.cleaned_data['columnas']
        config.save()
        
        # Actualizar proyectos por defecto (ManyToMany)
        config.proyectos_defecto.set(self.cleaned_data['proyectos_defecto'])
        
        return config

    def clean_columnas(self):
        columnas = self.cleaned_data.get('columnas')
        
        if not columnas:
            raise ValidationError("Debe seleccionar al menos una columna")
        
        # Validar que se incluyan columnas esenciales
        columnas_esenciales = ['fecha', 'proyecto', 'horas']
        columnas_faltantes = [col for col in columnas_esenciales if col not in columnas]
        
        if columnas_faltantes:
            raise ValidationError(
                f"Las siguientes columnas son esenciales y deben estar incluidas: {', '.join(columnas_faltantes)}"
            )
        
        return columnas


class FiltroReporteForm(forms.Form):
    """Formulario para filtrar reportes en la vista de lista"""
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control form-control-sm'
            }
        ),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control form-control-sm'
            }
        ),
        label='Hasta'
    )
    
    proyecto = forms.ModelChoiceField(
        queryset=Proyecto.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-sm'
            }
        ),
        label='Proyecto',
        empty_label='Todos'
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
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise ValidationError("La fecha 'desde' no puede ser posterior a la fecha 'hasta'")
        
        return cleaned_data
