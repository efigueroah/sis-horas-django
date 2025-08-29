from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from decimal import Decimal
from datetime import datetime
from apps.core.models import Periodo
from apps.proyectos.models import Proyecto


class RegistroHora(models.Model):
    """Registro de horas trabajadas"""
    
    TIPO_TAREA_CHOICES = [
        ('tarea', 'Tarea'),
        ('reunion', 'Reunión'),
    ]
    
    fecha = models.DateField()
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        related_name='registros_horas'
    )
    horas = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.5')),
            MaxValueValidator(Decimal('12.0'))
        ],
        help_text="Horas trabajadas (mínimo 0.5h, máximo 12h, incrementos de 0.5h)"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción detallada de las actividades realizadas"
    )
    tipo_tarea = models.CharField(
        max_length=10,
        choices=TIPO_TAREA_CHOICES,
        default='tarea'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='registros_horas'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registros_horas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de Hora"
        verbose_name_plural = "Registros de Horas"
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['fecha', 'usuario']),
            models.Index(fields=['proyecto', 'fecha']),
            models.Index(fields=['periodo', 'fecha']),
        ]

    def __str__(self):
        return f"{self.fecha} - {self.proyecto.nombre} - {self.horas}h ({self.get_tipo_tarea_display()})"

    def get_absolute_url(self):
        """Retorna la URL de detalle del registro de hora"""
        return reverse('horas:hora_detail', kwargs={'pk': self.pk})

    def clean(self):
        """Validaciones personalizadas"""
        if self.horas:
            # Validar que las horas sean múltiplos de 0.5
            if float(self.horas) % 0.5 != 0:
                raise ValidationError("Las horas deben ser múltiplos de 0.5 (30 minutos)")
        
        if self.fecha:
            # Validar que no sea fin de semana
            if self.fecha.weekday() >= 5:  # 5=sábado, 6=domingo
                raise ValidationError("No se pueden registrar horas en fines de semana")
            
            # Solo validar si el usuario está asignado
            if hasattr(self, 'usuario') and self.usuario:
                # Validar que no sea día feriado
                from apps.core.models import DiaFeriado
                if DiaFeriado.objects.filter(fecha=self.fecha, usuario=self.usuario).exists():
                    raise ValidationError("No se pueden registrar horas en días feriados")
                
                # Validar horas máximas por día
                if self.horas:
                    total_horas_dia = RegistroHora.objects.filter(
                        fecha=self.fecha,
                        usuario=self.usuario
                    ).exclude(pk=self.pk).aggregate(
                        total=models.Sum('horas')
                    )['total'] or Decimal('0')
                    
                    horas_max = Decimal('8')  # Default como Decimal
                    if hasattr(self.usuario, 'profile') and self.usuario.profile:
                        horas_max = Decimal(str(self.usuario.profile.horas_max_dia))
                    if self.periodo:
                        horas_max = Decimal(str(self.periodo.horas_max_dia))
                    
                    if total_horas_dia + self.horas > horas_max:
                        raise ValidationError(
                            f"Excede el máximo de {horas_max} horas por día. "
                            f"Ya tienes {total_horas_dia}h registradas."
                        )

        # Validar que el proyecto pertenezca al mismo usuario (solo si ambos están asignados)
        if hasattr(self, 'proyecto') and self.proyecto and hasattr(self, 'usuario') and self.usuario:
            if self.proyecto.usuario != self.usuario:
                raise ValidationError("El proyecto debe pertenecer al mismo usuario")
        
        # Validar que el período pertenezca al mismo usuario (solo si ambos están asignados)
        if hasattr(self, 'periodo') and self.periodo and hasattr(self, 'usuario') and self.usuario:
            if self.periodo.usuario != self.usuario:
                raise ValidationError("El período debe pertenecer al mismo usuario")

    def save(self, *args, **kwargs):
        # Si no se especifica período, usar el activo
        if not self.periodo_id and self.usuario:
            periodo_activo = Periodo.objects.filter(
                usuario=self.usuario,
                activo=True
            ).first()
            if periodo_activo:
                self.periodo = periodo_activo
        
        super().save(*args, **kwargs)

    @property
    def horas_float(self):
        """Retorna las horas como float para cálculos"""
        return float(self.horas)

    @property
    def tipo_tarea_icon(self):
        """Retorna el ícono para el tipo de tarea"""
        icons = {
            'tarea': 'fas fa-tasks',
            'reunion': 'fas fa-users'
        }
        return icons.get(self.tipo_tarea, 'fas fa-clock')

    @property
    def tipo_tarea_color(self):
        """Retorna el color para el tipo de tarea"""
        colors = {
            'tarea': 'primary',
            'reunion': 'warning'
        }
        return colors.get(self.tipo_tarea, 'secondary')

    @classmethod
    def get_resumen_por_proyecto(cls, usuario, fecha_inicio=None, fecha_fin=None, periodo=None):
        """Obtiene resumen de horas agrupadas por proyecto"""
        queryset = cls.objects.filter(usuario=usuario)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        if periodo:
            queryset = queryset.filter(periodo=periodo)
        
        return queryset.values(
            'proyecto__nombre',
            'proyecto__cliente',
            'proyecto__color_hex'
        ).annotate(
            total_horas=models.Sum('horas'),
            total_registros=models.Count('id')
        ).order_by('-total_horas')

    @classmethod
    def get_resumen_por_tipo_tarea(cls, usuario, fecha_inicio=None, fecha_fin=None, periodo=None):
        """Obtiene resumen de horas agrupadas por tipo de tarea"""
        queryset = cls.objects.filter(usuario=usuario)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        if periodo:
            queryset = queryset.filter(periodo=periodo)
        
        return queryset.values('tipo_tarea').annotate(
            total_horas=models.Sum('horas'),
            total_registros=models.Count('id')
        ).order_by('tipo_tarea')

    @classmethod
    def get_horas_por_fecha(cls, usuario, fecha):
        """Obtiene todas las horas de una fecha específica"""
        return cls.objects.filter(
            usuario=usuario,
            fecha=fecha
        ).select_related('proyecto', 'periodo')

    @classmethod
    def get_total_horas_dia(cls, usuario, fecha):
        """Obtiene el total de horas registradas en un día"""
        return cls.objects.filter(
            usuario=usuario,
            fecha=fecha
        ).aggregate(total=models.Sum('horas'))['total'] or Decimal('0')
