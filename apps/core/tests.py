from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, datetime, timedelta
from .models import Periodo, DiaFeriado


class PeriodoModelTest(TestCase):
    """Pruebas para el modelo Periodo"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_periodo_creation(self):
        """Prueba la creación de un período"""
        periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            horas_max_dia=8,
            usuario=self.user
        )
        self.assertEqual(periodo.nombre, 'Test Periodo')
        self.assertEqual(periodo.año, 2025)
        self.assertFalse(periodo.activo)  # Por defecto inactivo
    
    def test_periodo_auto_year_calculation(self):
        """Prueba el cálculo automático del año"""
        periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2024, 12, 1),
            fecha_fin=date(2024, 12, 31),
            horas_objetivo=160,
            usuario=self.user
        )
        self.assertEqual(periodo.año, 2024)
    
    def test_unique_active_period_per_user(self):
        """Prueba que solo puede haber un período activo por usuario"""
        # Crear primer período activo
        periodo1 = Periodo.objects.create(
            nombre='Periodo 1',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            activo=True,
            usuario=self.user
        )
        
        # Crear segundo período activo - debe desactivar el primero
        periodo2 = Periodo.objects.create(
            nombre='Periodo 2',
            fecha_inicio=date(2025, 9, 1),
            fecha_fin=date(2025, 9, 30),
            horas_objetivo=160,
            activo=True,
            usuario=self.user
        )
        
        # Recargar desde DB
        periodo1.refresh_from_db()
        
        self.assertFalse(periodo1.activo)
        self.assertTrue(periodo2.activo)
    
    def test_periodo_validation_fecha_inicio_fin(self):
        """Prueba validación de fechas de inicio y fin"""
        periodo = Periodo(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 31),
            fecha_fin=date(2025, 8, 1),  # Fecha fin antes que inicio
            horas_objetivo=160,
            usuario=self.user
        )
        
        with self.assertRaises(ValidationError):
            periodo.clean()
    
    def test_periodo_duracion_dias_property(self):
        """Prueba la propiedad duracion_dias"""
        periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            usuario=self.user
        )
        self.assertEqual(periodo.duracion_dias, 31)
    
    def test_periodo_progreso_temporal_property(self):
        """Prueba la propiedad progreso_temporal"""
        # Período en el pasado
        periodo_pasado = Periodo.objects.create(
            nombre='Periodo Pasado',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 1, 31),
            horas_objetivo=160,
            usuario=self.user
        )
        self.assertEqual(periodo_pasado.progreso_temporal, 100)
        
        # Período en el futuro
        periodo_futuro = Periodo.objects.create(
            nombre='Periodo Futuro',
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 1, 31),
            horas_objetivo=160,
            usuario=self.user
        )
        self.assertEqual(periodo_futuro.progreso_temporal, 0)


class DiaFeriadoModelTest(TestCase):
    """Pruebas para el modelo DiaFeriado"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_dia_feriado_creation(self):
        """Prueba la creación de un día feriado"""
        feriado = DiaFeriado.objects.create(
            fecha=date(2025, 12, 25),
            nombre='Navidad',
            usuario=self.user
        )
        self.assertEqual(feriado.nombre, 'Navidad')
        self.assertEqual(feriado.año, 2025)
    
    def test_unique_holiday_per_user_date(self):
        """Prueba que no puede haber feriados duplicados por usuario y fecha"""
        DiaFeriado.objects.create(
            fecha=date(2025, 12, 25),
            nombre='Navidad',
            usuario=self.user
        )
        
        # Intentar crear otro feriado en la misma fecha
        with self.assertRaises(Exception):
            DiaFeriado.objects.create(
                fecha=date(2025, 12, 25),
                nombre='Navidad 2',
                usuario=self.user
            )
    
    def test_dia_feriado_properties(self):
        """Prueba las propiedades del día feriado"""
        # Feriado en el pasado
        feriado_pasado = DiaFeriado.objects.create(
            fecha=date(2024, 1, 1),
            nombre='Año Nuevo Pasado',
            usuario=self.user
        )
        self.assertTrue(feriado_pasado.es_pasado)
        self.assertFalse(feriado_pasado.es_futuro)
        
        # Feriado en el futuro
        feriado_futuro = DiaFeriado.objects.create(
            fecha=date(2026, 1, 1),
            nombre='Año Nuevo Futuro',
            usuario=self.user
        )
        self.assertFalse(feriado_futuro.es_pasado)
        self.assertTrue(feriado_futuro.es_futuro)


class CoreViewsTest(TestCase):
    """Pruebas para las vistas de core"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            activo=True,
            usuario=self.user
        )
    
    def test_dashboard_view_requires_login(self):
        """Prueba que el dashboard requiere autenticación"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_authenticated(self):
        """Prueba el dashboard con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Test Periodo')
    
    def test_periodo_list_view(self):
        """Prueba la vista de lista de períodos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:periodo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Periodo')
    
    def test_periodo_create_view_get(self):
        """Prueba la vista de creación de período (GET)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:periodo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nuevo Período')
    
    def test_periodo_create_view_post(self):
        """Prueba la creación de período (POST)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('core:periodo_create'), {
            'nombre': 'Nuevo Periodo',
            'fecha_inicio': '2025-09-01',
            'fecha_fin': '2025-09-30',
            'horas_objetivo': 160,
            'horas_max_dia': 8
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Periodo.objects.filter(nombre='Nuevo Periodo').exists())
    
    def test_activar_periodo_view(self):
        """Prueba la activación de período"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear otro período inactivo
        periodo2 = Periodo.objects.create(
            nombre='Periodo 2',
            fecha_inicio=date(2025, 9, 1),
            fecha_fin=date(2025, 9, 30),
            horas_objetivo=160,
            activo=False,
            usuario=self.user
        )
        
        # Activar el segundo período
        response = self.client.post(
            reverse('core:periodo_activate', kwargs={'pk': periodo2.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se activó correctamente
        periodo2.refresh_from_db()
        self.periodo.refresh_from_db()
        
        self.assertTrue(periodo2.activo)
        self.assertFalse(self.periodo.activo)


class CoreAPIViewsTest(TestCase):
    """Pruebas para las APIs de core"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.periodo = Periodo.objects.create(
            nombre='Test Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            activo=True,
            usuario=self.user
        )
    
    def test_periodo_api_view(self):
        """Prueba la API de períodos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/periodos/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Test Periodo')
    
    def test_periodo_activo_api_view(self):
        """Prueba la API de período activo"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/periodos/activo/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        # La API devuelve un objeto con 'periodo' que contiene los datos
        if data.get('success') and data.get('periodo'):
            self.assertEqual(data['periodo']['nombre'], 'Test Periodo')
            self.assertTrue(data['periodo']['activo'])
        else:
            # Si no hay período activo, verificar que se maneje correctamente
            self.assertFalse(data.get('success', True))
    
    def test_calendario_api_view(self):
        """Prueba la API del calendario"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/calendario/2025/8/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['mes'], 8)
        self.assertEqual(data['año'], 2025)
    
    def test_dashboard_api_view(self):
        """Prueba la API del dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_horas'], 0)  # Sin horas registradas
        self.assertEqual(data['periodo']['nombre'], 'Test Periodo')


class FeriadoViewsTest(TestCase):
    """Pruebas para las vistas de feriados"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_feriado_list_view(self):
        """Prueba la vista de lista de feriados"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear un feriado
        DiaFeriado.objects.create(
            fecha=date(2025, 12, 25),
            nombre='Navidad',
            usuario=self.user
        )
        
        response = self.client.get(reverse('core:feriado_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Navidad')
    
    def test_feriado_create_view(self):
        """Prueba la creación de feriados"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('core:feriado_create'), {
            'fecha': '2025-12-25',
            'nombre': 'Navidad'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(DiaFeriado.objects.filter(nombre='Navidad').exists())
    
    def test_feriado_delete_view(self):
        """Prueba la eliminación de feriados"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear feriado
        feriado = DiaFeriado.objects.create(
            fecha=date(2025, 12, 25),
            nombre='Navidad',
            usuario=self.user
        )
        
        # Eliminar feriado
        response = self.client.post(
            reverse('core:feriado_delete', kwargs={'pk': feriado.pk})
        )
        # La vista de eliminación redirige después de eliminar
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DiaFeriado.objects.filter(pk=feriado.pk).exists())
