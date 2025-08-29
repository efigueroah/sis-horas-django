#!/usr/bin/env python
"""
Script para probar el nuevo sistema de formato de horas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from apps.horas.widgets import HoursField
from apps.horas.forms import RegistroHoraForm
from apps.proyectos.models import Proyecto
from datetime import date

def test_hours_field():
    """Probar el campo personalizado de horas"""
    
    print("🔍 Probando campo personalizado de horas...")
    
    # Crear instancia del campo
    field = HoursField()
    
    # Casos de prueba
    test_cases = [
        # Formato decimal válido
        ('1.5', 1.5, True, 'Decimal válido'),
        ('2.0', 2.0, True, 'Decimal entero'),
        ('0.5', 0.5, True, 'Mínimo válido'),
        ('8.0', 8.0, True, 'Jornada completa'),
        
        # Formato tiempo válido
        ('01:30', 1.5, True, 'Tiempo HH:MM'),
        ('02:00', 2.0, True, 'Tiempo horas exactas'),
        ('00:30', 0.5, True, 'Tiempo mínimo'),
        ('08:00', 8.0, True, 'Tiempo jornada completa'),
        ('1:30', 1.5, True, 'Tiempo H:MM'),
        
        # Casos inválidos
        ('0.25', None, False, 'Menos del mínimo'),
        ('13.0', None, False, 'Más del máximo'),
        ('1.25', None, False, 'No múltiplo de 0.5'),
        ('25:00', None, False, 'Horas inválidas'),
        ('01:70', None, False, 'Minutos inválidos'),
        ('abc', None, False, 'Texto inválido'),
        ('', None, True, 'Vacío (válido para campo opcional)'),
    ]
    
    for input_value, expected_output, should_be_valid, description in test_cases:
        try:
            result = field.to_python(input_value)
            
            if should_be_valid:
                if result == expected_output:
                    print(f"  {description}: '{input_value}' → {result}")
                else:
                    print(f"  {description}: '{input_value}' → {result} (esperado: {expected_output})")
            else:
                print(f"  {description}: '{input_value}' debería ser inválido pero retornó {result}")
                
        except Exception as e:
            if should_be_valid:
                print(f"  {description}: '{input_value}' → Error: {e}")
            else:
                print(f"  {description}: '{input_value}' → Error esperado: {e}")

def test_form_integration():
    """Probar integración con formulario"""
    
    print("\nProbando integración con formulario...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario: {admin_user.username}")
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Obtener o crear proyecto
    proyecto, created = Proyecto.objects.get_or_create(
        nombre='Proyecto de Prueba Horas',
        usuario=admin_user,
        defaults={
            'descripcion': 'Proyecto para probar formato de horas',
            'activo': True
        }
    )
    
    if created:
        print(f"Proyecto creado: {proyecto.nombre}")
    else:
        print(f"Proyecto existente: {proyecto.nombre}")
    
    # Casos de prueba para formulario
    form_test_cases = [
        {
            'data': {
                'fecha': date.today(),
                'proyecto': proyecto.id,
                'horas': '1.5',  # Formato decimal
                'descripcion': 'Prueba formato decimal',
                'tipo_tarea': 'tarea'
            },
            'should_be_valid': True,
            'description': 'Formato decimal 1.5'
        },
        {
            'data': {
                'fecha': date.today(),
                'proyecto': proyecto.id,
                'horas': '01:30',  # Formato tiempo
                'descripcion': 'Prueba formato tiempo',
                'tipo_tarea': 'tarea'
            },
            'should_be_valid': True,
            'description': 'Formato tiempo 01:30'
        },
        {
            'data': {
                'fecha': date.today(),
                'proyecto': proyecto.id,
                'horas': '2:00',  # Formato tiempo sin cero inicial
                'descripcion': 'Prueba formato tiempo sin cero',
                'tipo_tarea': 'tarea'
            },
            'should_be_valid': True,
            'description': 'Formato tiempo 2:00'
        },
        {
            'data': {
                'fecha': date.today(),
                'proyecto': proyecto.id,
                'horas': '1.25',  # No múltiplo de 0.5
                'descripcion': 'Prueba formato inválido',
                'tipo_tarea': 'tarea'
            },
            'should_be_valid': False,
            'description': 'Formato inválido 1.25'
        }
    ]
    
    for test_case in form_test_cases:
        form = RegistroHoraForm(data=test_case['data'], user=admin_user)
        
        if form.is_valid():
            if test_case['should_be_valid']:
                horas_value = form.cleaned_data['horas']
                print(f"  {test_case['description']}: Válido → {horas_value} horas")
            else:
                print(f"  {test_case['description']}: Debería ser inválido pero es válido")
        else:
            if test_case['should_be_valid']:
                print(f"  {test_case['description']}: Debería ser válido pero tiene errores:")
                for field, errors in form.errors.items():
                    print(f"    - {field}: {errors}")
            else:
                print(f"  {test_case['description']}: Inválido como esperado")

def test_web_interface():
    """Probar interfaz web"""
    
    print("\n🌐 Probando interfaz web...")
    
    # Crear cliente de prueba
    client = Client()
    
    # Login
    try:
        admin_user = User.objects.get(username='admin')
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("No se pudo hacer login")
            return
        print("Login exitoso")
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Probar página de registro de horas
    print("\n📝 Probando página de registro de horas...")
    response = client.get(reverse('horas:hora_create'))
    
    if response.status_code == 200:
        print("Página de registro carga correctamente")
        
        content = response.content.decode('utf-8')
        
        # Verificar elementos del widget personalizado
        widget_checks = [
            ('hours-widget.css', 'CSS del widget de horas'),
            ('hours-widget.js', 'JavaScript del widget de horas'),
            ('hours-input', 'Clase CSS del input de horas'),
            ('HoursField', 'Campo personalizado de horas'),
            ('Ingrese horas en formato decimal', 'Texto de ayuda actualizado')
        ]
        
        for check, description in widget_checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
    else:
        print(f"Página de registro falló: {response.status_code}")

def verify_static_files():
    """Verificar archivos estáticos"""
    
    print("\nVerificando archivos estáticos...")
    
    import os
    from django.conf import settings
    
    static_files = [
        ('css/hours-widget.css', 'CSS del widget de horas'),
        ('js/hours-widget.js', 'JavaScript del widget de horas')
    ]
    
    for file_path, description in static_files:
        full_path = os.path.join(settings.BASE_DIR, 'static', file_path)
        if os.path.exists(full_path):
            print(f"  {description}")
            
            # Verificar contenido básico
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'hours' in content.lower():
                print(f"    Contiene código relacionado con horas")
            else:
                print(f"    No contiene código relacionado con horas")
        else:
            print(f"  {description} - Archivo no encontrado")

if __name__ == '__main__':
    test_hours_field()
    test_form_integration()
    test_web_interface()
    verify_static_files()
    
    print("\n🎉 Resumen de Mejoras Implementadas:")
    print("=" * 50)
    print("Campo personalizado HoursField")
    print("  - Soporte para formato decimal (1.5)")
    print("  - Soporte para formato tiempo (01:30)")
    print("  - Conversión automática entre formatos")
    print("  - Validaciones mejoradas")
    print()
    print("Widget personalizado HoursWidget")
    print("  - Interfaz visual mejorada")
    print("  - Ejemplos rápidos de uso")
    print("  - Validación en tiempo real")
    print("  - Conversión visual entre formatos")
    print()
    print("Integración completa")
    print("  - Formularios actualizados")
    print("  - Templates con CSS/JS incluidos")
    print("  - Compatibilidad con sistema existente")
    print()
    print("🎯 Para probar manualmente:")
    print("1. Ir a: http://localhost:8000/horas/registrar/")
    print("2. Probar ingresar: 1.5 (decimal)")
    print("3. Probar ingresar: 01:30 (tiempo)")
    print("4. Verificar conversión automática")
    print("5. Verificar validaciones en tiempo real")
