from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json


class ReporteExportacion(models.Model):
    """Registro de exportaciones realizadas"""
    
    FORMATO_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exportaciones')
    nombre_archivo = models.CharField(max_length=255)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    filtros_aplicados = models.JSONField(default=dict, blank=True)
    total_registros = models.IntegerField(default=0)
    tamaño_archivo = models.IntegerField(default=0, help_text="Tamaño en bytes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reporte de Exportación"
        verbose_name_plural = "Reportes de Exportación"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nombre_archivo} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    @property
    def tamaño_legible(self):
        """Retorna el tamaño del archivo en formato legible"""
        if self.tamaño_archivo < 1024:
            return f"{self.tamaño_archivo} B"
        elif self.tamaño_archivo < 1024 * 1024:
            return f"{self.tamaño_archivo / 1024:.1f} KB"
        else:
            return f"{self.tamaño_archivo / (1024 * 1024):.1f} MB"

    @property
    def periodo_texto(self):
        """Retorna el período en formato texto"""
        if self.fecha_inicio and self.fecha_fin:
            return f"{self.fecha_inicio.strftime('%d/%m/%Y')} - {self.fecha_fin.strftime('%d/%m/%Y')}"
        elif self.fecha_inicio:
            return f"Desde {self.fecha_inicio.strftime('%d/%m/%Y')}"
        elif self.fecha_fin:
            return f"Hasta {self.fecha_fin.strftime('%d/%m/%Y')}"
        return "Todos los registros"


class ConfiguracionReporte(models.Model):
    """Configuraciones personalizadas para reportes"""
    
    FORMATO_CHOICES = [
        ('csv', 'CSV (Comma Separated Values)'),
        ('xlsx', 'Excel (XLSX)'),
        ('pdf', 'PDF')
    ]
    
    SEPARADOR_CHOICES = [
        (',', 'Coma (,)'),
        (';', 'Punto y coma (;)'),
        ('|', 'Pipe (|)')
    ]
    
    DECIMAL_CHOICES = [
        ('.', 'Punto (.) - Formato internacional'),
        (',', 'Coma (,) - Formato europeo/español')
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='config_reportes')
    
    # Configuración de exportación
    formato_exportacion = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='csv')
    separador_csv = models.CharField(max_length=5, choices=SEPARADOR_CHOICES, default=',')
    separador_decimal = models.CharField(max_length=1, choices=DECIMAL_CHOICES, default='.')
    incluir_encabezados = models.BooleanField(default=True)
    
    # Filtros por defecto
    periodo_defecto = models.ForeignKey('core.Periodo', on_delete=models.SET_NULL, null=True, blank=True)
    proyectos_defecto = models.ManyToManyField('proyectos.Proyecto', blank=True)
    solo_activos = models.BooleanField(default=True)
    
    # Columnas a incluir (JSON field para lista de strings)
    columnas = models.JSONField(default=list, help_text="Lista de columnas a incluir: fecha, proyecto, horas, tipo_tarea, descripcion, cliente")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Reporte"
        verbose_name_plural = "Configuraciones de Reporte"

    def __str__(self):
        return f"Configuración de {self.usuario.username}"

    def get_columnas_exportacion(self):
        """Retorna la lista de columnas a incluir en la exportación"""
        if not self.columnas:
            return ['fecha', 'proyecto', 'horas']  # Columnas por defecto
        return self.columnas


# Signal para crear configuración automáticamente
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_report_config(sender, instance, created, **kwargs):
    if created:
        ConfiguracionReporte.objects.create(usuario=instance)
