#!/usr/bin/env python
"""
Script para probar la funcionalidad de feriados
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import DiaFeriado
from apps.core.forms import DiaFeriadoForm
from datetime import date, timedelta

def test_feriados():
    """Probar funcionalidad de feriados"""
    
    print("🔍 Probando funcionalidad de feriados...")
    
    # Obtener usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario: {admin_user.username}")
    except User.DoesNotExist:
        print("Usuario admin no encontrado")
        return
    
    # Probar creación de feriado
    print("\nProbando creación de feriado...")
    
    feriado_data = {
        'nombre': 'Día de Prueba',
        'fecha': date.today() + timedelta(days=30),
        'descripcion': 'Feriado de prueba para verificar funcionalidad'
    }
    
    # Probar formulario
    form = DiaFeriadoForm(data=feriado_data)
    if form.is_valid():
        print("Formulario válido")
        
        # Crear feriado
        feriado = form.save(commit=False)
        feriado.usuario = admin_user
        feriado.save()
        
        print(f"Feriado creado: {feriado.nombre}")
        print(f"Fecha: {feriado.fecha}")
        print(f"📝 Descripción: {feriado.descripcion}")
        
        # Verificar que se guardó correctamente
        feriado_guardado = DiaFeriado.objects.get(pk=feriado.pk)
        print(f"Feriado verificado en BD: {feriado_guardado.nombre}")
        
        # Limpiar - eliminar feriado de prueba
        feriado.delete()
        print("🗑️ Feriado de prueba eliminado")
        
    else:
        print("Formulario inválido:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
    
    # Verificar feriados existentes
    print("\nFeriados existentes:")
    feriados = DiaFeriado.objects.filter(usuario=admin_user)
    
    if feriados.exists():
        for feriado in feriados:
            print(f"  {feriado.fecha} - {feriado.nombre}")
            if feriado.descripcion:
                print(f"     📝 {feriado.descripcion}")
    else:
        print("  ℹ️ No hay feriados registrados")
    
    print("\nPrueba de feriados completada")

if __name__ == '__main__':
    test_feriados()
