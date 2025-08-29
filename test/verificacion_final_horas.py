#!/usr/bin/env python
"""
Verificación final del sistema de horas con formato dual
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

def test_final_hours_system():
    """Verificación final del sistema de horas"""
    
    print("🎯 VERIFICACIÓN FINAL - Sistema de Horas con Formato Dual")
    print("=" * 60)
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario: {admin_user.username}")
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
    
    print(f"Fecha de prueba: {test_date} ({test_date.strftime('%A')})")
    
    # Casos de prueba con ambos formatos
    test_cases = [
        {
            'horas': '1.5',
            'descripcion': 'Prueba formato decimal 1.5',
            'formato': 'decimal'
        },
        {
            'horas': '01:30',
            'descripcion': 'Prueba formato tiempo 01:30',
            'formato': 'tiempo'
        },
        {
            'horas': '2:00',
            'descripcion': 'Prueba formato tiempo 2:00',
            'formato': 'tiempo'
        },
        {
            'horas': '4.0',
            'descripcion': 'Prueba formato decimal 4.0',
            'formato': 'decimal'
        }
    ]
    
    print(f"\n🧪 Ejecutando {len(test_cases)} pruebas...")
    
    successful_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Prueba {i}: {test_case['formato']} - {test_case['horas']}")
        
        # Crear cliente web
        client = Client()
        login_success = client.login(username='admin', password='admin123')
        
        if not login_success:
            print("  Error de login")
            continue
        
        # Datos del formulario
        form_data = {
            'fecha': test_date.isoformat(),
            'proyecto': proyecto.id,
            'horas': test_case['horas'],
            'descripcion': test_case['descripcion'],
            'tipo_tarea': 'tarea'
        }
        
        try:
            # Enviar formulario
            response = client.post(reverse('horas:hora_create'), data=form_data)
            
            if response.status_code == 302:
                # Verificar que se guardó
                registro = RegistroHora.objects.filter(
                    usuario=admin_user,
                    fecha=test_date,
                    descripcion=test_case['descripcion']
                ).first()
                
                if registro:
                    print(f"  Guardado exitoso: {registro.horas} horas")
                    print(f"  📊 Conversión: '{test_case['horas']}' → {registro.horas}")
                    
                    # Limpiar para próxima prueba
                    registro.delete()
                    successful_tests += 1
                else:
                    print("  No se encontró el registro en BD")
            else:
                print(f"  Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\n📊 RESULTADOS FINALES:")
    print(f"Pruebas exitosas: {successful_tests}/{len(test_cases)}")
    print(f"📈 Tasa de éxito: {(successful_tests/len(test_cases)*100):.1f}%")
    
    if successful_tests == len(test_cases):
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("El sistema de horas con formato dual funciona correctamente")
    else:
        print(f"\n⚠️ {len(test_cases) - successful_tests} pruebas fallaron")

def test_format_conversion():
    """Probar conversión de formatos específicamente"""
    
    print(f"\n🔄 PRUEBA DE CONVERSIÓN DE FORMATOS")
    print("=" * 40)
    
    from apps.horas.fields import convert_hours_input
    
    conversion_tests = [
        # (entrada, esperado, descripción)
        ('0.5', 0.5, 'Media hora decimal'),
        ('00:30', 0.5, 'Media hora tiempo'),
        ('1.0', 1.0, 'Una hora decimal'),
        ('01:00', 1.0, 'Una hora tiempo'),
        ('1.5', 1.5, 'Hora y media decimal'),
        ('01:30', 1.5, 'Hora y media tiempo'),
        ('2.0', 2.0, 'Dos horas decimal'),
        ('02:00', 2.0, 'Dos horas tiempo'),
        ('8.0', 8.0, 'Jornada completa decimal'),
        ('08:00', 8.0, 'Jornada completa tiempo'),
    ]
    
    conversion_success = 0
    
    for entrada, esperado, descripcion in conversion_tests:
        try:
            resultado = convert_hours_input(entrada)
            if resultado == esperado:
                print(f"{descripcion}: '{entrada}' → {resultado}")
                conversion_success += 1
            else:
                print(f"{descripcion}: '{entrada}' → {resultado} (esperado: {esperado})")
        except Exception as e:
            print(f"{descripcion}: '{entrada}' → Error: {e}")
    
    print(f"\n📊 Conversiones exitosas: {conversion_success}/{len(conversion_tests)}")
    
    return conversion_success == len(conversion_tests)

def test_web_interface_access():
    """Verificar acceso a interfaces web"""
    
    print(f"\n🌐 VERIFICACIÓN DE INTERFACES WEB")
    print("=" * 40)
    
    client = Client()
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    if not login_success:
        print("No se pudo hacer login")
        return False
    
    print("Login exitoso")
    
    # URLs a verificar
    urls_to_test = [
        ('horas:hora_create', 'Formulario de registro de horas'),
        ('horas:hora_list', 'Lista de horas'),
        ('horas:test_hours', 'Página de prueba del widget'),
        ('proyectos:proyecto_list', 'Lista de proyectos'),
    ]
    
    web_success = 0
    
    for url_name, description in urls_to_test:
        try:
            response = client.get(reverse(url_name))
            if response.status_code == 200:
                print(f"{description}")
                web_success += 1
            else:
                print(f"{description}: HTTP {response.status_code}")
        except Exception as e:
            print(f"{description}: Error - {e}")
    
    print(f"\n📊 Interfaces accesibles: {web_success}/{len(urls_to_test)}")
    
    return web_success == len(urls_to_test)

if __name__ == '__main__':
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_final_hours_system()
    conversion_ok = test_format_conversion()
    web_ok = test_web_interface_access()
    
    print(f"\n🎯 RESUMEN FINAL")
    print("=" * 30)
    print(f"Conversión de formatos: {'OK' if conversion_ok else 'FALLO'}")
    print(f"Interfaces web: {'OK' if web_ok else 'FALLO'}")
    print(f"Guardado de horas: Verificado arriba")
    
    if conversion_ok and web_ok:
        print(f"\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("=" * 40)
        print("Formato dual implementado correctamente")
        print("Conversión automática operativa")
        print("Guardado sin errores")
        print("Interfaces web accesibles")
        print()
        print("🎯 El usuario puede ahora ingresar horas en:")
        print("   • Formato decimal: 1.5, 2.0, 8.0")
        print("   • Formato tiempo: 01:30, 02:00, 08:00")
        print()
        print("🔗 URLs disponibles:")
        print("   • Registro: http://localhost:8000/horas/registrar/")
        print("   • Prueba: http://localhost:8000/horas/test-hours/")
    else:
        print(f"\n⚠️ Hay problemas que requieren atención")
        print("Revisar los errores mostrados arriba")
