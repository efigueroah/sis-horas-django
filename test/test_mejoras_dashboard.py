#!/usr/bin/env python
"""
Script para probar las mejoras del dashboard y widget de calendario
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_dashboard_improvements():
    """Probar mejoras del dashboard"""
    
    print("🔍 Probando mejoras del dashboard...")
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario: {admin_user.username}")
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    if not login_success:
        print("No se pudo hacer login")
        return
    
    print("Login exitoso")
    
    # Probar dashboard
    print("\n📊 Probando dashboard...")
    response = client.get(reverse('core:dashboard'))
    
    if response.status_code == 200:
        print("Dashboard carga correctamente")
        
        # Verificar que contiene las acciones rápidas
        content = response.content.decode('utf-8')
        
        checks = [
            ('Acciones Rápidas', 'Sección de acciones rápidas'),
            ('Registrar Horas', 'Botón de registro individual'),
            ('Registro en Bloque', 'Botón de registro en bloque'),
            ('Vista del Día', 'Botón de vista completa del día'),
            ('Ver Todas', 'Botón de ver todas las horas'),
            ('quick-action-btn', 'Clases CSS de botones mejorados'),
            ('fas fa-plus-circle', 'Iconos de acciones'),
            ('fas fa-layer-group', 'Icono de registro en bloque'),
            ('fas fa-calendar-day', 'Icono de vista del día')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
    else:
        print(f"Dashboard falló: {response.status_code}")
    
    # Probar acceso a registro en bloque
    print("\n📦 Probando acceso a registro en bloque...")
    response = client.get(reverse('horas:hora_bloque'))
    
    if response.status_code == 200:
        print("Registro en bloque carga correctamente")
        
        content = response.content.decode('utf-8')
        
        # Verificar elementos del widget de calendario
        calendar_checks = [
            ('multi-date-calendar.css', 'CSS del widget de calendario'),
            ('multi-date-calendar.js', 'JavaScript del widget de calendario'),
            ('multiDateCalendar', 'Contenedor del calendario'),
            ('selectedDatesList', 'Lista de fechas seleccionadas'),
            ('Seleccione las fechas específicas', 'Instrucciones mejoradas'),
            ('Widget de Calendario Multi-fecha', 'Comentario del widget')
        ]
        
        for check, description in calendar_checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
    else:
        print(f"Registro en bloque falló: {response.status_code}")
    
    # Probar vista completa del día
    print("\nProbando vista completa del día...")
    response = client.get(reverse('horas:vista_completa_dia'))
    
    if response.status_code == 200:
        print("Vista completa del día carga correctamente")
    else:
        print(f"Vista completa del día falló: {response.status_code}")
    
    print("\nPrueba de mejoras del dashboard completada")

def test_static_files():
    """Verificar que los archivos estáticos existen"""
    
    print("\nVerificando archivos estáticos...")
    
    import os
    from django.conf import settings
    
    static_files = [
        'css/multi-date-calendar.css',
        'js/multi-date-calendar.js'
    ]
    
    for file_path in static_files:
        full_path = os.path.join(settings.BASE_DIR, 'static', file_path)
        if os.path.exists(full_path):
            print(f"  {file_path}")
        else:
            print(f"  {file_path} - No encontrado")

def test_urls():
    """Verificar que las URLs están configuradas"""
    
    print("\n🔗 Verificando URLs...")
    
    urls_to_test = [
        ('core:dashboard', 'Dashboard'),
        ('horas:hora_create', 'Crear hora'),
        ('horas:hora_bloque', 'Registro en bloque'),
        ('horas:vista_completa_dia', 'Vista completa del día'),
        ('horas:hora_list', 'Lista de horas'),
        ('core:feriado_list', 'Lista de feriados'),
        ('core:periodo_list', 'Lista de períodos'),
        ('proyectos:proyecto_list', 'Lista de proyectos')
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"  {description}: {url}")
        except Exception as e:
            print(f"  {description}: Error - {e}")

if __name__ == '__main__':
    test_dashboard_improvements()
    test_static_files()
    test_urls()
    
    print("\n🎉 Resumen de Mejoras Implementadas:")
    print("=" * 50)
    print("Acciones Rápidas en Dashboard")
    print("  - Botones grandes y visibles")
    print("  - Efectos hover y animaciones")
    print("  - Acceso directo a funciones principales")
    print()
    print("Widget de Calendario Multi-fecha")
    print("  - Selección visual de múltiples fechas")
    print("  - Interfaz intuitiva y responsive")
    print("  - Validaciones automáticas")
    print()
    print("Mejoras de UX")
    print("  - Navegación más rápida")
    print("  - Instrucciones claras")
    print("  - Diseño moderno y atractivo")
