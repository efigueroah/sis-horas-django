from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

from apps.core.models import Periodo, DiaFeriado
from apps.proyectos.models import Proyecto
from apps.horas.models import RegistroHora


class Command(BaseCommand):
    help = 'Genera datos de demostración para el sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los datos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Eliminando datos existentes...')
            self.reset_data()

        self.stdout.write('🚀 Generando datos de demostración...')
        
        # Crear usuarios de prueba
        users = self.create_demo_users()
        
        # Para cada usuario, crear datos completos
        for user in users:
            self.stdout.write(f'📊 Generando datos para {user.username}...')
            
            # Crear períodos
            periodos = self.create_periods(user)
            
            # Crear proyectos
            proyectos = self.create_projects(user)
            
            # Crear feriados
            self.create_holidays(user)
            
            # Crear registros de horas
            self.create_hour_records(user, proyectos, periodos)

        self.stdout.write(
            self.style.SUCCESS('Datos de demostración generados exitosamente!')
        )
        self.print_summary()

    def reset_data(self):
        """Elimina todos los datos de demostración"""
        RegistroHora.objects.all().delete()
        Proyecto.objects.all().delete()
        DiaFeriado.objects.all().delete()
        Periodo.objects.all().delete()
        # No eliminar usuarios admin existentes
        User.objects.filter(username__in=['demo1', 'demo2']).delete()

    def create_demo_users(self):
        """Crea usuarios de demostración"""
        users = []
        
        # Usuario demo 1
        user1, created = User.objects.get_or_create(
            username='demo1',
            defaults={
                'email': 'demo1@example.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'is_active': True
            }
        )
        if created:
            user1.set_password('demo123')
            user1.save()
            self.stdout.write(f'👤 Usuario creado: {user1.username}')
        users.append(user1)
        
        # Usuario demo 2
        user2, created = User.objects.get_or_create(
            username='demo2',
            defaults={
                'email': 'demo2@example.com',
                'first_name': 'María',
                'last_name': 'González',
                'is_active': True
            }
        )
        if created:
            user2.set_password('demo123')
            user2.save()
            self.stdout.write(f'👤 Usuario creado: {user2.username}')
        users.append(user2)
        
        return users

    def create_periods(self, user):
        """Crea períodos de trabajo"""
        periodos = []
        
        # Período pasado (julio 2025)
        periodo1 = Periodo.objects.create(
            nombre='Julio 2025',
            fecha_inicio=date(2025, 7, 1),
            fecha_fin=date(2025, 7, 31),
            horas_objetivo=160,
            horas_max_dia=8,
            activo=False,
            usuario=user
        )
        periodos.append(periodo1)
        
        # Período actual (agosto 2025) - ACTIVO
        periodo2 = Periodo.objects.create(
            nombre='Agosto 2025',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=168,
            horas_max_dia=8,
            activo=True,
            usuario=user
        )
        periodos.append(periodo2)
        
        # Período futuro (septiembre 2025)
        periodo3 = Periodo.objects.create(
            nombre='Septiembre 2025',
            fecha_inicio=date(2025, 9, 1),
            fecha_fin=date(2025, 9, 30),
            horas_objetivo=160,
            horas_max_dia=8,
            activo=False,
            usuario=user
        )
        periodos.append(periodo3)
        
        self.stdout.write(f'Creados {len(periodos)} períodos')
        return periodos

    def create_projects(self, user):
        """Crea proyectos de demostración"""
        proyectos_data = [
            {
                'nombre': 'Sistema de Gestión Empresarial',
                'cliente': 'TechCorp SA',
                'descripcion': 'Desarrollo de sistema ERP completo con módulos de contabilidad, inventario y RRHH',
                'color_hex': '#007bff',
                'fecha_inicio': date(2025, 6, 1),
                'fecha_fin': date(2025, 12, 31)
            },
            {
                'nombre': 'App Móvil de Delivery',
                'cliente': 'FoodExpress',
                'descripcion': 'Aplicación móvil para pedidos de comida con geolocalización y pagos online',
                'color_hex': '#28a745',
                'fecha_inicio': date(2025, 7, 15),
                'fecha_fin': date(2025, 10, 30)
            },
            {
                'nombre': 'Portal Web Corporativo',
                'cliente': 'InnovateLab',
                'descripcion': 'Sitio web corporativo con CMS personalizado y integración con redes sociales',
                'color_hex': '#ffc107',
                'fecha_inicio': date(2025, 8, 1),
                'fecha_fin': date(2025, 9, 15)
            },
            {
                'nombre': 'Sistema de Facturación',
                'cliente': 'ContableMax',
                'descripcion': 'Sistema de facturación electrónica con integración AFIP',
                'color_hex': '#dc3545',
                'fecha_inicio': date(2025, 5, 1),
                'fecha_fin': date(2025, 8, 31)
            },
            {
                'nombre': 'E-commerce Multitenant',
                'cliente': 'ShopSolutions',
                'descripcion': 'Plataforma de e-commerce para múltiples tiendas con panel de administración',
                'color_hex': '#6f42c1',
                'fecha_inicio': date(2025, 7, 1),
                'fecha_fin': date(2025, 11, 30)
            },
            {
                'nombre': 'API de Integración',
                'cliente': 'DataSync Inc',
                'descripcion': 'API REST para sincronización de datos entre sistemas legacy',
                'color_hex': '#17a2b8',
                'fecha_inicio': date(2025, 8, 15),
                'fecha_fin': date(2025, 9, 30)
            },
            {
                'nombre': 'Dashboard Analytics',
                'cliente': 'MetricsHub',
                'descripcion': 'Dashboard interactivo para visualización de métricas de negocio',
                'color_hex': '#fd7e14',
                'fecha_inicio': date(2025, 6, 15),
                'fecha_fin': date(2025, 8, 15)
            },
            {
                'nombre': 'Sistema de Reservas',
                'cliente': 'HotelChain',
                'descripcion': 'Sistema de reservas online para cadena hotelera con múltiples sucursales',
                'color_hex': '#20c997',
                'fecha_inicio': date(2025, 7, 1),
                'fecha_fin': date(2025, 10, 15)
            }
        ]
        
        proyectos = []
        for data in proyectos_data:
            proyecto = Proyecto.objects.create(
                usuario=user,
                **data
            )
            proyectos.append(proyecto)
        
        # Desactivar algunos proyectos aleatoriamente
        for proyecto in random.sample(proyectos, 2):
            proyecto.activo = False
            proyecto.save()
        
        self.stdout.write(f'🏗️  Creados {len(proyectos)} proyectos')
        return proyectos

    def create_holidays(self, user):
        """Crea días feriados"""
        feriados_2025 = [
            (date(2025, 1, 1), 'Año Nuevo'),
            (date(2025, 2, 24), 'Carnaval'),
            (date(2025, 2, 25), 'Carnaval'),
            (date(2025, 3, 24), 'Día Nacional de la Memoria'),
            (date(2025, 4, 18), 'Viernes Santo'),
            (date(2025, 5, 1), 'Día del Trabajador'),
            (date(2025, 5, 25), 'Día de la Revolución de Mayo'),
            (date(2025, 6, 20), 'Día de la Bandera'),
            (date(2025, 7, 9), 'Día de la Independencia'),
            (date(2025, 8, 17), 'Paso a la Inmortalidad del Gral. San Martín'),
            (date(2025, 10, 12), 'Día del Respeto a la Diversidad Cultural'),
            (date(2025, 11, 20), 'Día de la Soberanía Nacional'),
            (date(2025, 12, 8), 'Inmaculada Concepción de María'),
            (date(2025, 12, 25), 'Navidad'),
        ]
        
        for fecha, nombre in feriados_2025:
            DiaFeriado.objects.get_or_create(
                fecha=fecha,
                usuario=user,
                defaults={'nombre': nombre}
            )
        
        self.stdout.write(f'🎉 Creados {len(feriados_2025)} feriados')

    def create_hour_records(self, user, proyectos, periodos):
        """Crea registros de horas"""
        periodo_activo = next((p for p in periodos if p.activo), periodos[0])
        
        # Generar registros para el período activo
        fecha_actual = periodo_activo.fecha_inicio
        total_registros = 0
        
        while fecha_actual <= periodo_activo.fecha_fin:
            # Solo generar para días hábiles (no fines de semana ni feriados)
            if (fecha_actual.weekday() < 5 and 
                not DiaFeriado.objects.filter(fecha=fecha_actual, usuario=user).exists()):
                
                # 80% de probabilidad de tener registros en un día hábil
                if random.random() < 0.8:
                    # Número de registros por día (1-3)
                    num_registros = random.randint(1, 3)
                    horas_dia = 0
                    
                    for _ in range(num_registros):
                        if horas_dia >= 8:  # No exceder 8 horas por día
                            break
                            
                        proyecto = random.choice(proyectos)
                        horas_registro = random.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0])
                        
                        # Asegurar que no exceda el límite diario
                        if horas_dia + horas_registro > 8:
                            horas_registro = 8 - horas_dia
                        
                        tipo_tarea = random.choice(['tarea', 'reunion'])
                        
                        # Generar descripción realista
                        descripciones = {
                            'tarea': [
                                'Desarrollo de funcionalidades del módulo principal',
                                'Corrección de bugs reportados por QA',
                                'Implementación de nuevas características',
                                'Refactoring de código legacy',
                                'Optimización de consultas de base de datos',
                                'Documentación técnica del proyecto',
                                'Testing unitario y de integración',
                                'Configuración de entorno de desarrollo'
                            ],
                            'reunion': [
                                'Reunión de planificación de sprint',
                                'Daily standup con el equipo',
                                'Revisión de código con senior developer',
                                'Reunión con cliente para definir requerimientos',
                                'Sesión de brainstorming para nuevas funcionalidades',
                                'Retrospectiva del sprint anterior',
                                'Reunión de seguimiento del proyecto',
                                'Capacitación en nuevas tecnologías'
                            ]
                        }
                        
                        descripcion = random.choice(descripciones[tipo_tarea])
                        
                        RegistroHora.objects.create(
                            fecha=fecha_actual,
                            proyecto=proyecto,
                            horas=Decimal(str(horas_registro)),
                            descripcion=descripcion,
                            tipo_tarea=tipo_tarea,
                            periodo=periodo_activo,
                            usuario=user
                        )
                        
                        horas_dia += horas_registro
                        total_registros += 1
            
            fecha_actual += timedelta(days=1)
        
        self.stdout.write(f'Creados {total_registros} registros de horas')

    def print_summary(self):
        """Imprime resumen de datos creados"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMEN DE DATOS GENERADOS')
        self.stdout.write('='*50)
        
        total_users = User.objects.count()
        total_periods = Periodo.objects.count()
        total_projects = Proyecto.objects.count()
        total_hours = RegistroHora.objects.count()
        total_holidays = DiaFeriado.objects.count()
        
        self.stdout.write(f'👥 Usuarios: {total_users}')
        self.stdout.write(f'Períodos: {total_periods}')
        self.stdout.write(f'🏗️  Proyectos: {total_projects}')
        self.stdout.write(f'Registros de horas: {total_hours}')
        self.stdout.write(f'🎉 Días feriados: {total_holidays}')
        
        self.stdout.write('\n👤 USUARIOS DE PRUEBA:')
        self.stdout.write('  • admin / admin123 (superusuario)')
        self.stdout.write('  • demo1 / demo123 (Juan Pérez)')
        self.stdout.write('  • demo2 / demo123 (María González)')
        
        self.stdout.write('\n🚀 ¡El sistema está listo para usar!')
        self.stdout.write('='*50)
