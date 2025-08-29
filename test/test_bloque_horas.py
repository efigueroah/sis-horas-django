#!/usr/bin/env python
"""
Script para probar la funcionalidad de registro en bloque
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from apps.horas.models import RegistroHora
from apps.horas.forms import RegistroHoraBloqueForm
from apps.proyectos.models import Proyecto
from datetime import date, timedelta

def test_registro_bloque():
    """Probar funcionalidad de registro en bloque"""
    
    print("🔍 Probando funcionalidad de registro en bloque...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario: {admin_user.username}")
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Obtener o crear proyecto
    proyecto, created = Proyecto.objects.get_or_create(
        nombre='Proyecto de Prueba',
        usuario=admin_user,
        defaults={
            'descripcion': 'Proyecto para probar registro en bloque',
            'activo': True
        }
    )
    
    if created:
        print(f"Proyecto creado: {proyecto.nombre}")
    else:
        print(f"Proyecto existente: {proyecto.nombre}")
    
    # Probar formulario de registro en bloque
    print("\n📦 Probando formulario de registro en bloque...")
    
    # Datos para patrón semanal
    form_data = {
        'proyecto': proyecto.id,
        'horas': '1.5',
        'descripcion': 'Reunión semanal de seguimiento',
        'tipo_tarea': 'reunion',
        'patron_repeticion': 'semanal',
        'fecha_inicio': date.today(),
        'fecha_fin': date.today() + timedelta(days=21),  # 3 semanas
        'dia_semana': '4',  # Viernes
        'omitir_feriados': True,
        'omitir_fines_semana': True
    }
    
    # Probar formulario
    form = RegistroHoraBloqueForm(data=form_data, user=admin_user)
    if form.is_valid():
        print("Formulario válido")
        
        # Generar fechas
        fechas = form.generar_fechas()
        print(f"Fechas generadas: {len(fechas)}")
        
        for i, fecha in enumerate(fechas, 1):
            print(f"  {i}. {fecha.strftime('%Y-%m-%d (%A)')}")
        
        # Simular creación de registros (sin guardar realmente)
        registros_simulados = []
        for fecha in fechas:
            registro_data = {
                'usuario': admin_user,
                'fecha': fecha,
                'proyecto': proyecto,
                'horas': float(form.cleaned_data['horas']),
                'descripcion': form.cleaned_data['descripcion'],
                'tipo_tarea': form.cleaned_data['tipo_tarea']
            }
            registros_simulados.append(registro_data)
        
        print(f"Se crearían {len(registros_simulados)} registros de horas")
        print(f"Total de horas: {len(registros_simulados) * float(form.cleaned_data['horas'])}")
        
    else:
        print("Formulario inválido:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
    
    # Probar patrón manual
    print("\nProbando patrón manual...")
    
    fechas_manuales = [
        date.today() + timedelta(days=7),
        date.today() + timedelta(days=14),
        date.today() + timedelta(days=21)
    ]
    
    form_data_manual = {
        'proyecto': proyecto.id,
        'horas': '2.0',
        'descripcion': 'Capacitación mensual',
        'tipo_tarea': 'tarea',  # Usar opción válida
        'patron_repeticion': 'manual',
        'fechas_manuales': ','.join([f.strftime('%Y-%m-%d') for f in fechas_manuales]),
        'omitir_feriados': True,
        'omitir_fines_semana': False
    }
    
    form_manual = RegistroHoraBloqueForm(data=form_data_manual, user=admin_user)
    if form_manual.is_valid():
        print("Formulario manual válido")
        
        fechas_generadas = form_manual.generar_fechas()
        print(f"Fechas manuales generadas: {len(fechas_generadas)}")
        
        for i, fecha in enumerate(fechas_generadas, 1):
            print(f"  {i}. {fecha.strftime('%Y-%m-%d (%A)')}")
    else:
        print("Formulario manual inválido:")
        for field, errors in form_manual.errors.items():
            print(f"  - {field}: {errors}")
    
    print("\nPrueba de registro en bloque completada")

if __name__ == '__main__':
    test_registro_bloque()
