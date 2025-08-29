from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from .models import ReporteExportacion, ConfiguracionReporte
from apps.core.models import Periodo
from apps.proyectos.models import Proyecto
from apps.horas.models import RegistroHora
from decimal import Decimal


class ReporteExportacionModelTest(TestCase):
    """Pruebas para el modelo ReporteExportacion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_reporte_exportacion_creation(self):
        """Prueba la creación de un reporte de exportación"""
        reporte = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='test_export.csv',
            formato='csv',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            filtros_aplicados={'proyecto': 'Test Project'},
            total_registros=50,
            tamaño_archivo=1024
        )
        
        self.assertEqual(reporte.nombre_archivo, 'test_export.csv')
        self.assertEqual(reporte.formato, 'csv')
        self.assertEqual(reporte.total_registros, 50)
        self.assertEqual(reporte.tamaño_archivo, 1024)
    
    def test_reporte_exportacion_str_method(self):
        """Prueba el método __str__ del reporte"""
        reporte = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='test_export.csv',
            formato='csv',
            total_registros=50,
            tamaño_archivo=1024
        )
        
        str_repr = str(reporte)
        self.assertIn('test_export.csv', str_repr)
        self.assertIn(reporte.created_at.strftime('%d/%m/%Y %H:%M'), str_repr)
    
    def test_tamaño_legible_property(self):
        """Prueba la propiedad tamaño_legible"""
        # Tamaño en bytes
        reporte1 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='small.csv',
            formato='csv',
            tamaño_archivo=512
        )
        self.assertEqual(reporte1.tamaño_legible, '512 B')
        
        # Tamaño en KB
        reporte2 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='medium.csv',
            formato='csv',
            tamaño_archivo=2048
        )
        self.assertEqual(reporte2.tamaño_legible, '2.0 KB')
        
        # Tamaño en MB
        reporte3 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='large.csv',
            formato='csv',
            tamaño_archivo=2097152  # 2 MB
        )
        self.assertEqual(reporte3.tamaño_legible, '2.0 MB')
    
    def test_periodo_texto_property(self):
        """Prueba la propiedad periodo_texto"""
        # Con ambas fechas
        reporte1 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='test1.csv',
            formato='csv',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31)
        )
        self.assertEqual(reporte1.periodo_texto, '01/08/2025 - 31/08/2025')
        
        # Solo fecha inicio
        reporte2 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='test2.csv',
            formato='csv',
            fecha_inicio=date(2025, 8, 1)
        )
        self.assertEqual(reporte2.periodo_texto, 'Desde 01/08/2025')
        
        # Solo fecha fin
        reporte3 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='test3.csv',
            formato='csv',
            fecha_fin=date(2025, 8, 31)
        )
        self.assertEqual(reporte3.periodo_texto, 'Hasta 31/08/2025')
        
        # Sin fechas
        reporte4 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='test4.csv',
            formato='csv'
        )
        self.assertEqual(reporte4.periodo_texto, 'Todos los registros')


class ConfiguracionReporteModelTest(TestCase):
    """Pruebas para el modelo ConfiguracionReporte"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_configuracion_reporte_auto_creation(self):
        """Prueba que se crea automáticamente la configuración al crear usuario"""
        # La configuración debe crearse automáticamente por el signal
        self.assertTrue(hasattr(self.user, 'config_reportes'))
        self.assertIsInstance(self.user.config_reportes, ConfiguracionReporte)
    
    def test_configuracion_reporte_defaults(self):
        """Prueba los valores por defecto de la configuración"""
        config = self.user.config_reportes
        
        self.assertEqual(config.separador_csv, ',')
        self.assertTrue(config.incluir_encabezados)
        self.assertEqual(config.formato_fecha, '%d/%m/%Y')
        self.assertTrue(config.incluir_proyecto)
        self.assertTrue(config.incluir_cliente)
        self.assertTrue(config.incluir_descripcion)
        self.assertTrue(config.incluir_tipo_tarea)
        self.assertFalse(config.incluir_periodo)
        self.assertFalse(config.agrupar_por_proyecto)
        self.assertFalse(config.agrupar_por_fecha)
        self.assertTrue(config.incluir_totales)
    
    def test_configuracion_reporte_str_method(self):
        """Prueba el método __str__ de la configuración"""
        config = self.user.config_reportes
        self.assertEqual(str(config), 'Configuración de testuser')
    
    def test_get_columnas_exportacion_method(self):
        """Prueba el método get_columnas_exportacion"""
        config = self.user.config_reportes
        
        # Configuración por defecto
        columnas = config.get_columnas_exportacion()
        expected_columns = ['fecha', 'horas', 'proyecto', 'cliente', 'descripcion', 'tipo_tarea']
        self.assertEqual(set(columnas), set(expected_columns))
        
        # Modificar configuración
        config.incluir_cliente = False
        config.incluir_periodo = True
        config.save()
        
        columnas = config.get_columnas_exportacion()
        expected_columns = ['fecha', 'horas', 'proyecto', 'descripcion', 'tipo_tarea', 'periodo']
        self.assertEqual(set(columnas), set(expected_columns))


class ReporteViewsTest(TestCase):
    """Pruebas para las vistas de reportes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear algunos reportes de prueba
        self.reporte1 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='export1.csv',
            formato='csv',
            total_registros=25,
            tamaño_archivo=1024
        )
        self.reporte2 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='export2.xlsx',
            formato='xlsx',
            total_registros=50,
            tamaño_archivo=2048
        )
    
    def test_reporte_list_view_requires_login(self):
        """Prueba que la lista de reportes requiere autenticación"""
        response = self.client.get(reverse('reportes:reporte_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_reporte_list_view_authenticated(self):
        """Prueba la vista de lista de reportes con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reportes:reporte_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'export1.csv')
        self.assertContains(response, 'export2.xlsx')
        self.assertContains(response, 'CSV')
        self.assertContains(response, 'XLSX')
    
    def test_exportar_view(self):
        """Prueba la vista de exportación"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reportes:exportar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exportar')
    
    def test_configuracion_view(self):
        """Prueba la vista de configuración"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reportes:configuracion'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Configuración')


class ReporteAPIViewsTest(TestCase):
    """Pruebas para las APIs de reportes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            activo=True,
            usuario=self.user
        )
        self.proyecto = Proyecto.objects.create(
            nombre='Test Project',
            cliente='Test Client',
            usuario=self.user
        )
        self.registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.0'),
            descripcion='Test work',
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
        
        # Crear reportes de prueba
        self.reporte1 = ReporteExportacion.objects.create(
            usuario=self.user,
            nombre_archivo='export1.csv',
            formato='csv',
            total_registros=1,
            tamaño_archivo=512
        )
    
    def test_exportar_csv_api_view(self):
        """Prueba la API de exportación CSV"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/reportes/api/exportar/csv/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Verificar contenido CSV
        content = response.content.decode('utf-8')
        self.assertIn('fecha,proyecto,horas,tipo_tarea', content)
    
    def test_historial_exportacion_api_view(self):
        """Prueba la API de historial de exportaciones"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/reportes/api/historial/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre_archivo'], 'export1.csv')
        self.assertEqual(data[0]['formato'], 'csv')


class ReportePermissionsTest(TestCase):
    """Pruebas de permisos para reportes"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Crear reporte para user1
        self.reporte_user1 = ReporteExportacion.objects.create(
            usuario=self.user1,
            nombre_archivo='user1_export.csv',
            formato='csv',
            total_registros=10,
            tamaño_archivo=1024
        )
    
    def test_user_can_only_see_own_reports(self):
        """Prueba que los usuarios solo ven sus propios reportes"""
        # Login como user2
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('reportes:reporte_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'user1_export.csv')
    
    def test_api_returns_only_user_reports(self):
        """Prueba que las APIs solo retornan reportes del usuario"""
        # Crear reporte para user2
        ReporteExportacion.objects.create(
            usuario=self.user2,
            nombre_archivo='user2_export.csv',
            formato='csv',
            total_registros=5,
            tamaño_archivo=512
        )
        
        # Login como user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/reportes/api/historial/')
        
        data = response.json()
        self.assertEqual(len(data), 1)  # Solo su reporte
        self.assertEqual(data[0]['nombre_archivo'], 'user1_export.csv')
    
    def test_user_configuration_isolation(self):
        """Prueba que las configuraciones están aisladas por usuario"""
        # Modificar configuración de user1
        config1 = self.user1.config_reportes
        config1.separador_csv = ';'
        config1.incluir_cliente = False
        config1.save()
        
        # Verificar que user2 mantiene configuración por defecto
        config2 = self.user2.config_reportes
        self.assertEqual(config2.separador_csv, ',')
        self.assertTrue(config2.incluir_cliente)


class ReporteIntegrationTest(TestCase):
    """Pruebas de integración para reportes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear datos completos de prueba
        self.periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            activo=True,
            usuario=self.user
        )
        
        self.proyecto1 = Proyecto.objects.create(
            nombre='Project Alpha',
            cliente='Client A',
            usuario=self.user
        )
        
        self.proyecto2 = Proyecto.objects.create(
            nombre='Project Beta',
            cliente='Client B',
            usuario=self.user
        )
        
        # Crear varios registros de horas
        RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto1,
            horas=Decimal('4.0'),
            descripcion='Development work',
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
        
        RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto2,
            horas=Decimal('2.5'),
            descripcion='Client meeting',
            tipo_tarea='reunion',
            periodo=self.periodo,
            usuario=self.user
        )
        
        RegistroHora.objects.create(
            fecha=date(2025, 8, 16),
            proyecto=self.proyecto1,
            horas=Decimal('3.5'),
            descripcion='Code review',
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
    
    def test_csv_export_contains_all_data(self):
        """Prueba que la exportación CSV contiene todos los datos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/reportes/api/exportar/csv/')
        
        content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        
        # Verificar encabezado
        self.assertIn('fecha,proyecto,horas,tipo_tarea', lines[0])
        
        # Verificar que hay 4 líneas (encabezado + 3 registros)
        self.assertEqual(len(lines), 4)
        
        # Verificar contenido
        self.assertIn('Project Alpha', content)
        self.assertIn('Project Beta', content)
        self.assertIn('4.0', content)
        self.assertIn('2.5', content)
        self.assertIn('3.5', content)
        self.assertIn('tarea', content)
        self.assertIn('reunion', content)
    
    def test_export_respects_user_configuration(self):
        """Prueba que la exportación respeta la configuración del usuario"""
        # Modificar configuración
        config = self.user.config_reportes
        config.separador_csv = ';'
        config.incluir_cliente = True
        config.incluir_descripcion = False
        config.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/reportes/api/exportar/csv/')
        
        content = response.content.decode('utf-8')
        
        # Verificar separador
        self.assertIn(';', content)
        self.assertNotIn(',', content.replace('Client A', '').replace('Client B', ''))
        
        # Verificar que incluye cliente pero no descripción
        self.assertIn('Client A', content)
        self.assertIn('Client B', content)
        self.assertNotIn('Development work', content)
        self.assertNotIn('Client meeting', content)
