#!/usr/bin/env python3
"""
Script para iniciar el servidor en modo producción con Gunicorn
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Configurar variables de entorno para producción
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
    os.environ['DEBUG'] = 'False'
    
    # Directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("Iniciando Sistema de Gestión de Horas en modo PRODUCCIÓN...")
    print("=" * 60)
    
    # Verificar que el entorno virtual esté activado
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  ADVERTENCIA: No se detectó entorno virtual activado")
        print("   Ejecuta: source venv/bin/activate")
        return
    
    # Recolectar archivos estáticos
    print("📦 Recolectando archivos estáticos...")
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
    
    # Aplicar migraciones
    print("🔄 Aplicando migraciones...")
    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
    
    # Iniciar Gunicorn
    print("🚀 Iniciando servidor Gunicorn...")
    print("   URL: http://localhost:8000")
    print("   Modo: PRODUCCIÓN")
    print("   Workers: 3")
    print("=" * 60)
    
    try:
        subprocess.run([
            'gunicorn',
            'sis_horas.wsgi:application',
            '--config', 'gunicorn.conf.py'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar Gunicorn: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
