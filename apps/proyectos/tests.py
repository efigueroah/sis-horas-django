from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, datetime
from .models import Proyecto


class ProyectoModelTest(TestCase):
    """Pruebas para el modelo Proyecto"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_proyecto_creation(self):
        """Prueba la creación de un proyecto"""
        proyecto = Proyecto.objects.create(
            nombre='Test Project',
            descripcion='Test description',
            cliente='Test Client',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 12, 31),
            usuario=self.user
        )
        self.assertEqual(proyecto.nombre, 'Test Project')
        self.assertEqual(proyecto.cliente, 'Test Client')
        self.assertEqual(proyecto.año, 2025)
        self.assertTrue(proyecto.activo)  # Por defecto activo
    
    def test_proyecto_auto_year_calculation(self):
        """Prueba el cálculo automático del año"""
        proyecto = Proyecto.objects.create(
            nombre='Test Project',
            fecha_inicio=date(2024, 6, 1),
            usuario=self.user
        )
        self.assertEqual(proyecto.año, 2024)
    
    def test_proyecto_without_dates(self):
        """Prueba proyecto sin fechas definidas"""
        proyecto = Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
        self.assertEqual(proyecto.año, datetime.now().year)
    
    def test_proyecto_str_method(self):
        """Prueba el método __str__ del proyecto"""
        # Sin cliente
        proyecto1 = Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
        self.assertEqual(str(proyecto1), 'Test Project')
        
        # Con cliente
        proyecto2 = Proyecto.objects.create(
            nombre='Test Project 2',
            cliente='Test Client',
            usuario=self.user
        )
        self.assertEqual(str(proyecto2), 'Test Project 2 (Test Client)')
    
    def test_proyecto_get_absolute_url(self):
        """Prueba el método get_absolute_url"""
        proyecto = Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
        expected_url = reverse('proyectos:proyecto_detail', kwargs={'pk': proyecto.pk})
        self.assertEqual(proyecto.get_absolute_url(), expected_url)
    
    def test_proyecto_unique_name_per_user(self):
        """Prueba que no puede haber nombres duplicados por usuario"""
        Proyecto.objects.create(
            nombre='Test Project',
            usuario=self.user
        )
        
        # Intentar crear otro proyecto con el mismo nombre
        with self.assertRaises(Exception):
            Proyecto.objects.create(
                nombre='Test Project',
                usuario=self.user
            )
    
    def test_proyecto_color_hex_validation(self):
        """Prueba la validación del color hexadecimal"""
        proyecto = Proyecto(
            nombre='Test Project',
            color_hex='invalid_color',
            usuario=self.user
        )
        
        with self.assertRaises(ValidationError):
            proyecto.full_clean()
        
        # Color válido
        proyecto.color_hex = '#FF5733'
        proyecto.full_clean()  # No debe lanzar excepción
    
    def test_proyecto_properties(self):
        """Prueba las propiedades del proyecto"""
        proyecto = Proyecto.objects.create(
            nombre='Test Project',
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 12, 31),
            usuario=self.user
        )
        
        # Propiedad display_name
        self.assertEqual(proyecto.display_name, 'Test Project')
        
        # Propiedad estado_texto
        self.assertEqual(proyecto.estado_texto, 'Activo')
        proyecto.activo = False
        self.assertEqual(proyecto.estado_texto, 'Inactivo')
        
        # Propiedad duracion_dias
        self.assertEqual(proyecto.duracion_dias, 153)  # Días entre fechas
        
        # Propiedad es_vigente
        self.assertTrue(proyecto.es_vigente)
    
    def test_proyecto_es_vigente_logic(self):
        """Prueba la lógica de vigencia del proyecto"""
        # Proyecto sin fechas - siempre vigente
        proyecto1 = Proyecto.objects.create(
            nombre='Project 1',
            usuario=self.user
        )
        self.assertTrue(proyecto1.es_vigente)
        
        # Proyecto en el pasado - no vigente
        proyecto2 = Proyecto.objects.create(
            nombre='Project 2',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 1, 31),
            usuario=self.user
        )
        self.assertFalse(proyecto2.es_vigente)
        
        # Proyecto en el futuro - no vigente
        proyecto3 = Proyecto.objects.create(
            nombre='Project 3',
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 1, 31),
            usuario=self.user
        )
        self.assertFalse(proyecto3.es_vigente)


class ProyectoViewsTest(TestCase):
    """Pruebas para las vistas de proyectos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.proyecto = Proyecto.objects.create(
            nombre='Test Project',
            descripcion='Test description',
            cliente='Test Client',
            usuario=self.user
        )
    
    def test_proyecto_list_view_requires_login(self):
        """Prueba que la lista de proyectos requiere autenticación"""
        response = self.client.get(reverse('proyectos:proyecto_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_proyecto_list_view_authenticated(self):
        """Prueba la vista de lista de proyectos con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('proyectos:proyecto_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Test Client')
    
    def test_proyecto_create_view_get(self):
        """Prueba la vista de creación de proyecto (GET)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('proyectos:proyecto_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nuevo Proyecto')
    
    def test_proyecto_create_view_post(self):
        """Prueba la creación de proyecto (POST)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('proyectos:proyecto_create'), {
            'nombre': 'New Project',
            'descripcion': 'New description',
            'cliente': 'New Client',
            'fecha_inicio': '2025-09-01',
            'fecha_fin': '2025-12-31',
            'color_hex': '#FF5733'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Proyecto.objects.filter(nombre='New Project').exists())
    
    def test_proyecto_detail_view(self):
        """Prueba la vista de detalle de proyecto"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('proyectos:proyecto_detail', kwargs={'pk': self.proyecto.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_proyecto_update_view_get(self):
        """Prueba la vista de actualización de proyecto (GET)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('proyectos:proyecto_update', kwargs={'pk': self.proyecto.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_proyecto_update_view_post(self):
        """Prueba la actualización de proyecto (POST)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('proyectos:proyecto_update', kwargs={'pk': self.proyecto.pk}),
            {
                'nombre': 'Updated Project',
                'descripcion': 'Updated description',
                'cliente': 'Updated Client',
                'color_hex': '#33FF57',
                'activo': True
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verificar que se actualizó
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.nombre, 'Updated Project')
        self.assertEqual(self.proyecto.cliente, 'Updated Client')
    
    def test_proyecto_toggle_view(self):
        """Prueba el toggle de estado del proyecto"""
        self.client.login(username='testuser', password='testpass123')
        
        # Proyecto inicialmente activo
        self.assertTrue(self.proyecto.activo)
        
        # Toggle a inactivo
        response = self.client.post(
            reverse('proyectos:proyecto_toggle', kwargs={'pk': self.proyecto.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Verificar cambio de estado
        self.proyecto.refresh_from_db()
        self.assertFalse(self.proyecto.activo)
        
        # Toggle de vuelta a activo
        response = self.client.post(
            reverse('proyectos:proyecto_toggle', kwargs={'pk': self.proyecto.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        self.proyecto.refresh_from_db()
        self.assertTrue(self.proyecto.activo)


class ProyectoAPIViewsTest(TestCase):
    """Pruebas para las APIs de proyectos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.proyecto_activo = Proyecto.objects.create(
            nombre='Active Project',
            cliente='Active Client',
            activo=True,
            usuario=self.user
        )
        self.proyecto_inactivo = Proyecto.objects.create(
            nombre='Inactive Project',
            cliente='Inactive Client',
            activo=False,
            usuario=self.user
        )
    
    def test_proyecto_api_view(self):
        """Prueba la API de proyectos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/proyectos/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 2)  # Ambos proyectos
        
        # Verificar que incluye ambos proyectos
        nombres = [p['nombre'] for p in data]
        self.assertIn('Active Project', nombres)
        self.assertIn('Inactive Project', nombres)
    
    def test_proyecto_activos_api_view(self):
        """Prueba la API de proyectos activos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/proyectos/activos/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)  # Solo el activo
        self.assertEqual(data[0]['nombre'], 'Active Project')
    
    def test_proyecto_detail_api_view(self):
        """Prueba la API de detalle de proyecto"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/proyectos/api/{self.proyecto_activo.pk}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['nombre'], 'Active Project')
        self.assertEqual(data['cliente'], 'Active Client')
        self.assertTrue(data['activo'])
    
    def test_proyecto_años_api_view(self):
        """Prueba la API de años de proyectos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/proyectos/api/años/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn(datetime.now().year, data)


class ProyectoPermissionsTest(TestCase):
    """Pruebas de permisos para proyectos"""
    
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
        self.proyecto_user1 = Proyecto.objects.create(
            nombre='User1 Project',
            usuario=self.user1
        )
    
    def test_user_can_only_see_own_projects(self):
        """Prueba que los usuarios solo ven sus propios proyectos"""
        # Login como user2
        self.client.login(username='user2', password='testpass123')
        
        # Intentar acceder al proyecto de user1
        response = self.client.get(
            reverse('proyectos:proyecto_detail', kwargs={'pk': self.proyecto_user1.pk})
        )
        self.assertEqual(response.status_code, 404)  # No encontrado
    
    def test_user_cannot_modify_other_user_projects(self):
        """Prueba que los usuarios no pueden modificar proyectos de otros"""
        # Login como user2
        self.client.login(username='user2', password='testpass123')
        
        # Intentar actualizar proyecto de user1
        response = self.client.post(
            reverse('proyectos:proyecto_update', kwargs={'pk': self.proyecto_user1.pk}),
            {
                'nombre': 'Hacked Project',
                'activo': True
            }
        )
        self.assertEqual(response.status_code, 404)  # No encontrado
        
        # Verificar que no se modificó
        self.proyecto_user1.refresh_from_db()
        self.assertEqual(self.proyecto_user1.nombre, 'User1 Project')
    
    def test_api_returns_only_user_projects(self):
        """Prueba que las APIs solo retornan proyectos del usuario"""
        # Crear proyecto para user2
        Proyecto.objects.create(
            nombre='User2 Project',
            usuario=self.user2
        )
        
        # Login como user1
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/proyectos/')
        
        data = response.json()
        self.assertEqual(len(data), 1)  # Solo su proyecto
        self.assertEqual(data[0]['nombre'], 'User1 Project')
