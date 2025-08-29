from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import re
from .models import Proyecto


class ProyectoForm(forms.ModelForm):
    """Formulario para proyectos con widgets apropiados"""
    
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'cliente', 'fecha_inicio', 'fecha_fin', 'color_hex', 'activo']
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Desarrollo Web, Consultoría, Proyecto ABC'
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Descripción detallada del proyecto...'
                }
            ),
            'cliente': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Empresa XYZ, Cliente ABC'
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
            'color_hex': forms.TextInput(
                attrs={
                    'type': 'color',
                    'class': 'form-control form-control-color',
                    'style': 'width: 60px; height: 40px;'
                }
            ),
            'activo': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            )
        }
        labels = {
            'nombre': 'Nombre del proyecto',
            'descripcion': 'Descripción',
            'cliente': 'Cliente',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de finalización',
            'color_hex': 'Color del proyecto',
            'activo': 'Proyecto activo'
        }
        help_texts = {
            'nombre': 'Nombre descriptivo para identificar el proyecto',
            'descripcion': 'Opcional: Descripción detallada del proyecto',
            'cliente': 'Opcional: Nombre del cliente o empresa',
            'fecha_inicio': 'Opcional: Fecha planificada de inicio del proyecto',
            'fecha_fin': 'Opcional: Fecha planificada de finalización del proyecto',
            'color_hex': 'Color para identificar visualmente el proyecto en calendarios y reportes',
            'activo': 'Los proyectos inactivos no aparecen en formularios de registro de horas'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer color por defecto si es un nuevo proyecto
        if not self.instance.pk:
            self.fields['color_hex'].initial = '#007bff'  # Azul por defecto

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del proyecto es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres")
        
        # Verificar que no exista otro proyecto con el mismo nombre para el usuario
        if self.instance.usuario_id:
            existing = Proyecto.objects.filter(
                usuario=self.instance.usuario,
                nombre__iexact=nombre.strip()
            ).exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError("Ya existe un proyecto con este nombre")
        
        return nombre.strip()

    def clean_color_hex(self):
        color_hex = self.cleaned_data.get('color_hex')
        
        if not color_hex:
            return '#007bff'  # Color por defecto
        
        # Validar formato hexadecimal
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color_hex):
            raise ValidationError("El color debe estar en formato hexadecimal válido (ej: #FF0000)")
        
        return color_hex.upper()

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            # Validar que fecha_fin sea posterior a fecha_inicio
            if fecha_fin <= fecha_inicio:
                raise ValidationError("La fecha de finalización debe ser posterior a la fecha de inicio")
            
            # Validar que el proyecto no sea demasiado largo (más de 5 años)
            if (fecha_fin - fecha_inicio).days > 1825:  # 5 años
                raise ValidationError("La duración del proyecto no puede ser mayor a 5 años")
        
        # Validar fechas muy antiguas o muy futuras
        if fecha_inicio:
            hace_dos_años = date.today() - timedelta(days=730)
            en_cinco_años = date.today() + timedelta(days=1825)
            
            if fecha_inicio < hace_dos_años:
                raise ValidationError("La fecha de inicio no puede ser de hace más de 2 años")
            
            if fecha_inicio > en_cinco_años:
                raise ValidationError("La fecha de inicio no puede ser de más de 5 años en el futuro")
        
        return cleaned_data


class ProyectoFiltroForm(forms.Form):
    """Formulario para filtrar proyectos"""
    
    ESTADO_CHOICES = [
        ('', 'Todos los estados'),
        ('activo', 'Solo activos'),
        ('inactivo', 'Solo inactivos')
    ]
    
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Buscar por nombre...'
            }
        ),
        label='Nombre'
    )
    
    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Buscar por cliente...'
            }
        ),
        label='Cliente'
    )
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        ),
        label='Estado'
    )
    
    fecha_inicio_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Inicio desde'
    )
    
    fecha_inicio_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        label='Inicio hasta'
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio_desde = cleaned_data.get('fecha_inicio_desde')
        fecha_inicio_hasta = cleaned_data.get('fecha_inicio_hasta')
        
        if fecha_inicio_desde and fecha_inicio_hasta:
            if fecha_inicio_desde > fecha_inicio_hasta:
                raise ValidationError("La fecha 'desde' no puede ser posterior a la fecha 'hasta'")
        
        return cleaned_data


class ProyectoRapidoForm(forms.ModelForm):
    """Formulario simplificado para creación rápida de proyectos"""
    
    class Meta:
        model = Proyecto
        fields = ['nombre', 'cliente', 'color_hex']
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del proyecto',
                    'required': True
                }
            ),
            'cliente': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Cliente (opcional)'
                }
            ),
            'color_hex': forms.TextInput(
                attrs={
                    'type': 'color',
                    'class': 'form-control form-control-color',
                    'style': 'width: 50px; height: 35px;',
                    'value': '#007bff'
                }
            )
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del proyecto es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres")
        
        return nombre.strip()


class ProyectoImportForm(forms.Form):
    """Formulario para importar proyectos desde archivo CSV"""
    
    archivo_csv = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': '.csv'
            }
        ),
        label='Archivo CSV',
        help_text='Seleccione un archivo CSV con los proyectos a importar'
    )
    
    sobrescribir = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        ),
        label='Sobrescribir proyectos existentes',
        help_text='Si está marcado, actualizará proyectos con nombres duplicados'
    )

    def clean_archivo_csv(self):
        archivo = self.cleaned_data.get('archivo_csv')
        
        if not archivo:
            raise ValidationError("Debe seleccionar un archivo")
        
        if not archivo.name.endswith('.csv'):
            raise ValidationError("El archivo debe tener extensión .csv")
        
        if archivo.size > 1024 * 1024:  # 1MB
            raise ValidationError("El archivo no puede ser mayor a 1MB")
        
        return archivo
