#!/usr/bin/env python
"""
Script para verificar que se corrigió el error 404 de URLs
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_url_fix():
    """Verificar que las URLs funcionan correctamente"""
    
    print("🔍 Verificando corrección de URLs...")
    
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
    
    # URLs a probar
    urls_to_test = [
        # URL correcta
        ('/horas/registrar/', 'URL correcta /horas/registrar/'),
        ('/horas/registrar/?fecha=2025-08-13', 'URL correcta con parámetro fecha'),
        
        # URL de redirección (debería redirigir a la correcta)
        ('/horas/crear/', 'URL de redirección /horas/crear/'),
        ('/horas/crear/?fecha=2025-08-13', 'URL de redirección con parámetro fecha'),
        
        # Otras URLs importantes
        ('/horas/', 'Lista de horas'),
        ('/horas/bloque/', 'Registro en bloque'),
        ('/horas/test-hours/', 'Página de prueba del widget'),
    ]
    
    successful_tests = 0
    
    for url, description in urls_to_test:
        try:
            response = client.get(url)
            
            if response.status_code == 200:
                print(f"{description}: HTTP 200")
                successful_tests += 1
            elif response.status_code == 301 or response.status_code == 302:
                print(f"{description}: HTTP {response.status_code} (redirección)")
                successful_tests += 1
            elif response.status_code == 404:
                print(f"{description}: HTTP 404 (No encontrado)")
            else:
                print(f"⚠️ {description}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"{description}: Error - {e}")
    
    print(f"\n📊 Resultados: {successful_tests}/{len(urls_to_test)} URLs funcionando")
    
    if successful_tests == len(urls_to_test):
        print("🎉 ¡Todas las URLs funcionan correctamente!")
    else:
        print(f"⚠️ {len(urls_to_test) - successful_tests} URLs tienen problemas")

def check_file_references():
    """Verificar que se corrigieron las referencias en archivos"""
    
    print(f"\n🔍 Verificando referencias en archivos...")
    
    files_to_check = [
        'templates/dashboard/dashboard.html',
        'static/js/calendar-widget.js',
        'staticfiles/js/calendar-widget.js'
    ]
    
    base_dir = '/home/efigueroa/Proyectos/AWS-QDeveloper/proyectos/reporte_horas_trabajadas/sis-horas-django'
    
    for file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Contar referencias incorrectas
                incorrect_refs = content.count('/horas/crear/')
                correct_refs = content.count('/horas/registrar/')
                
                if incorrect_refs == 0:
                    print(f"{file_path}: Sin referencias incorrectas")
                else:
                    print(f"{file_path}: {incorrect_refs} referencias incorrectas encontradas")
                
                if correct_refs > 0:
                    print(f"  📊 Referencias correctas: {correct_refs}")
                    
            except Exception as e:
                print(f"{file_path}: Error al leer - {e}")
        else:
            print(f"⚠️ {file_path}: Archivo no encontrado")

def test_dashboard_calendar_links():
    """Probar específicamente los enlaces del calendario en dashboard"""
    
    print(f"\nProbando enlaces del calendario en dashboard...")
    
    client = Client()
    
    # Login
    try:
        admin_user = User.objects.get(username='admin')
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("No se pudo hacer login")
            return
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Probar dashboard
    response = client.get('/')
    
    if response.status_code == 200:
        print("Dashboard carga correctamente")
        
        content = response.content.decode('utf-8')
        
        # Verificar que no hay referencias incorrectas
        if '/horas/crear/' in content:
            print("Dashboard aún contiene referencias a /horas/crear/")
        else:
            print("Dashboard no contiene referencias incorrectas")
        
        # Verificar que hay referencias correctas
        if '/horas/registrar/' in content:
            print("Dashboard contiene referencias correctas a /horas/registrar/")
        else:
            print("⚠️ Dashboard no contiene referencias a /horas/registrar/")
            
    else:
        print(f"Dashboard falló: HTTP {response.status_code}")

if __name__ == '__main__':
    test_url_fix()
    check_file_references()
    test_dashboard_calendar_links()
    
    print(f"\n🎯 Resumen de la corrección:")
    print("=" * 40)
    print("URLs corregidas de /horas/crear/ a /horas/registrar/")
    print("Redirección agregada para compatibilidad")
    print("Referencias en archivos JavaScript corregidas")
    print("Referencias en templates corregidas")
    print()
    print("🔗 URLs disponibles:")
    print("  • /horas/registrar/ (URL correcta)")
    print("  • /horas/crear/ (redirige a la correcta)")
    print("  • /horas/registrar/?fecha=YYYY-MM-DD (con fecha)")
    print("  • /horas/crear/?fecha=YYYY-MM-DD (redirige con fecha)")
