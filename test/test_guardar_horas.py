#!/usr/bin/env python
"""
Script para probar y corregir el error al guardar horas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from apps.horas.forms import RegistroHoraForm
from apps.proyectos.models import Proyecto
from apps.horas.models import RegistroHora
from datetime import date, timedelta

def test_save_hours_error():
    """Probar el error al guardar horas"""
    
    print("🔍 Diagnosticando error al guardar horas...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario: {admin_user.username}")
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Obtener o crear proyecto
    proyecto, created = Proyecto.objects.get_or_create(
        nombre='Proyecto Test Guardar',
        usuario=admin_user,
        defaults={
            'descripcion': 'Proyecto para probar guardado de horas',
            'activo': True
        }
    )
    
    if created:
        print(f"Proyecto creado: {proyecto.nombre}")
    else:
        print(f"Proyecto existente: {proyecto.nombre}")
    
    # Usar una fecha de día laboral (lunes)
    today = date.today()
    # Encontrar el próximo lunes
    days_ahead = 0 - today.weekday()  # 0 = lunes
    if days_ahead <= 0:  # Si hoy es lunes o después
        days_ahead += 7
    next_monday = today + timedelta(days_ahead)
    
    # Si el próximo lunes es muy lejos, usar el lunes pasado
    if days_ahead > 3:
        next_monday = today - timedelta(days=today.weekday())
    
    test_date = next_monday
    print(f"Fecha de prueba: {test_date} ({test_date.strftime('%A')})")
    
    # Casos de prueba
    test_cases = [
        {
            'data': {
                'fecha': test_date,
                'proyecto': proyecto.id,
                'horas': '1.5',  # Formato decimal
                'descripcion': 'Prueba formato decimal',
                'tipo_tarea': 'tarea'
            },
            'description': 'Formato decimal 1.5'
        },
        {
            'data': {
                'fecha': test_date,
                'proyecto': proyecto.id,
                'horas': '01:30',  # Formato tiempo
                'descripcion': 'Prueba formato tiempo',
                'tipo_tarea': 'reunion'
            },
            'description': 'Formato tiempo 01:30'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Prueba {i}: {test_case['description']}")
        
        try:
            # Crear formulario
            form = RegistroHoraForm(data=test_case['data'], user=admin_user)
            
            print(f"  Datos del formulario: {test_case['data']}")
            
            # Verificar si es válido
            if form.is_valid():
                print("  Formulario válido")
                
                # Intentar guardar
                try:
                    registro = form.save()
                    print(f"  💾 Guardado exitoso: ID {registro.id}")
                    print(f"  📊 Horas guardadas: {registro.horas}")
                    
                    # Limpiar para próxima prueba
                    registro.delete()
                    print("  🗑️ Registro eliminado para próxima prueba")
                    
                except Exception as save_error:
                    print(f"  Error al guardar: {save_error}")
                    print(f"  🔍 Tipo de error: {type(save_error).__name__}")
                    
                    # Mostrar traceback completo
                    import traceback
                    print("  Traceback completo:")
                    traceback.print_exc()
                    
            else:
                print("  Formulario inválido:")
                for field, errors in form.errors.items():
                    print(f"    - {field}: {errors}")
                
                # Mostrar errores no de campo
                if form.non_field_errors():
                    print(f"    - Errores generales: {form.non_field_errors()}")
                    
        except Exception as form_error:
            print(f"  Error al crear formulario: {form_error}")
            import traceback
            traceback.print_exc()

def test_web_interface():
    """Probar interfaz web para guardar horas"""
    
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
    
    # Obtener proyecto
    try:
        proyecto = Proyecto.objects.filter(usuario=admin_user, activo=True).first()
        if not proyecto:
            print("No hay proyectos activos")
            return
        print(f"Proyecto para prueba: {proyecto.nombre}")
    except Exception as e:
        print(f"Error al obtener proyecto: {e}")
        return
    
    # Usar fecha de día laboral
    today = date.today()
    # Usar lunes de esta semana o anterior
    days_back = today.weekday()  # 0 = lunes
    test_date = today - timedelta(days=days_back)
    
    print(f"Fecha de prueba web: {test_date}")
    
    # Datos de prueba
    post_data = {
        'fecha': test_date.isoformat(),
        'proyecto': proyecto.id,
        'horas': '1.5',
        'descripcion': 'Prueba desde interfaz web',
        'tipo_tarea': 'tarea'
    }
    
    print(f"📝 Datos POST: {post_data}")
    
    try:
        # Hacer POST al formulario
        response = client.post(reverse('horas:hora_create'), data=post_data)
        
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 302:
            print("Redirección exitosa (guardado correcto)")
            
            # Verificar que se guardó
            registro = RegistroHora.objects.filter(
                usuario=admin_user,
                fecha=test_date,
                descripcion='Prueba desde interfaz web'
            ).first()
            
            if registro:
                print(f"Registro encontrado en BD: {registro.horas} horas")
                # Limpiar
                registro.delete()
                print("🗑️ Registro eliminado")
            else:
                print("Registro no encontrado en BD")
                
        elif response.status_code == 200:
            print("⚠️ Formulario devuelto (posibles errores)")
            
            # Buscar errores en el contenido
            content = response.content.decode('utf-8')
            if 'error' in content.lower() or 'invalid' in content.lower():
                print("Posibles errores en el formulario")
            else:
                print("ℹ️ Formulario mostrado sin errores aparentes")
                
        else:
            print(f"Error HTTP: {response.status_code}")
            
    except Exception as web_error:
        print(f"Error en interfaz web: {web_error}")
        import traceback
        traceback.print_exc()

def check_field_compatibility():
    """Verificar compatibilidad del campo personalizado"""
    
    print("\n🔧 Verificando compatibilidad del campo personalizado...")
    
    from apps.horas.fields import HoursField, convert_hours_input
    
    # Probar función de conversión
    test_values = [
        ('1.5', 1.5),
        ('01:30', 1.5),
        ('2:00', 2.0),
        ('00:30', 0.5),
        ('8.0', 8.0),
        ('08:00', 8.0)
    ]
    
    print("🔄 Probando conversión de valores:")
    for input_val, expected in test_values:
        try:
            result = convert_hours_input(input_val)
            if result == expected:
                print(f"  '{input_val}' → {result}")
            else:
                print(f"  '{input_val}' → {result} (esperado: {expected})")
        except Exception as e:
            print(f"  '{input_val}' → Error: {e}")
    
    # Probar campo directamente
    print("\n🔧 Probando campo HoursField:")
    field = HoursField()
    
    for input_val, expected in test_values:
        try:
            result = field.to_python(input_val)
            if result == expected:
                print(f"  Campo: '{input_val}' → {result}")
            else:
                print(f"  Campo: '{input_val}' → {result} (esperado: {expected})")
        except Exception as e:
            print(f"  Campo: '{input_val}' → Error: {e}")

if __name__ == '__main__':
    test_save_hours_error()
    test_web_interface()
    check_field_compatibility()
    
    print("\n🎯 Diagnóstico completado")
    print("=" * 50)
    print("Si hay errores, revisar:")
    print("1. Importaciones en forms.py")
    print("2. Compatibilidad del campo personalizado")
    print("3. Validaciones de fecha (fines de semana/feriados)")
    print("4. Configuración de la base de datos")
    print("5. Logs del servidor Django")
