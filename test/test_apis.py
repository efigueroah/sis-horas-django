#!/usr/bin/env python
"""
Script para probar las APIs del sistema
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from apps.proyectos.models import Proyecto
from apps.core.models import Periodo
from apps.horas.models import RegistroHora

def test_api_endpoints():
    """Probar todos los endpoints de la API"""
    
    print("🔍 Probando endpoints de la API...")
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Usuario de prueba creado: {user.username}")
    
    # Hacer login
    login_success = client.login(username='test_user', password='testpass123')
    print(f"🔐 Login: {'Exitoso' if login_success else 'Fallido'}")
    
    if not login_success:
        print("No se puede continuar sin login")
        return
    
    # Probar endpoints
    endpoints = [
        ('/api/periodos/', 'GET', 'Períodos'),
        ('/api/periodos/activo/', 'GET', 'Período Activo'),
        ('/api/proyectos/', 'GET', 'Proyectos'),
        ('/api/proyectos/activos/', 'GET', 'Proyectos Activos'),
        ('/api/horas/', 'GET', 'Horas'),
        ('/api/feriados/', 'GET', 'Feriados'),
        ('/api/calendario/2025/8/', 'GET', 'Calendario'),
    ]
    
    for url, method, name in endpoints:
        try:
            if method == 'GET':
                response = client.get(url)
            else:
                response = client.post(url)
            
            status = response.status_code
            if status == 200:
                print(f"{name}: {url} - Status {status}")
                
                # Mostrar datos si es JSON
                if 'application/json' in response.get('Content-Type', ''):
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   📊 Datos: {len(data)} elementos")
                        elif isinstance(data, dict):
                            print(f"   📊 Datos: {list(data.keys())}")
                    except:
                        pass
            else:
                print(f"⚠️  {name}: {url} - Status {status}")
                
        except Exception as e:
            print(f"{name}: {url} - Error: {e}")
    
    print("\n🔧 Verificando datos de prueba...")
    
    # Crear datos de prueba si no existen
    if not Proyecto.objects.filter(usuario=user).exists():
        proyecto = Proyecto.objects.create(
            usuario=user,
            nombre="Proyecto de Prueba",
            descripcion="Proyecto para probar la API",
            color_hex="#007bff"
        )
        print(f"Proyecto de prueba creado: {proyecto.nombre}")
    
    if not Periodo.objects.filter(usuario=user).exists():
        from datetime import date, timedelta
        periodo = Periodo.objects.create(
            usuario=user,
            nombre="Período de Prueba",
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            horas_objetivo=160,
            activo=True
        )
        print(f"Período de prueba creado: {periodo.nombre}")
    
    print("\n🎯 Probando creación de registro de horas via API...")
    
    # Probar POST a la API de horas
    proyecto = Proyecto.objects.filter(usuario=user).first()
    if proyecto:
        post_data = {
            'fecha': '2025-08-23',
            'proyecto': proyecto.id,
            'horas': 8.0,
            'descripcion': 'Registro de prueba via API',
            'tipo_tarea': 'desarrollo'
        }
        
        response = client.post('/api/horas/', 
                             data=post_data, 
                             content_type='application/json')
        
        if response.status_code == 200:
            print("POST /api/horas/ - Exitoso")
            try:
                data = response.json()
                print(f"   📊 Respuesta: {data}")
            except:
                pass
        else:
            print(f"POST /api/horas/ - Status {response.status_code}")
            print(f"   📄 Respuesta: {response.content.decode()}")
    
    print("\nPrueba de APIs completada")

if __name__ == '__main__':
    test_api_endpoints()
