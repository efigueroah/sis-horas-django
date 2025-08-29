from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.urls import reverse
from datetime import datetime


class Proyecto(models.Model):
    """Proyectos para la gestión de horas"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, help_text="Descripción detallada del proyecto")
    cliente = models.CharField(max_length=200, blank=True, help_text="Nombre del cliente")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    año = models.IntegerField(editable=False, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos')
    color_hex = models.CharField(
        max_length=7,
        default='#007bff',
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='El color debe estar en formato hexadecimal (#RRGGBB)'
            )
        ],
        help_text="Color para visualización en gráficos"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'usuario'],
                name='unique_project_name_per_user'
            )
        ]

    def __str__(self):
        if self.cliente:
            return f"{self.nombre} ({self.cliente})"
        return self.nombre

    def get_absolute_url(self):
        """URL absoluta del proyecto"""
        return reverse('proyectos:proyecto_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Auto-calcular el año basado en fecha_inicio
        if self.fecha_inicio:
            self.año = self.fecha_inicio.year
        elif not self.año:
            self.año = datetime.now().year
        
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Nombre para mostrar en la interfaz"""
        return str(self)

    @property
    def estado_texto(self):
        """Estado del proyecto en texto"""
        return "Activo" if self.activo else "Inactivo"

    @property
    def duracion_dias(self):
        """Duración del proyecto en días"""
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return None

    @property
    def es_vigente(self):
        """Verifica si el proyecto está vigente según las fechas"""
        if not self.fecha_inicio and not self.fecha_fin:
            return True  # Sin fechas definidas, siempre vigente
        
        hoy = datetime.now().date()
        
        if self.fecha_inicio and hoy < self.fecha_inicio:
            return False  # Aún no ha comenzado
        
        if self.fecha_fin and hoy > self.fecha_fin:
            return False  # Ya terminó
        
        return True

    @property
    def total_horas_registradas(self):
        """Total de horas registradas en este proyecto"""
        return self.registros_horas.aggregate(
            total=models.Sum('horas')
        )['total'] or 0

    def get_horas_por_tipo(self):
        """Retorna las horas agrupadas por tipo de tarea"""
        from apps.horas.models import RegistroHora
        return self.registros_horas.values('tipo_tarea').annotate(
            total_horas=models.Sum('horas'),
            total_registros=models.Count('id')
        ).order_by('tipo_tarea')

    def get_horas_por_mes(self, año=None):
        """Retorna las horas agrupadas por mes"""
        queryset = self.registros_horas.all()
        if año:
            queryset = queryset.filter(fecha__year=año)
        
        return queryset.extra(
            select={'mes': 'strftime("%%m", fecha)'}
        ).values('mes').annotate(
            total_horas=models.Sum('horas')
        ).order_by('mes')
