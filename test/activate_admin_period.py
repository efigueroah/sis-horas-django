#!/usr/bin/env python
"""
Script para activar el período del usuario admin
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Periodo

def activate_admin_period():
    """Activar período del usuario admin"""
    
    try:
        # Obtener usuario admin
        admin_user = User.objects.get(username='admin')
        print(f"👤 Usuario encontrado: {admin_user.username}")
        
        # Obtener período del admin
        periodo = Periodo.objects.filter(usuario=admin_user).first()
        
        if periodo:
            # Desactivar otros períodos del usuario (por si acaso)
            Periodo.objects.filter(usuario=admin_user, activo=True).update(activo=False)
            
            # Activar este período
            periodo.activo = True
            periodo.save()
            
            print(f"Período '{periodo.nombre}' activado para {admin_user.username}")
            print(f"Fechas: {periodo.fecha_inicio} - {periodo.fecha_fin}")
            print(f"🎯 Horas objetivo: {periodo.horas_objetivo}")
            print(f"Horas máx/día: {periodo.horas_max_dia}")
        else:
            print(f"No se encontró ningún período para el usuario {admin_user.username}")
            
    except User.DoesNotExist:
        print("Usuario 'admin' no encontrado")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    activate_admin_period()
