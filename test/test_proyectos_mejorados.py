#!/usr/bin/env python
"""
Script para probar la funcionalidad mejorada de proyectos
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

def test_improved_projects():
    """Probar funcionalidad mejorada de proyectos"""
    
    print("🔍 Probando funcionalidad mejorada de proyectos...")
    
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
    
    # Crear proyectos de prueba si no existen
    print("\n📦 Verificando proyectos de prueba...")
    
    proyectos_prueba = [
        {
            'nombre': 'Proyecto Activo 1',
            'cliente': 'Cliente ABC',
            'descripcion': 'Proyecto de desarrollo web activo',
            'activo': True
        },
        {
            'nombre': 'Proyecto Activo 2', 
            'cliente': 'Cliente XYZ',
            'descripcion': 'Proyecto de aplicación móvil activo',
            'activo': True
        },
        {
            'nombre': 'Proyecto Inactivo 1',
            'cliente': 'Cliente ABC',
            'descripcion': 'Proyecto finalizado o pausado',
            'activo': False
        },
        {
            'nombre': 'Proyecto Inactivo 2',
            'cliente': 'Cliente DEF',
            'descripcion': 'Proyecto en pausa temporal',
            'activo': False
        }
    ]
    
    for proyecto_data in proyectos_prueba:
        proyecto, created = Proyecto.objects.get_or_create(
            nombre=proyecto_data['nombre'],
            usuario=admin_user,
            defaults=proyecto_data
        )
        if created:
            print(f"  Creado: {proyecto.nombre}")
        else:
            print(f"  Existente: {proyecto.nombre}")
    
    # Probar lista de proyectos
    print("\nProbando lista de proyectos...")
    response = client.get(reverse('proyectos:proyecto_list'))
    
    if response.status_code == 200:
        print("Lista de proyectos carga correctamente")
        
        content = response.content.decode('utf-8')
        
        # Verificar elementos de la interfaz mejorada
        ui_checks = [
            ('Proyectos Activos', 'Sección de proyectos activos'),
            ('Proyectos Inactivos', 'Sección de proyectos inactivos'),
            ('Filtros de Búsqueda', 'Sección de filtros'),
            ('project-stats', 'Estadísticas de proyectos'),
            ('filter-section', 'Sección de filtros'),
            ('toggleProyecto', 'Función JavaScript de toggle'),
            ('showAlert', 'Función de alertas'),
            ('name="nombre"', 'Campo de filtro por nombre'),
            ('name="cliente"', 'Campo de filtro por cliente'),
            ('name="estado"', 'Campo de filtro por estado')
        ]
        
        for check, description in ui_checks:
            if check in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
        
        # Verificar que se muestran proyectos activos e inactivos
        context = response.context
        proyectos_activos = context.get('proyectos_activos', [])
        proyectos_inactivos = context.get('proyectos_inactivos', [])
        
        print(f"  📊 Proyectos activos: {len(proyectos_activos)}")
        print(f"  📊 Proyectos inactivos: {len(proyectos_inactivos)}")
        
    else:
        print(f"Lista de proyectos falló: {response.status_code}")
        return
    
    # Probar filtros
    print("\n🔍 Probando filtros...")
    
    # Filtro por nombre
    response = client.get(reverse('proyectos:proyecto_list') + '?nombre=Activo')
    if response.status_code == 200:
        proyectos_filtrados = response.context['proyectos']
        print(f"  Filtro por nombre: {len(proyectos_filtrados)} proyectos encontrados")
    else:
        print("  Filtro por nombre falló")
    
    # Filtro por cliente
    response = client.get(reverse('proyectos:proyecto_list') + '?cliente=ABC')
    if response.status_code == 200:
        proyectos_filtrados = response.context['proyectos']
        print(f"  Filtro por cliente: {len(proyectos_filtrados)} proyectos encontrados")
    else:
        print("  Filtro por cliente falló")
    
    # Filtro por estado
    response = client.get(reverse('proyectos:proyecto_list') + '?estado=activo')
    if response.status_code == 200:
        proyectos_filtrados = response.context['proyectos']
        print(f"  Filtro por estado activo: {len(proyectos_filtrados)} proyectos encontrados")
    else:
        print("  Filtro por estado falló")
    
    # Probar toggle de proyecto
    print("\n🔄 Probando toggle de proyecto...")
    
    # Obtener un proyecto para probar
    proyecto_test = Proyecto.objects.filter(usuario=admin_user).first()
    if proyecto_test:
        estado_original = proyecto_test.activo
        
        # Hacer toggle
        response = client.post(
            reverse('proyectos:proyecto_toggle', kwargs={'pk': proyecto_test.pk}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  Toggle exitoso: {proyecto_test.nombre}")
                
                # Verificar que cambió el estado
                proyecto_test.refresh_from_db()
                if proyecto_test.activo != estado_original:
                    print(f"  Estado cambiado: {estado_original} → {proyecto_test.activo}")
                    
                    # Restaurar estado original
                    proyecto_test.activo = estado_original
                    proyecto_test.save()
                    print(f"  Estado restaurado")
                else:
                    print(f"  Estado no cambió")
            else:
                print(f"  Toggle falló: {data.get('error', 'Error desconocido')}")
        else:
            print(f"  Toggle falló con código: {response.status_code}")
    else:
        print("  No hay proyectos para probar toggle")
    
    print("\nPrueba de funcionalidad mejorada de proyectos completada")

def verify_template_features():
    """Verificar características del template mejorado"""
    
    print("\n🎨 Verificando características del template...")
    
    template_path = '/home/efigueroa/Proyectos/AWS-QDeveloper/proyectos/reporte_horas_trabajadas/sis-horas-django/templates/proyectos/proyecto_list.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        features = [
            ('project-stats', 'Estadísticas de proyectos'),
            ('filter-section', 'Sección de filtros'),
            ('section-header active', 'Header de proyectos activos'),
            ('section-header inactive', 'Header de proyectos inactivos'),
            ('project-card active', 'Cards de proyectos activos'),
            ('project-card inactive', 'Cards de proyectos inactivos'),
            ('toggleProyecto', 'Función de toggle'),
            ('showAlert', 'Sistema de alertas'),
            ('csrf_token', 'Token CSRF'),
            ('applyFilters', 'Filtrado automático')
        ]
        
        for feature, description in features:
            if feature in content:
                print(f"  {description}")
            else:
                print(f"  {description} - No encontrado")
                
    except FileNotFoundError:
        print("  Template no encontrado")

if __name__ == '__main__':
    test_improved_projects()
    verify_template_features()
    
    print("\n🎉 Resumen de Mejoras Implementadas:")
    print("=" * 50)
    print("Separación visual de proyectos activos e inactivos")
    print("Filtros por nombre, cliente y estado")
    print("Estadísticas en tiempo real")
    print("Botón de toggle mejorado con confirmación")
    print("Sistema de alertas para feedback")
    print("Interfaz responsive y moderna")
    print("Filtrado automático mientras se escribe")
    print("Token CSRF incluido para seguridad")
    print()
    print("🎯 Para probar manualmente:")
    print("1. Ir a: http://localhost:8000/proyectos/")
    print("2. Verificar separación de proyectos activos/inactivos")
    print("3. Probar filtros de búsqueda")
    print("4. Probar botones de activar/desactivar")
    print("5. Verificar alertas de confirmación")
