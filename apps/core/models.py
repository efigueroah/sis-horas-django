from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime


class ConfiguracionSistema(models.Model):
    """Configuración global del sistema"""
    
    # Configuración de horas por defecto
    incremento_horas_default = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        choices=[
            (0.25, '15 minutos (0.25h)'),
            (0.5, '30 minutos (0.5h)'),
            (1.0, '1 hora (1.0h)'),
        ],
        help_text="Incremento por defecto para nuevos usuarios"
    )
    horas_minimas_default = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        help_text="Mínimo de horas por defecto para nuevos usuarios"
    )
    horas_maximas_default = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=12.0,
        help_text="Máximo de horas por defecto para nuevos usuarios"
    )
    horas_max_dia_default = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=8.0,
        help_text="Máximo de horas por día por defecto"
    )
    
    # Configuración de formato
    formato_fecha_default = models.CharField(
        max_length=20,
        choices=[
            ('%d/%m/%Y', 'DD/MM/YYYY'),
            ('%m/%d/%Y', 'MM/DD/YYYY'),
            ('%Y-%m-%d', 'YYYY-MM-DD'),
        ],
        default='%d/%m/%Y',
        help_text="Formato de fecha por defecto para nuevos usuarios"
    )
    
    # Configuración de validaciones
    permitir_fines_semana = models.BooleanField(
        default=False,
        help_text="Permitir registro de horas en fines de semana"
    )
    validar_feriados = models.BooleanField(
        default=True,
        help_text="Validar automáticamente días feriados"
    )
    
    # Configuración de períodos
    duracion_periodo_default = models.IntegerField(
        default=30,
        help_text="Duración por defecto de períodos en días"
    )
    
    # Metadatos
    nombre_sistema = models.CharField(
        max_length=100,
        default="Sistema de Gestión de Horas",
        help_text="Nombre del sistema"
    )
    version = models.CharField(
        max_length=20,
        default="1.0.0",
        help_text="Versión del sistema"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"

    def __str__(self):
        return f"Configuración del Sistema - {self.nombre_sistema}"

    def save(self, *args, **kwargs):
        # Asegurar que solo haya una instancia
        if not self.pk and ConfiguracionSistema.objects.exists():
            raise ValidationError("Solo puede existir una configuración del sistema")
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Obtener la configuración del sistema (singleton)"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Periodo(models.Model):
    """Períodos de trabajo con objetivos de horas"""
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas_objetivo = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número total de horas objetivo para el período"
    )
    horas_max_dia = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=8.00,
        validators=[MinValueValidator(0.5)],
        help_text="Máximo de horas que se pueden registrar por día (ej: 7.5, 8.0)"
    )
    activo = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='periodos')
    año = models.IntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Período"
        verbose_name_plural = "Períodos"
        ordering = ['-fecha_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'activo'],
                condition=models.Q(activo=True),
                name='unique_active_period_per_user'
            )
        ]

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"

    def clean(self):
        """Validaciones personalizadas"""
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        # Validar que solo haya un período activo por usuario
        if self.activo:
            existing_active = Periodo.objects.filter(
                usuario=self.usuario, 
                activo=True
            ).exclude(pk=self.pk)
            if existing_active.exists():
                raise ValidationError("Solo puede haber un período activo por usuario")

    def save(self, *args, **kwargs):
        # Auto-calcular el año
        if self.fecha_inicio:
            self.año = self.fecha_inicio.year
        
        # Si se activa este período, desactivar otros
        if self.activo:
            Periodo.objects.filter(
                usuario=self.usuario, 
                activo=True
            ).exclude(pk=self.pk).update(activo=False)
        
        super().save(*args, **kwargs)

    @property
    def duracion_dias(self):
        """Retorna la duración del período en días"""
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return 0

    @property
    def progreso_temporal(self):
        """Retorna el progreso temporal del período (0-100)"""
        if not self.fecha_inicio or not self.fecha_fin:
            return 0
        
        hoy = datetime.now().date()
        if hoy < self.fecha_inicio:
            return 0
        elif hoy > self.fecha_fin:
            return 100
        
        total_dias = (self.fecha_fin - self.fecha_inicio).days
        dias_transcurridos = (hoy - self.fecha_inicio).days
        return min(100, (dias_transcurridos / total_dias) * 100)


class DiaFeriado(models.Model):
    """Días feriados por usuario"""
    fecha = models.DateField()
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción opcional del feriado")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dias_feriados')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Día Feriado"
        verbose_name_plural = "Días Feriados"
        ordering = ['fecha']
        constraints = [
            models.UniqueConstraint(
                fields=['fecha', 'usuario'],
                name='unique_holiday_per_user_date'
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

    @property
    def año(self):
        return self.fecha.year

    @property
    def es_pasado(self):
        return self.fecha < datetime.now().date()

    @property
    def es_futuro(self):
        return self.fecha > datetime.now().date()
