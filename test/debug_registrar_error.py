#!/usr/bin/env python
"""
Script para diagnosticar el error interno en /horas/registrar/
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
import traceback

def debug_registrar_error():
    """Diagnosticar el error en /horas/registrar/"""
    
    print("🔍 Diagnosticando error en /horas/registrar/...")
    
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
    
    # Probar diferentes variantes de la URL
    urls_to_test = [
        '/horas/registrar/',
        '/horas/registrar/?fecha=2025-08-18',
        reverse('horas:hora_create'),
        reverse('horas:hora_create') + '?fecha=2025-08-18'
    ]
    
    for url in urls_to_test:
        print(f"\n📝 Probando: {url}")
        
        try:
            response = client.get(url)
            print(f"  📊 Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                print("  Página carga correctamente")
                
                # Verificar contenido básico
                content = response.content.decode('utf-8')
                if 'horas' in content.lower():
                    print("  Contenido relacionado con horas encontrado")
                else:
                    print("  ⚠️ Contenido no parece relacionado con horas")
                    
            elif response.status_code == 500:
                print("  Error interno del servidor (500)")
                
                # Intentar obtener más información del error
                if hasattr(response, 'context') and response.context:
                    print(f"  🔍 Contexto: {response.context}")
                    
            else:
                print(f"  ⚠️ Código inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"  Error al acceder: {e}")
            print("  Traceback:")
            traceback.print_exc()

def test_view_directly():
    """Probar la vista directamente"""
    
    print(f"\n🔧 Probando vista directamente...")
    
    try:
        from apps.horas.views import HoraCreateView
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        # Crear request simulado
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.get(username='admin')
        
        # Crear vista
        view = HoraCreateView()
        view.request = request
        
        print("Vista creada exitosamente")
        
        # Probar get_form_kwargs
        try:
            kwargs = view.get_form_kwargs()
            print(f"get_form_kwargs: {list(kwargs.keys())}")
        except Exception as e:
            print(f"Error en get_form_kwargs: {e}")
            traceback.print_exc()
        
        # Probar get_context_data
        try:
            context = view.get_context_data()
            print(f"get_context_data: {list(context.keys())}")
        except Exception as e:
            print(f"Error en get_context_data: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error al probar vista: {e}")
        traceback.print_exc()

def test_form_creation():
    """Probar creación del formulario"""
    
    print(f"\nProbando creación del formulario...")
    
    try:
        from apps.horas.forms import RegistroHoraForm
        from django.contrib.auth.models import User
        
        admin_user = User.objects.get(username='admin')
        
        # Probar crear formulario sin datos
        try:
            form = RegistroHoraForm(user=admin_user)
            print("Formulario creado sin datos")
        except Exception as e:
            print(f"Error al crear formulario sin datos: {e}")
            traceback.print_exc()
        
        # Probar crear formulario con datos
        try:
            form_data = {
                'fecha': '2025-08-18',
                'horas': '1.5',
                'descripcion': 'Prueba',
                'tipo_tarea': 'tarea'
            }
            form = RegistroHoraForm(data=form_data, user=admin_user)
            print("Formulario creado con datos")
            
            if form.is_valid():
                print("Formulario válido")
            else:
                print(f"Formulario inválido: {form.errors}")
                
        except Exception as e:
            print(f"Error al crear formulario con datos: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error general en formulario: {e}")
        traceback.print_exc()

def test_template_rendering():
    """Probar renderizado del template"""
    
    print(f"\n🎨 Probando renderizado del template...")
    
    try:
        from django.template.loader import get_template
        from django.template import Context
        
        # Verificar que el template existe
        try:
            template = get_template('horas/hora_form.html')
            print("Template encontrado")
        except Exception as e:
            print(f"Error al cargar template: {e}")
            return
        
        # Probar renderizado básico
        try:
            from apps.horas.forms import RegistroHoraForm
            admin_user = User.objects.get(username='admin')
            
            form = RegistroHoraForm(user=admin_user)
            context = {
                'form': form,
                'user': admin_user
            }
            
            rendered = template.render(context)
            print("Template renderizado exitosamente")
            
            if len(rendered) > 1000:
                print(f"Template tiene contenido sustancial ({len(rendered)} caracteres)")
            else:
                print(f"⚠️ Template parece muy corto ({len(rendered)} caracteres)")
                
        except Exception as e:
            print(f"Error al renderizar template: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error general en template: {e}")
        traceback.print_exc()

def check_dependencies():
    """Verificar dependencias y configuración"""
    
    print(f"\n🔧 Verificando dependencias...")
    
    # Verificar importaciones críticas
    critical_imports = [
        ('apps.horas.models', 'RegistroHora'),
        ('apps.horas.forms', 'RegistroHoraForm'),
        ('apps.horas.views', 'HoraCreateView'),
        ('apps.proyectos.models', 'Proyecto'),
        ('apps.horas.fields', 'HoursField'),
    ]
    
    for module_name, class_name in critical_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"{module_name}.{class_name}")
        except Exception as e:
            print(f"{module_name}.{class_name}: {e}")
    
    # Verificar configuración de URLs
    try:
        from django.urls import reverse
        url = reverse('horas:hora_create')
        print(f"URL reverse: {url}")
    except Exception as e:
        print(f"URL reverse: {e}")

if __name__ == '__main__':
    debug_registrar_error()
    test_view_directly()
    test_form_creation()
    test_template_rendering()
    check_dependencies()
    
    print(f"\n🎯 Diagnóstico completado")
    print("=" * 40)
    print("Revisar los errores mostrados arriba para identificar la causa del problema.")
