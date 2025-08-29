#!/usr/bin/env python
"""
Script para debuggear problemas con períodos
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Periodo

def debug_periodos():
    """Debuggear períodos"""
    
    print("🔍 Debuggeando períodos...")
    
    # Obtener todos los usuarios
    users = User.objects.all()
    print(f"📊 Total usuarios: {users.count()}")
    
    for user in users:
        print(f"\n👤 Usuario: {user.username}")
        
        # Obtener períodos del usuario
        periodos = Periodo.objects.filter(usuario=user)
        print(f"Total períodos: {periodos.count()}")
        
        for periodo in periodos:
            print(f"  {periodo.nombre}")
            print(f"     🗓️  Fechas: {periodo.fecha_inicio} - {periodo.fecha_fin}")
            print(f"     ⚡ Activo: {periodo.activo}")
            print(f"     🎯 Horas objetivo: {periodo.horas_objetivo}")
            print(f"     Horas máx/día: {periodo.horas_max_dia}")
            print(f"     Año: {periodo.año}")
            print(f"     🕐 Creado: {periodo.created_at}")
            print(f"     🔄 Actualizado: {periodo.updated_at}")
            print()
        
        # Verificar período activo
        periodo_activo = Periodo.objects.filter(usuario=user, activo=True).first()
        if periodo_activo:
            print(f"Período activo: {periodo_activo.nombre}")
        else:
            print("No hay período activo")
    
    print("\n🔧 Verificando integridad de datos...")
    
    # Verificar usuarios con múltiples períodos activos
    for user in users:
        activos = Periodo.objects.filter(usuario=user, activo=True).count()
        if activos > 1:
            print(f"⚠️  Usuario {user.username} tiene {activos} períodos activos (debería ser 1)")
        elif activos == 0:
            print(f"ℹ️  Usuario {user.username} no tiene períodos activos")

def fix_periodos():
    """Corregir problemas comunes con períodos"""
    
    print("\n🔧 Corrigiendo problemas con períodos...")
    
    users = User.objects.all()
    
    for user in users:
        # Verificar múltiples períodos activos
        activos = Periodo.objects.filter(usuario=user, activo=True)
        
        if activos.count() > 1:
            print(f"🔧 Corrigiendo múltiples períodos activos para {user.username}")
            
            # Mantener solo el más reciente activo
            periodo_mas_reciente = activos.order_by('-created_at').first()
            
            # Desactivar todos
            activos.update(activo=False)
            
            # Activar solo el más reciente
            periodo_mas_reciente.activo = True
            periodo_mas_reciente.save()
            
            print(f"Período '{periodo_mas_reciente.nombre}' mantenido como activo")
        
        # Verificar campos año
        for periodo in Periodo.objects.filter(usuario=user):
            if not periodo.año:
                periodo.año = periodo.fecha_inicio.year
                periodo.save()
                print(f"🔧 Corregido año para período '{periodo.nombre}': {periodo.año}")

if __name__ == '__main__':
    debug_periodos()
    
    # Preguntar si quiere corregir problemas
    respuesta = input("\n¿Desea corregir los problemas encontrados? (s/n): ")
    if respuesta.lower() in ['s', 'si', 'y', 'yes']:
        fix_periodos()
        print("\nCorrecciones aplicadas")
        
        # Verificar nuevamente
        print("\n🔍 Verificando después de las correcciones...")
        debug_periodos()
    else:
        print("\nNo se aplicaron correcciones")
