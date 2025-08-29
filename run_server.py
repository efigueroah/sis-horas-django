#!/usr/bin/env python
"""
Script de inicio para el Sistema de Gestión de Horas Django
"""

import os
import sys
import socket
import subprocess
import webbrowser
from pathlib import Path

def find_available_port(start_port=8000, max_port=8010):
    """Encuentra un puerto disponible"""
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def check_virtual_env():
    """Verifica si el entorno virtual está activado"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    print("=" * 60)
    print("🚀 SISTEMA DE GESTIÓN DE HORAS - DJANGO")
    print("=" * 60)
    
    # Verificar entorno virtual
    if not check_virtual_env():
        print("⚠️  ADVERTENCIA: No se detectó un entorno virtual activado")
        print("   Ejecuta: source venv/bin/activate")
        print()
    
    # Encontrar puerto disponible
    port = find_available_port()
    if not port:
        print("No se pudo encontrar un puerto disponible")
        return
    
    # URLs importantes
    server_url = f"http://127.0.0.1:{port}"
    admin_url = f"{server_url}/admin/"
    
    print(f"🌐 Servidor iniciando en: {server_url}")
    print(f"🔧 Panel Admin en: {admin_url}")
    print()
    
    # Información de usuarios
    print("👤 USUARIOS DE PRUEBA:")
    print("   • admin / admin123 (Superusuario)")
    print("   • demo1 / demo123 (Juan Pérez)")
    print("   • demo2 / demo123 (María González)")
    print()
    
    # Características del sistema
    print("✨ CARACTERÍSTICAS PRINCIPALES:")
    print("   • Dashboard interactivo con gráficos")
    print("   • CRUD completo de proyectos")
    print("   • Gestión avanzada de horas con slider")
    print("   • Tipos de tarea (Tarea/Reunión)")
    print("   • Calendario visual con estados")
    print("   • Filtros avanzados por fecha, proyecto y tipo")
    print("   • Validaciones inteligentes (fines de semana, feriados)")
    print("   • Sistema de períodos con activación exclusiva")
    print("   • Exportación a CSV/Excel")
    print("   • Panel de administración Django completo")
    print("   • Autenticación multiusuario con perfiles")
    print("   • Datos de demostración incluidos")
    print()
    
    print("🎯 FUNCIONALIDADES IMPLEMENTADAS:")
    print("   Autenticación avanzada (multiusuario + roles)")
    print("   CRUD proyectos con filtros por año")
    print("   Slider de horas (0.5h - 12h, incrementos 30min)")
    print("   Tipos de tarea con estadísticas")
    print("   Selector de período activo")
    print("   Validaciones en tiempo real")
    print("   Calendario interactivo")
    print("   Dashboard con gráficos")
    print("   Exportación configurable")
    print("   Admin interface completa")
    print("   Datos de prueba automáticos")
    print()
    
    print("🔧 COMANDOS ÚTILES:")
    print(f"   • Crear superusuario: python manage.py createsuperuser")
    print(f"   • Generar datos demo: python manage.py setup_demo_data")
    print(f"   • Resetear datos: python manage.py setup_demo_data --reset")
    print(f"   • Migraciones: python manage.py makemigrations && python manage.py migrate")
    print()
    
    print("=" * 60)
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    try:
        # Abrir navegador automáticamente
        print("🌐 Abriendo navegador...")
        webbrowser.open(server_url)
        
        # Iniciar servidor Django
        os.system(f"python manage.py runserver 127.0.0.1:{port}")
        
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 Servidor detenido")
        print("¡Gracias por usar el Sistema de Gestión de Horas!")
        print("=" * 60)

if __name__ == "__main__":
    main()
