#!/usr/bin/env python
"""
Script para reproducir el error en POST de /horas/registrar/
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
from datetime import date, timedelta

def test_post_error():
    """Probar el error en POST"""
    
    print("🔍 Probando error en POST /horas/registrar/...")
    
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
    
    # Casos de prueba POST
    test_cases = [
        {
            'data': {
                'fecha': test_date.isoformat(),
                'proyecto': proyecto.id,
                'horas': '1.5',
                'descripcion': 'Prueba POST decimal',
                'tipo_tarea': 'tarea'
            },
            'description': 'POST con formato decimal'
        },
        {
            'data': {
                'fecha': test_date.isoformat(),
                'proyecto': proyecto.id,
                'horas': '01:30',
                'descripcion': 'Prueba POST tiempo',
                'tipo_tarea': 'reunion'
            },
            'description': 'POST con formato tiempo'
        },
        {
            'data': {
                'fecha': test_date.isoformat(),
                'proyecto': proyecto.id,
                'horas': 'invalid',
                'descripcion': 'Prueba POST inválido',
                'tipo_tarea': 'tarea'
            },
            'description': 'POST con datos inválidos'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Prueba {i}: {test_case['description']}")
        print(f"  Datos: {test_case['data']}")
        
        try:
            response = client.post(reverse('horas:hora_create'), data=test_case['data'])
            
            print(f"  📊 Código de respuesta: {response.status_code}")
            
            if response.status_code == 302:
                print("  Redirección exitosa (guardado correcto)")
                
                # Verificar que se guardó
                from apps.horas.models import RegistroHora
                registro = RegistroHora.objects.filter(
                    usuario=admin_user,
                    fecha=test_date,
                    descripcion=test_case['data']['descripcion']
                ).first()
                
                if registro:
                    print(f"  Registro guardado: {registro.horas} horas")
                    # Limpiar
                    registro.delete()
                else:
                    print("  Registro no encontrado en BD")
                    
            elif response.status_code == 200:
                print("  ⚠️ Formulario devuelto (posibles errores de validación)")
                
                # Buscar errores en el contenido
                content = response.content.decode('utf-8')
                if 'errorlist' in content:
                    print("  Errores de validación encontrados")
                else:
                    print("  ℹ️ Formulario mostrado sin errores aparentes")
                    
            elif response.status_code == 500:
                print("  Error interno del servidor")
                
                # Intentar obtener más información
                if hasattr(response, 'context'):
                    print(f"  🔍 Contexto disponible: {bool(response.context)}")
                    
            else:
                print(f"  ⚠️ Código inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"  Error durante POST: {e}")
            import traceback
            traceback.print_exc()

def test_get_with_parameters():
    """Probar GET con diferentes parámetros"""
    
    print(f"\n🔍 Probando GET con parámetros...")
    
    client = Client()
    
    # Login
    admin_user = User.objects.get(username='admin')
    client.login(username='admin', password='admin123')
    
    # Diferentes parámetros GET
    get_tests = [
        ('', 'Sin parámetros'),
        ('?fecha=2025-08-18', 'Con fecha válida'),
        ('?fecha=invalid', 'Con fecha inválida'),
        ('?proyecto=1', 'Con proyecto'),
        ('?fecha=2025-08-18&proyecto=1', 'Con fecha y proyecto'),
    ]
    
    for params, description in get_tests:
        print(f"\n📝 {description}: {params}")
        
        try:
            url = reverse('horas:hora_create') + params
            response = client.get(url)
            
            print(f"  📊 Código: {response.status_code}")
            
            if response.status_code == 200:
                print("  Página carga correctamente")
            else:
                print(f"  Error: {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == '__main__':
    test_post_error()
    test_get_with_parameters()
    
    print(f"\n🎯 Si no se reproduce el error aquí, puede ser:")
    print("1. Error intermitente o de concurrencia")
    print("2. Error específico del navegador/JavaScript")
    print("3. Error en condiciones específicas no cubiertas")
    print("4. Error en el servidor de desarrollo vs producción")
