from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """Perfil extendido del usuario con configuraciones personales"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nombre_completo = models.CharField(max_length=200, blank=True)
    horas_max_dia = models.IntegerField(
        default=8,
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text="Máximo de horas que se pueden registrar por día"
    )
    timezone = models.CharField(max_length=50, default='America/Argentina/Buenos_Aires')
    formato_fecha = models.CharField(
        max_length=20,
        choices=[
            ('%d/%m/%Y', 'DD/MM/YYYY'),
            ('%m/%d/%Y', 'MM/DD/YYYY'),
            ('%Y-%m-%d', 'YYYY-MM-DD'),
        ],
        default='%d/%m/%Y'
    )
    incremento_horas = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        choices=[
            (0.25, '15 minutos (0.25h)'),
            (0.5, '30 minutos (0.5h)'),
            (1.0, '1 hora (1.0h)'),
        ],
        help_text="Incremento mínimo para registro de horas"
    )
    horas_minimas = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        help_text="Mínimo de horas que se pueden registrar"
    )
    horas_maximas = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=12.0,
        help_text="Máximo de horas que se pueden registrar por entrada"
    )
    tema = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Oscuro'),
            ('auto', 'Automático'),
        ],
        default='light'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def display_name(self):
        """Retorna el nombre completo o username si no está definido"""
        return self.nombre_completo or self.user.get_full_name() or self.user.username


# Signal para crear automáticamente el perfil cuando se crea un usuario
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
