#!/usr/bin/env python
"""
Script para debuggear por qué falló el formato 2:00
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
from apps.horas.forms import RegistroHoraForm
from datetime import date, timedelta

def debug_2_00_format():
    """Debuggear el formato 2:00"""
    
    print("🔍 Debuggeando formato 2:00...")
    
    admin_user = User.objects.get(username='admin')
    proyecto = Proyecto.objects.filter(usuario=admin_user, activo=True).first()
    
    today = date.today()
    days_back = today.weekday() + 7
    test_date = today - timedelta(days=days_back)
    
    # Probar el formulario directamente
    form_data = {
        'fecha': test_date,
        'proyecto': proyecto.id,
        'horas': '2:00',
        'descripcion': 'Prueba 2:00',
        'tipo_tarea': 'desarrollo'
    }
    
    print(f"Datos del formulario: {form_data}")
    
    form = RegistroHoraForm(data=form_data, user=admin_user)
    
    print(f"📊 Formulario válido: {form.is_valid()}")
    
    if not form.is_valid():
        print("Errores del formulario:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
        
        # Verificar específicamente el campo horas
        if 'horas' in form.errors:
            print(f"\n🔍 Error específico en horas:")
            print(f"  Valor ingresado: '{form_data['horas']}'")
            
            # Probar la conversión directamente
            from apps.horas.fields import convert_hours_input
            try:
                converted = convert_hours_input('2:00')
                print(f"  Conversión directa: {converted}")
            except Exception as e:
                print(f"  Error en conversión: {e}")
    
    # Probar también con el cliente web
    print(f"\n🌐 Probando con cliente web...")
    
    client = Client()
    client.login(username='admin', password='admin123')
    
    web_data = {
        'fecha': test_date.isoformat(),
        'proyecto': proyecto.id,
        'horas': '2:00',
        'descripcion': 'Prueba web 2:00',
        'tipo_tarea': 'desarrollo'
    }
    
    response = client.post(reverse('horas:hora_create'), data=web_data)
    
    print(f"📊 Código de respuesta web: {response.status_code}")
    
    if response.status_code == 200:
        # Buscar errores en el HTML
        content = response.content.decode('utf-8')
        
        if 'errorlist' in content:
            print("Errores encontrados en HTML:")
            # Extraer errores básicos
            import re
            errors = re.findall(r'<li>(.*?)</li>', content)
            for error in errors[:5]:  # Mostrar solo los primeros 5
                if 'horas' in error.lower():
                    print(f"  - {error}")

if __name__ == '__main__':
    debug_2_00_format()
