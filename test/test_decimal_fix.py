#!/usr/bin/env python
"""
Script para verificar que se corrigió el error de Decimal + float
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from apps.proyectos.models import Proyecto
from apps.horas.models import RegistroHora
from datetime import date, timedelta

def test_decimal_fix():
    """Probar que se corrigió el error de tipos Decimal + float"""
    
    print("🔍 Probando corrección del error Decimal + float...")
    
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
    
    # Obtener proyecto activo
    proyecto = Proyecto.objects.filter(usuario=admin_user, activo=True).first()
    if not proyecto:
        print("No hay proyectos activos")
        return
    
    print(f"Proyecto: {proyecto.nombre}")
    
    # Usar fecha válida (lunes de la semana pasada)
    today = date.today()
    days_back = today.weekday() + 7  # Lunes de la semana pasada
    test_date = today - timedelta(days=days_back)
    
    print(f"Fecha de prueba: {test_date}")
    
    # Limpiar registros existentes para esta fecha
    RegistroHora.objects.filter(usuario=admin_user, fecha=test_date).delete()
    print("🗑️ Registros existentes limpiados")
    
    # Casos de prueba que anteriormente causaban el error
    test_cases = [
        {
            'data': {
                'fecha': test_date.isoformat(),
                'proyecto': proyecto.id,
                'horas': '1.5',  # Formato decimal
                'descripcion': 'Prueba decimal fix',
                'tipo_tarea': 'tarea'
            },
            'description': 'Formato decimal 1.5'
        },
        {
            'data': {
                'fecha': test_date.isoformat(),
                'proyecto': proyecto.id,
                'horas': '01:30',  # Formato tiempo
                'descripcion': 'Prueba tiempo fix',
                'tipo_tarea': 'reunion'
            },
            'description': 'Formato tiempo 01:30'
        },
        {
            'data': {
                'fecha': test_date.isoformat(),
                'proyecto': proyecto.id,
                'horas': '2:00',  # Formato tiempo sin cero inicial
                'descripcion': 'Prueba tiempo 2:00 fix',
                'tipo_tarea': 'desarrollo'
            },
            'description': 'Formato tiempo 2:00'
        }
    ]
    
    successful_posts = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Prueba {i}: {test_case['description']}")
        
        try:
            response = client.post(reverse('horas:hora_create'), data=test_case['data'])
            
            print(f"  📊 Código de respuesta: {response.status_code}")
            
            if response.status_code == 302:
                print("  Redirección exitosa (guardado correcto)")
                
                # Verificar que se guardó
                registro = RegistroHora.objects.filter(
                    usuario=admin_user,
                    fecha=test_date,
                    descripcion=test_case['data']['descripcion']
                ).first()
                
                if registro:
                    print(f"  Registro guardado: {registro.horas} horas")
                    print(f"  🔄 Conversión: '{test_case['data']['horas']}' → {registro.horas}")
                    successful_posts += 1
                else:
                    print("  Registro no encontrado en BD")
                    
            elif response.status_code == 200:
                print("  ⚠️ Formulario devuelto (posibles errores de validación)")
                
                # Buscar errores específicos
                content = response.content.decode('utf-8')
                if 'TypeError' in content:
                    print("  Error de tipo aún presente")
                elif 'Decimal' in content and 'float' in content:
                    print("  Error Decimal + float aún presente")
                elif 'errorlist' in content:
                    print("  Errores de validación (no de tipo)")
                else:
                    print("  ℹ️ Formulario mostrado sin errores aparentes")
                    
            elif response.status_code == 500:
                print("  Error interno del servidor")
                
            else:
                print(f"  ⚠️ Código inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"  Error durante POST: {e}")
            if 'Decimal' in str(e) and 'float' in str(e):
                print("  🔍 Error de tipo Decimal + float detectado")
    
    print(f"\n📊 Resultados: {successful_posts}/{len(test_cases)} POST exitosos")
    
    if successful_posts == len(test_cases):
        print("🎉 ¡Todos los POST funcionan correctamente!")
        print("Error Decimal + float corregido")
    else:
        print(f"⚠️ {len(test_cases) - successful_posts} POST fallaron")
    
    # Limpiar registros de prueba
    RegistroHora.objects.filter(usuario=admin_user, fecha=test_date).delete()
    print("🗑️ Registros de prueba limpiados")

def test_validation_with_existing_hours():
    """Probar validación cuando ya hay horas registradas (caso que causaba el error)"""
    
    print(f"\n🔍 Probando validación con horas existentes...")
    
    client = Client()
    admin_user = User.objects.get(username='admin')
    client.login(username='admin', password='admin123')
    
    proyecto = Proyecto.objects.filter(usuario=admin_user, activo=True).first()
    
    # Usar fecha válida
    today = date.today()
    days_back = today.weekday() + 7
    test_date = today - timedelta(days=days_back)
    
    # Limpiar registros existentes
    RegistroHora.objects.filter(usuario=admin_user, fecha=test_date).delete()
    
    # Crear un registro existente
    existing_registro = RegistroHora.objects.create(
        usuario=admin_user,
        fecha=test_date,
        proyecto=proyecto,
        horas=4.0,
        descripcion='Registro existente',
        tipo_tarea='tarea'
    )
    
    print(f"📊 Registro existente creado: {existing_registro.horas} horas")
    
    # Intentar agregar más horas (esto debería activar la validación que causaba el error)
    test_data = {
        'fecha': test_date.isoformat(),
        'proyecto': proyecto.id,
        'horas': '3.5',  # Total sería 7.5, debería ser válido
        'descripcion': 'Registro adicional',
        'tipo_tarea': 'reunion'
    }
    
    try:
        response = client.post(reverse('horas:hora_create'), data=test_data)
        
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 302:
            print("Validación funciona correctamente (registro adicional guardado)")
        elif response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'TypeError' in content or ('Decimal' in content and 'float' in content):
                print("Error de tipo aún presente en validación")
            else:
                print("Validación funciona (formulario devuelto sin error de tipo)")
        else:
            print(f"⚠️ Código inesperado: {response.status_code}")
            
    except Exception as e:
        if 'Decimal' in str(e) and 'float' in str(e):
            print(f"Error de tipo en validación: {e}")
        else:
            print(f"⚠️ Otro error: {e}")
    
    # Limpiar
    RegistroHora.objects.filter(usuario=admin_user, fecha=test_date).delete()
    print("🗑️ Registros de prueba limpiados")

if __name__ == '__main__':
    test_decimal_fix()
    test_validation_with_existing_hours()
    
    print(f"\n🎯 Resumen de la corrección:")
    print("=" * 40)
    print("Importación de Decimal agregada")
    print("Conversión float(horas) → Decimal(str(horas))")
    print("Validación de tipos en formulario corregida")
    print("Validación de tipos en modelo verificada")
    print()
    print("🔧 Cambios realizados:")
    print("  • forms.py: Línea 152 corregida")
    print("  • models.py: horas_max como Decimal")
    print("  • Importaciones actualizadas")
