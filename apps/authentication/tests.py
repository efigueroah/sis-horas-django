from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile


class UserProfileModelTest(TestCase):
    """Pruebas para el modelo UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Prueba que se crea automáticamente un perfil al crear un usuario"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_defaults(self):
        """Prueba los valores por defecto del perfil"""
        profile = self.user.profile
        self.assertEqual(profile.horas_max_dia, 8)
        self.assertEqual(profile.timezone, 'America/Argentina/Buenos_Aires')
        self.assertEqual(profile.formato_fecha, '%d/%m/%Y')
        self.assertEqual(profile.tema, 'light')
    
    def test_display_name_property(self):
        """Prueba la propiedad display_name"""
        profile = self.user.profile
        
        # Sin nombre completo, debe retornar username
        self.assertEqual(profile.display_name, 'testuser')
        
        # Con nombre completo
        profile.nombre_completo = 'Test User'
        profile.save()
        self.assertEqual(profile.display_name, 'Test User')
    
    def test_user_profile_str(self):
        """Prueba el método __str__ del perfil"""
        profile = self.user.profile
        self.assertEqual(str(profile), 'Perfil de testuser')


class AuthenticationViewsTest(TestCase):
    """Pruebas para las vistas de autenticación"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """Prueba que la vista de login carga correctamente"""
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar Sesión')
    
    def test_login_view_post_valid(self):
        """Prueba login con credenciales válidas"""
        response = self.client.post(reverse('authentication:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_login_view_post_invalid(self):
        """Prueba login con credenciales inválidas"""
        response = self.client.post(reverse('authentication:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'error')
    
    def test_register_view_get(self):
        """Prueba que la vista de registro carga correctamente"""
        response = self.client.get(reverse('authentication:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrarse')
    
    def test_register_view_post_valid(self):
        """Prueba registro con datos válidos"""
        response = self.client.post(reverse('authentication:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_profile_view_requires_login(self):
        """Prueba que la vista de perfil requiere autenticación"""
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Prueba la vista de perfil con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')


class UserProfileValidationTest(TestCase):
    """Pruebas de validación del modelo UserProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_horas_max_dia_validation(self):
        """Prueba validación de horas máximas por día"""
        profile = self.user.profile
        
        # Valor válido
        profile.horas_max_dia = 8
        profile.full_clean()  # No debe lanzar excepción
        
        # Valor inválido (menor a 1)
        profile.horas_max_dia = 0
        with self.assertRaises(Exception):
            profile.full_clean()
        
        # Valor inválido (mayor a 24)
        profile.horas_max_dia = 25
        with self.assertRaises(Exception):
            profile.full_clean()
    
    def test_timezone_choices(self):
        """Prueba que se puede establecer timezone"""
        profile = self.user.profile
        profile.timezone = 'UTC'
        profile.save()
        self.assertEqual(profile.timezone, 'UTC')
    
    def test_formato_fecha_choices(self):
        """Prueba las opciones de formato de fecha"""
        profile = self.user.profile
        
        valid_formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d']
        for formato in valid_formats:
            profile.formato_fecha = formato
            profile.save()
            self.assertEqual(profile.formato_fecha, formato)
    
    def test_tema_choices(self):
        """Prueba las opciones de tema"""
        profile = self.user.profile
        
        valid_themes = ['light', 'dark', 'auto']
        for tema in valid_themes:
            profile.tema = tema
            profile.save()
            self.assertEqual(profile.tema, tema)
