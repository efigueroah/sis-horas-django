from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Personalizar placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
        self.fields['email'].widget.attrs['placeholder'] = 'correo@ejemplo.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Apellido'
        self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar contraseña'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil de usuario"""
    
    class Meta:
        model = UserProfile
        fields = [
            'nombre_completo',
            'horas_max_dia',
            'timezone',
            'formato_fecha',
            'tema'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'horas_max_dia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 24
            }),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
            'formato_fecha': forms.Select(attrs={'class': 'form-select'}),
            'tema': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar labels
        self.fields['nombre_completo'].label = 'Nombre Completo'
        self.fields['horas_max_dia'].label = 'Horas Máximas por Día'
        self.fields['timezone'].label = 'Zona Horaria'
        self.fields['formato_fecha'].label = 'Formato de Fecha'
        self.fields['tema'].label = 'Tema de la Interfaz'
        
        # Help texts
        self.fields['horas_max_dia'].help_text = 'Número máximo de horas que puedes registrar por día'
        self.fields['timezone'].help_text = 'Tu zona horaria local'


class UserBasicInfoForm(forms.ModelForm):
    """Formulario para información básica del usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['email'].label = 'Correo Electrónico'
        self.fields['email'].required = True
