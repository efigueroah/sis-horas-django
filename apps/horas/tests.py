from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta
from .models import RegistroHora
from apps.core.models import Periodo, DiaFeriado, ConfiguracionSistema
from apps.proyectos.models import Proyecto
from apps.authentication.models import UserProfile


class HoraViewsTestCase(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Crear perfil de usuario con configuración
        self.profile = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'incremento_horas': Decimal('0.5'),
                'horas_minimas': Decimal('0.5'),
                'horas_maximas': Decimal('12.0'),
                'horas_max_dia': 8
            }
        )[0]
        
        # Crear proyecto
        self.proyecto = Proyecto.objects.create(
            nombre='Proyecto Test',
            cliente='Cliente Test',
            usuario=self.user,
            activo=True
        )
        
        # Crear período activo
        self.periodo = Periodo.objects.create(
            nombre='Período Test',
            fecha_inicio=date.today() - timedelta(days=30),
            fecha_fin=date.today() + timedelta(days=30),
            horas_objetivo=160,
            horas_max_dia=Decimal('7.5'),
            activo=True,
            usuario=self.user
        )
        
        # Crear configuración del sistema
        ConfiguracionSistema.objects.get_or_create(pk=1)
        
        self.client = Client()
        self.client.force_login(self.user)

    def test_hora_create_view_get(self):
        """Test GET de la vista de crear horas simple"""
        url = reverse('horas:hora_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar Horas de Trabajo')
        
        # Verificar que las variables de contexto están presentes
        self.assertIn('incremento_horas', response.context)
        self.assertIn('horas_minimas', response.context)
        self.assertIn('horas_maximas', response.context)
        
        # Verificar valores correctos
        self.assertEqual(response.context['incremento_horas'], 0.5)

    def test_hora_create_multiple_view_get(self):
        """Test GET de la vista de crear horas múltiples"""
        url = reverse('horas:hora_create_multiple')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar Horas de Trabajo')
        
        # Verificar que las variables de contexto están presentes
        self.assertIn('proyectos', response.context)
        self.assertIn('incremento_horas', response.context)
        self.assertIn('horas_minimas', response.context)
        self.assertIn('horas_maximas', response.context)
        self.assertIn('limite_diario', response.context)
        
        # Verificar valores correctos
        self.assertEqual(response.context['limite_diario'], 7.5)  # Del período activo
        self.assertEqual(response.context['incremento_horas'], 0.5)

    def test_hora_create_view_with_fecha_param(self):
        """Test GET con parámetro fecha"""
        url = reverse('horas:hora_create') + '?fecha=2025-08-13'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar Horas de Trabajo')

    def test_hora_update_view_get(self):
        """Test GET de la vista de editar horas"""
        # Crear registro de horas
        registro = RegistroHora.objects.create(
            usuario=self.user,
            fecha=date.today(),
            proyecto=self.proyecto,
            horas=Decimal('2.0'),
            descripcion='Test registro',
            tipo_tarea='tarea'
        )
        
        url = reverse('horas:hora_update', kwargs={'pk': registro.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar Registro de Horas')

    def test_hora_por_fecha_api(self):
        """Test de la API de horas por fecha"""
        # Crear registro
        RegistroHora.objects.create(
            usuario=self.user,
            fecha=date(2025, 8, 13),
            proyecto=self.proyecto,
            horas=Decimal('2.0'),
            descripcion='Test registro',
            tipo_tarea='tarea'
        )
        
        url = '/horas/api/fecha/2025-08-13/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['horas'], 2.0)
        self.assertEqual(data[0]['descripcion'], 'Test registro')

    def test_limite_diario_periodo_activo(self):
        """Test que se respeta el límite diario del período activo en vista múltiple"""
        url = reverse('horas:hora_create_multiple')
        response = self.client.get(url)
        
        # Debe usar el límite del período activo (7.5h), no el por defecto (8h)
        self.assertEqual(response.context['limite_diario'], 7.5)


class RegistroHoraModelTest(TestCase):
    """Pruebas para el modelo RegistroHora"""
    
    def setUp(self):
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
            horas_max_dia=8,
            activo=True,
            usuario=self.user
        )
        self.proyecto = Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
    
    def test_registro_hora_creation(self):
        """Prueba la creación de un registro de horas"""
        registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.5'),
            descripcion='Test work',
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
        self.assertEqual(registro.horas, Decimal('4.5'))
        self.assertEqual(registro.tipo_tarea, 'tarea')
        self.assertEqual(registro.proyecto, self.proyecto)
    
    def test_registro_hora_str_method(self):
        """Prueba el método __str__ del registro"""
        registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.5'),
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
        expected = f"2025-08-15 - {self.proyecto.nombre} - 4.5h (Tarea)"
        self.assertEqual(str(registro), expected)
    
    def test_registro_hora_horas_validation(self):
        """Prueba la validación de horas"""
        # Horas válidas
        registro = RegistroHora(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.5'),
            periodo=self.periodo,
            usuario=self.user
        )
        registro.full_clean()  # No debe lanzar excepción
        
        # Horas inválidas - menos del mínimo
        registro.horas = Decimal('0.25')
        with self.assertRaises(ValidationError):
            registro.full_clean()
        
        # Horas inválidas - más del máximo
        registro.horas = Decimal('15.0')
        with self.assertRaises(ValidationError):
            registro.full_clean()
    
    def test_registro_hora_multiples_validation(self):
        """Prueba la validación de múltiplos de 0.5"""
        registro = RegistroHora(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.25'),  # No es múltiplo de 0.5
            periodo=self.periodo,
            usuario=self.user
        )
        
        with self.assertRaises(ValidationError):
            registro.clean()
    
    def test_registro_hora_weekend_validation(self):
        """Prueba la validación de fines de semana"""
        # Sábado (weekday = 5)
        sabado = date(2025, 8, 16)  # Asumiendo que es sábado
        
        registro = RegistroHora(
            fecha=sabado,
            proyecto=self.proyecto,
            horas=Decimal('4.0'),
            periodo=self.periodo,
            usuario=self.user
        )
        
        # Verificar que es fin de semana
        if sabado.weekday() >= 5:
            with self.assertRaises(ValidationError):
                registro.clean()
    
    def test_registro_hora_holiday_validation(self):
        """Prueba la validación de días feriados"""
        # Crear un día feriado
        feriado = DiaFeriado.objects.create(
            fecha=date(2025, 8, 15),
            nombre='Test Holiday',
            usuario=self.user
        )
        
        registro = RegistroHora(
            fecha=feriado.fecha,
            proyecto=self.proyecto,
            horas=Decimal('4.0'),
            periodo=self.periodo,
            usuario=self.user
        )
        
        with self.assertRaises(ValidationError):
            registro.clean()
    
    def test_registro_hora_max_hours_per_day_validation(self):
        """Prueba la validación de horas máximas por día"""
        fecha_test = date(2025, 8, 15)
        
        # Crear primer registro de 6 horas
        RegistroHora.objects.create(
            fecha=fecha_test,
            proyecto=self.proyecto,
            horas=Decimal('6.0'),
            periodo=self.periodo,
            usuario=self.user
        )
        
        # Intentar crear segundo registro que exceda el límite
        registro2 = RegistroHora(
            fecha=fecha_test,
            proyecto=self.proyecto,
            horas=Decimal('3.0'),  # 6 + 3 = 9 > 8 (máximo)
            periodo=self.periodo,
            usuario=self.user
        )
        
        with self.assertRaises(ValidationError):
            registro2.clean()
    
    def test_registro_hora_auto_periodo_assignment(self):
        """Prueba la asignación automática del período activo"""
        registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.0'),
            usuario=self.user
            # No especificar período
        )
        
        # Debe asignarse automáticamente el período activo
        self.assertEqual(registro.periodo, self.periodo)
    
    def test_registro_hora_properties(self):
        """Prueba las propiedades del registro"""
        registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.5'),
            tipo_tarea='reunion',
            periodo=self.periodo,
            usuario=self.user
        )
        
        # Propiedad horas_float
        self.assertEqual(registro.horas_float, 4.5)
        
        # Propiedad tipo_tarea_icon
        self.assertEqual(registro.tipo_tarea_icon, 'fas fa-users')
        
        # Propiedad tipo_tarea_color
        self.assertEqual(registro.tipo_tarea_color, 'warning')


class RegistroHoraClassMethodsTest(TestCase):
    """Pruebas para los métodos de clase de RegistroHora"""
    
    def setUp(self):
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
        self.proyecto1 = Proyecto.objects.create(
            nombre='Project 1',
            cliente='Client 1',
            usuario=self.user
        )
        self.proyecto2 = Proyecto.objects.create(
            nombre='Project 2',
            cliente='Client 2',
            usuario=self.user
        )
        
        # Crear algunos registros de prueba
        RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto1,
            horas=Decimal('4.0'),
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
        RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto2,
            horas=Decimal('2.5'),
            tipo_tarea='reunion',
            periodo=self.periodo,
            usuario=self.user
        )
        RegistroHora.objects.create(
            fecha=date(2025, 8, 16),
            proyecto=self.proyecto1,
            horas=Decimal('3.0'),
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
    
    def test_get_resumen_por_proyecto(self):
        """Prueba el resumen por proyecto"""
        resumen = RegistroHora.get_resumen_por_proyecto(self.user)
        
        self.assertEqual(len(resumen), 2)  # Dos proyectos
        
        # Verificar totales por proyecto
        for item in resumen:
            if item['proyecto__nombre'] == 'Project 1':
                self.assertEqual(item['total_horas'], Decimal('7.0'))  # 4.0 + 3.0
                self.assertEqual(item['total_registros'], 2)
            elif item['proyecto__nombre'] == 'Project 2':
                self.assertEqual(item['total_horas'], Decimal('2.5'))
                self.assertEqual(item['total_registros'], 1)
    
    def test_get_resumen_por_tipo_tarea(self):
        """Prueba el resumen por tipo de tarea"""
        resumen = RegistroHora.get_resumen_por_tipo_tarea(self.user)
        
        self.assertEqual(len(resumen), 2)  # Dos tipos
        
        for item in resumen:
            if item['tipo_tarea'] == 'tarea':
                self.assertEqual(item['total_horas'], Decimal('7.0'))  # 4.0 + 3.0
                self.assertEqual(item['total_registros'], 2)
            elif item['tipo_tarea'] == 'reunion':
                self.assertEqual(item['total_horas'], Decimal('2.5'))
                self.assertEqual(item['total_registros'], 1)
    
    def test_get_horas_por_fecha(self):
        """Prueba obtener horas por fecha"""
        horas_fecha = RegistroHora.get_horas_por_fecha(self.user, date(2025, 8, 15))
        
        self.assertEqual(horas_fecha.count(), 2)  # Dos registros en esa fecha
        
        total_horas = sum(h.horas for h in horas_fecha)
        self.assertEqual(total_horas, Decimal('6.5'))  # 4.0 + 2.5
    
    def test_get_total_horas_dia(self):
        """Prueba obtener total de horas por día"""
        total = RegistroHora.get_total_horas_dia(self.user, date(2025, 8, 15))
        self.assertEqual(total, Decimal('6.5'))  # 4.0 + 2.5
        
        total_vacio = RegistroHora.get_total_horas_dia(self.user, date(2025, 8, 20))
        self.assertEqual(total_vacio, Decimal('0'))


class HoraViewsTest(TestCase):
    """Pruebas para las vistas de horas"""
    
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
        self.proyecto = Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
        self.registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.0'),
            descripcion='Test work',
            periodo=self.periodo,
            usuario=self.user
        )
    
    def test_hora_list_view_requires_login(self):
        """Prueba que la lista de horas requiere autenticación"""
        response = self.client.get(reverse('horas:hora_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_hora_list_view_authenticated(self):
        """Prueba la vista de lista de horas con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('horas:hora_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, '4.0')
    
    def test_hora_create_view_get(self):
        """Prueba la vista de creación de horas (GET)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('horas:hora_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar Horas')
    
    def test_hora_create_view_post(self):
        """Prueba la creación de horas (POST)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('horas:hora_create'), {
            'fecha': '2025-08-16',
            'proyecto': self.proyecto.pk,
            'horas': '3.5',
            'descripcion': 'New work',
            'tipo_tarea': 'reunion'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verificar que se creó
        nuevo_registro = RegistroHora.objects.filter(
            fecha=date(2025, 8, 16),
            horas=Decimal('3.5')
        ).first()
        self.assertIsNotNone(nuevo_registro)
        self.assertEqual(nuevo_registro.tipo_tarea, 'reunion')
    
    def test_hora_detail_view(self):
        """Prueba la vista de detalle de horas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('horas:hora_detail', kwargs={'pk': self.registro.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test work')
    
    def test_hora_update_view(self):
        """Prueba la actualización de horas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('horas:hora_update', kwargs={'pk': self.registro.pk}),
            {
                'fecha': '2025-08-15',
                'proyecto': self.proyecto.pk,
                'horas': '5.0',
                'descripcion': 'Updated work',
                'tipo_tarea': 'reunion'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verificar actualización
        self.registro.refresh_from_db()
        self.assertEqual(self.registro.horas, Decimal('5.0'))
        self.assertEqual(self.registro.descripcion, 'Updated work')
        self.assertEqual(self.registro.tipo_tarea, 'reunion')
    
    def test_hora_delete_view(self):
        """Prueba la eliminación de horas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('horas:hora_delete', kwargs={'pk': self.registro.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verificar eliminación
        self.assertFalse(
            RegistroHora.objects.filter(pk=self.registro.pk).exists()
        )


class HoraAPIViewsTest(TestCase):
    """Pruebas para las APIs de horas"""
    
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
        self.proyecto = Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
        self.registro = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto,
            horas=Decimal('4.0'),
            tipo_tarea='tarea',
            periodo=self.periodo,
            usuario=self.user
        )
    
    def test_hora_api_view(self):
        """Prueba la API de horas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/horas/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['proyecto'], 'Test Project')
        self.assertEqual(data[0]['horas'], 4.0)
    
    def test_hora_por_fecha_api_view(self):
        """Prueba la API de horas por fecha"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/horas/api/fecha/2025-08-15/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['proyecto'], 'Test Project')
    
    def test_hora_detail_api_view(self):
        """Prueba la API de detalle de horas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/horas/api/{self.registro.pk}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['proyecto'], 'Test Project')
        self.assertEqual(data['horas'], 4.0)
        self.assertEqual(data['tipo_tarea'], 'tarea')


class HoraPermissionsTest(TestCase):
    """Pruebas de permisos para horas"""
    
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
        
        # Crear datos para user1
        self.periodo1 = Periodo.objects.create(
            nombre='User1 Periodo',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 8, 31),
            horas_objetivo=160,
            activo=True,
            usuario=self.user1
        )
        self.proyecto1 = Proyecto.objects.create(
            nombre='User1 Project',
            usuario=self.user1
        )
        self.registro1 = RegistroHora.objects.create(
            fecha=date(2025, 8, 15),
            proyecto=self.proyecto1,
            horas=Decimal('4.0'),
            periodo=self.periodo1,
            usuario=self.user1
        )
    
    def test_user_can_only_see_own_hours(self):
        """Prueba que los usuarios solo ven sus propias horas"""
        # Login como user2
        self.client.login(username='user2', password='testpass123')
        
        # Intentar acceder al registro de user1
        response = self.client.get(
            reverse('horas:hora_detail', kwargs={'pk': self.registro1.pk})
        )
        self.assertEqual(response.status_code, 404)  # No encontrado
    
    def test_user_cannot_modify_other_user_hours(self):
        """Prueba que los usuarios no pueden modificar horas de otros"""
        # Login como user2
        self.client.login(username='user2', password='testpass123')
        
        # Intentar actualizar registro de user1
        response = self.client.post(
            reverse('horas:hora_update', kwargs={'pk': self.registro1.pk}),
            {
                'fecha': '2025-08-15',
                'proyecto': self.proyecto1.pk,
                'horas': '8.0',
                'tipo_tarea': 'tarea'
            }
        )
        self.assertEqual(response.status_code, 404)  # No encontrado
        
        # Verificar que no se modificó
        self.registro1.refresh_from_db()
        self.assertEqual(self.registro1.horas, Decimal('4.0'))
    
    def test_api_returns_only_user_hours(self):
        """Prueba que las APIs solo retornan horas del usuario"""
        # Login como user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/horas/')
        
        data = response.json()
        self.assertEqual(len(data), 1)  # Solo su registro
        self.assertEqual(data[0]['proyecto'], 'User1 Project')
