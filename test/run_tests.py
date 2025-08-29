#!/usr/bin/env python
"""
Script para ejecutar pruebas unitarias del Sistema de Gestión de Horas
"""

import os
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Ejecuta todas las pruebas unitarias"""
    print("=" * 70)
    print("🧪 EJECUTANDO SUITE DE PRUEBAS UNITARIAS")
    print("=" * 70)
    
    # Configurar entorno
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_horas.settings')
    
    # Apps a probar
    apps_to_test = [
        'apps.authentication',
        'apps.core', 
        'apps.proyectos',
        'apps.horas',
        'apps.reportes'
    ]
    
    print("Apps a probar:")
    for app in apps_to_test:
        print(f"   • {app}")
    print()
    
    # Ejecutar pruebas por app
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for app in apps_to_test:
        print(f"🔍 Probando {app}...")
        print("-" * 50)
        
        try:
            # Ejecutar pruebas con verbosidad
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', app, 
                '--verbosity=2', '--keepdb'
            ], capture_output=True, text=True, timeout=300)
            
            # Analizar resultado
            output = result.stdout + result.stderr
            print(output)
            
            # Contar resultados
            if 'OK' in output:
                # Extraer número de pruebas
                lines = output.split('\n')
                for line in lines:
                    if 'Ran' in line and 'test' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                num_tests = int(parts[1])
                                total_tests += num_tests
                                print(f"{app}: {num_tests} pruebas pasaron")
                            except ValueError:
                                pass
                        break
            else:
                print(f"{app}: Fallos detectados")
                total_failures += 1
                
        except subprocess.TimeoutExpired:
            print(f"{app}: Timeout - pruebas tomaron más de 5 minutos")
            total_errors += 1
        except Exception as e:
            print(f"💥 {app}: Error ejecutando pruebas - {e}")
            total_errors += 1
        
        print()
    
    # Ejecutar todas las pruebas juntas para reporte final
    print("🎯 EJECUTANDO TODAS LAS PRUEBAS JUNTAS...")
    print("=" * 70)
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', 
            '--verbosity=2', '--keepdb'
        ], capture_output=True, text=True, timeout=600)
        
        output = result.stdout + result.stderr
        print(output)
        
        # Generar reporte final
        print("=" * 70)
        print("📊 REPORTE FINAL DE PRUEBAS")
        print("=" * 70)
        
        if result.returncode == 0:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
            
            # Extraer estadísticas finales
            lines = output.split('\n')
            for line in lines:
                if 'Ran' in line and 'test' in line:
                    print(f"📈 {line}")
                    break
            
            # Buscar tiempo de ejecución
            for line in lines:
                if 'OK' in line and 's' in line:
                    print(f"⏱️  Tiempo de ejecución: {line}")
                    break
                    
        else:
            print("ALGUNAS PRUEBAS FALLARON")
            print("🔍 Revisa el output anterior para detalles")
            
            # Contar fallos
            failure_count = output.count('FAIL:')
            error_count = output.count('ERROR:')
            
            if failure_count > 0:
                print(f"💥 Fallos: {failure_count}")
            if error_count > 0:
                print(f"🚨 Errores: {error_count}")
        
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Las pruebas tomaron más de 10 minutos")
    except Exception as e:
        print(f"💥 ERROR EJECUTANDO PRUEBAS: {e}")
    
    print()
    print("=" * 70)
    print("🏁 PRUEBAS COMPLETADAS")
    print("=" * 70)


def run_coverage():
    """Ejecuta pruebas con coverage si está disponible"""
    print("📊 INTENTANDO EJECUTAR CON COVERAGE...")
    
    try:
        # Verificar si coverage está instalado
        subprocess.run(['coverage', '--version'], 
                      capture_output=True, check=True)
        
        print("Coverage disponible, ejecutando con reporte de cobertura...")
        
        # Ejecutar con coverage
        subprocess.run([
            'coverage', 'run', '--source=.', 'manage.py', 'test'
        ], check=True)
        
        # Generar reporte
        print("\nREPORTE DE COBERTURA:")
        print("-" * 50)
        subprocess.run(['coverage', 'report'])
        
        # Generar reporte HTML si es posible
        try:
            subprocess.run(['coverage', 'html'], check=True)
            print("\n🌐 Reporte HTML generado en htmlcov/index.html")
        except:
            pass
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Coverage no disponible, ejecutando pruebas normales...")
        run_tests()


def main():
    """Función principal"""
    print("🚀 SISTEMA DE GESTIÓN DE HORAS - SUITE DE PRUEBAS")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not Path('manage.py').exists():
        print("Error: No se encontró manage.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        return 1
    
    # Preguntar tipo de ejecución
    print("Opciones de ejecución:")
    print("1. Pruebas normales")
    print("2. Pruebas con coverage (si está disponible)")
    print("3. Solo verificar configuración")
    
    try:
        choice = input("\nSelecciona una opción (1-3) [1]: ").strip() or "1"
        
        if choice == "1":
            run_tests()
        elif choice == "2":
            run_coverage()
        elif choice == "3":
            print("🔧 VERIFICANDO CONFIGURACIÓN...")
            
            # Verificar Django
            try:
                import django
                print(f"Django {django.get_version()} disponible")
            except ImportError:
                print("Django no disponible")
                return 1
            
            # Verificar apps
            for app in ['authentication', 'core', 'proyectos', 'horas', 'reportes']:
                test_file = Path(f'apps/{app}/tests.py')
                if test_file.exists():
                    print(f"Pruebas para {app} disponibles")
                else:
                    print(f"Pruebas para {app} no encontradas")
            
            print("🎯 Configuración verificada")
        else:
            print("Opción inválida")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Ejecución cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
