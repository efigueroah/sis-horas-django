#!/usr/bin/env python
"""
Script para probar específicamente el widget de calendario
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_calendar_widget():
    """Probar widget de calendario en registro en bloque"""
    
    print("🔍 Probando widget de calendario...")
    
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
    
    # Probar página de registro en bloque
    print("\n📦 Probando página de registro en bloque...")
    response = client.get(reverse('horas:hora_bloque'))
    
    if response.status_code == 200:
        print("Página carga correctamente")
        
        content = response.content.decode('utf-8')
        
        # Verificar elementos críticos del widget
        critical_checks = [
            ('multiDateCalendar', 'Contenedor del calendario'),
            ('selectedDatesList', 'Lista de fechas seleccionadas'),
            ('config-manual', 'Sección de configuración manual'),
            ('MultiDateCalendar', 'Clase JavaScript del calendario'),
            ('initMultiDateCalendar', 'Función de inicialización'),
            ('updatePatronConfig', 'Función de actualización de patrón'),
            ('multi-date-calendar.js', 'Script del widget'),
            ('multi-date-calendar.css', 'Estilos del widget')
        ]
        
        for check, description in critical_checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
        
        # Verificar estructura HTML específica
        html_checks = [
            ('id="multiDateCalendar"', 'ID del contenedor del calendario'),
            ('id="selectedDatesList"', 'ID de la lista de fechas'),
            ('name="fechas_manuales"', 'Campo oculto para fechas'),
            ('type="hidden"', 'Campo oculto configurado'),
            ('patron_repeticion', 'Radio buttons de patrón'),
            ('value="manual"', 'Opción manual disponible')
        ]
        
        for check, description in html_checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
        
        # Verificar JavaScript específico
        js_checks = [
            ('console.log(\'Inicializando calendario', 'Debug de inicialización'),
            ('new MultiDateCalendar(', 'Instanciación del calendario'),
            ('onChange: function(selectedDates)', 'Callback de cambios'),
            ('updateSelectedDatesList', 'Función de actualización de lista'),
            ('clearAllSelectedDates', 'Función de limpiar fechas'),
            ('selectedPatron === \'manual\'', 'Detección de patrón manual')
        ]
        
        for check, description in js_checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
                
    else:
        print(f"Página falló: {response.status_code}")
        return
    
    print("\nVerificando archivos estáticos...")
    
    # Verificar archivos CSS y JS
    import os
    from django.conf import settings
    
    static_files = [
        ('css/multi-date-calendar.css', 'Estilos del calendario'),
        ('js/multi-date-calendar.js', 'JavaScript del calendario')
    ]
    
    for file_path, description in static_files:
        full_path = os.path.join(settings.BASE_DIR, 'static', file_path)
        if os.path.exists(full_path):
            print(f"  {description}")
            
            # Verificar contenido del archivo
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'MultiDateCalendar' in content:
                print(f"    Contiene clase MultiDateCalendar")
            else:
                print(f"    No contiene clase MultiDateCalendar")
                
        else:
            print(f"  {description} - Archivo no encontrado")
    
    print("\nPrueba del widget de calendario completada")

def debug_calendar_issues():
    """Diagnosticar posibles problemas con el calendario"""
    
    print("\n🔧 Diagnosticando posibles problemas...")
    
    # Verificar estructura de archivos
    import os
    from django.conf import settings
    
    base_dir = settings.BASE_DIR
    
    # Verificar directorios
    directories = [
        'static',
        'static/css',
        'static/js',
        'templates',
        'templates/horas'
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if os.path.exists(dir_path):
            print(f"  Directorio {directory} existe")
        else:
            print(f"  Directorio {directory} no existe")
    
    # Verificar permisos de archivos
    files_to_check = [
        'static/css/multi-date-calendar.css',
        'static/js/multi-date-calendar.js',
        'templates/horas/hora_bloque_form.html'
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if os.access(full_path, os.R_OK):
                print(f"  {file_path} - Legible")
            else:
                print(f"  {file_path} - Sin permisos de lectura")
        else:
            print(f"  {file_path} - No existe")

if __name__ == '__main__':
    test_calendar_widget()
    debug_calendar_issues()
    
    print("\n🎯 Instrucciones para verificar manualmente:")
    print("=" * 50)
    print("1. Abrir navegador en modo desarrollador (F12)")
    print("2. Ir a Registro en Bloque")
    print("3. Seleccionar 'Selección Manual' en Patrón de Repetición")
    print("4. Verificar en Console si aparecen mensajes de debug")
    print("5. Verificar si el div 'multiDateCalendar' se hace visible")
    print("6. Verificar si se carga el script multi-date-calendar.js")
    print("7. Verificar si la clase MultiDateCalendar está definida")
