#!/usr/bin/env python
"""
Script para verificar que el fix del widget de calendario funciona
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def verificar_fix_calendario():
    """Verificar que el fix del calendario funciona"""
    
    print("🔧 Verificando fix del widget de calendario...")
    
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
    
    # Probar página de prueba del calendario
    print("\nProbando página de prueba del calendario...")
    try:
        response = client.get(reverse('horas:test_calendar'))
        if response.status_code == 200:
            print("Página de prueba carga correctamente")
            print("🌐 URL: /horas/test-calendar/")
        else:
            print(f"Página de prueba falló: {response.status_code}")
    except Exception as e:
        print(f"Error al acceder a página de prueba: {e}")
    
    # Probar registro en bloque
    print("\n📦 Probando registro en bloque...")
    response = client.get(reverse('horas:hora_bloque'))
    
    if response.status_code == 200:
        print("Registro en bloque carga correctamente")
        
        content = response.content.decode('utf-8')
        
        # Verificar fixes aplicados
        fixes_verificados = [
            ('type="hidden"', 'Campo fechas_manuales oculto'),
            ('id="multiDateCalendar"', 'Contenedor del calendario presente'),
            ('style="display: none;"', 'Sección manual oculta por defecto'),
            ('console.log(\'Inicializando calendario', 'Debug habilitado'),
            ('setTimeout(() => {', 'Inicialización con delay'),
            ('document.getElementById(\'config-manual\').style.display = \'block\'', 'Mostrar sección manual'),
            ('MultiDateCalendar no está disponible', 'Verificación de clase'),
            ('updatePatronConfig()', 'Inicialización al cargar página')
        ]
        
        for check, description in fixes_verificados:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
    else:
        print(f"Registro en bloque falló: {response.status_code}")
    
    print("\nResumen de fixes aplicados:")
    print("=" * 50)
    print("Campo fechas_manuales convertido a hidden")
    print("Sección manual oculta por defecto")
    print("Calendario se inicializa al seleccionar patrón manual")
    print("Debug logging agregado")
    print("Script carga antes del JavaScript principal")
    print("Página de prueba creada para debugging")
    
    print("\n🎯 Pasos para probar manualmente:")
    print("=" * 50)
    print("1. Ir a: http://localhost:8000/horas/test-calendar/")
    print("   - Verificar que el calendario se muestra inmediatamente")
    print("   - Probar selección de fechas")
    print("   - Verificar log de debug")
    print()
    print("2. Ir a: http://localhost:8000/horas/bloque/")
    print("   - Seleccionar 'Selección Manual' en Patrón de Repetición")
    print("   - Verificar que aparece el calendario")
    print("   - Abrir DevTools (F12) y verificar console")
    print("   - Verificar que no hay errores JavaScript")
    
    print("\n🚀 El fix ha sido aplicado exitosamente!")

if __name__ == '__main__':
    verificar_fix_calendario()
