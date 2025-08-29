from django.contrib import admin
from django.utils.html import format_html
from .models import ReporteExportacion, ConfiguracionReporte


@admin.register(ReporteExportacion)
class ReporteExportacionAdmin(admin.ModelAdmin):
    list_display = ('nombre_archivo', 'usuario', 'formato_badge', 'total_registros', 'tamaño_badge', 'created_at')
    list_filter = ('formato', 'usuario', 'created_at')
    search_fields = ('nombre_archivo', 'usuario__username')
    readonly_fields = ('created_at', 'tamaño_legible_display', 'filtros_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('usuario', 'nombre_archivo', 'formato')
        }),
        ('Período y Filtros', {
            'fields': ('fecha_inicio', 'fecha_fin', 'filtros_display')
        }),
        ('Estadísticas', {
            'fields': ('total_registros', 'tamaño_archivo', 'tamaño_legible_display')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def formato_badge(self, obj):
        colors = {
            'csv': '#28a745',
            'xlsx': '#007bff',
            'json': '#ffc107'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.formato, '#6c757d'),
            obj.formato.upper()
        )
    formato_badge.short_description = 'Formato'
    
    def tamaño_badge(self, obj):
        tamaño = obj.tamaño_legible
        color = '#28a745' if obj.tamaño_archivo < 1024*1024 else '#ffc107'  # Verde si < 1MB
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            tamaño
        )
    tamaño_badge.short_description = 'Tamaño'
    
    def tamaño_legible_display(self, obj):
        return obj.tamaño_legible
    tamaño_legible_display.short_description = 'Tamaño Legible'
    
    def filtros_display(self, obj):
        if obj.filtros_aplicados:
            filtros = []
            for key, value in obj.filtros_aplicados.items():
                filtros.append(f"{key}: {value}")
            return format_html('<br>'.join(filtros))
        return "Sin filtros aplicados"
    filtros_display.short_description = 'Filtros Aplicados'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    actions = ['eliminar_reportes_antiguos']
    
    def eliminar_reportes_antiguos(self, request, queryset):
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=30)
        antiguos = queryset.filter(created_at__lt=fecha_limite)
        count = antiguos.count()
        antiguos.delete()
        self.message_user(request, f'{count} reporte(s) antiguo(s) eliminado(s)')
    eliminar_reportes_antiguos.short_description = 'Eliminar reportes de más de 30 días'


@admin.register(ConfiguracionReporte)
class ConfiguracionReporteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'formato_exportacion', 'separador_csv', 'incluir_encabezados_badge', 'columnas_incluidas')
    list_filter = ('formato_exportacion', 'separador_csv', 'incluir_encabezados', 'solo_activos')
    search_fields = ('usuario__username',)
    readonly_fields = ('created_at', 'updated_at', 'columnas_seleccionadas')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Configuración de Exportación', {
            'fields': ('formato_exportacion', 'separador_csv', 'incluir_encabezados')
        }),
        ('Filtros por Defecto', {
            'fields': ('periodo_defecto', 'proyectos_defecto', 'solo_activos')
        }),
        ('Columnas', {
            'fields': ('columnas',)
        }),
        ('Resumen', {
            'fields': ('columnas_seleccionadas',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def incluir_encabezados_badge(self, obj):
        if obj.incluir_encabezados:
            return format_html('<span style="color: green;">✓ Sí</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    incluir_encabezados_badge.short_description = 'Encabezados'
    
    def columnas_incluidas(self, obj):
        columnas = obj.get_columnas_exportacion()
        return format_html(
            '<span style="font-size: 11px;">{} columnas</span>',
            len(columnas)
        )
    columnas_incluidas.short_description = 'Columnas'
    
    def columnas_seleccionadas(self, obj):
        columnas = obj.get_columnas_exportacion()
        return ', '.join(columnas)
    columnas_seleccionadas.short_description = 'Columnas Seleccionadas'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    actions = ['resetear_configuraciones']
    
    def resetear_configuraciones(self, request, queryset):
        for config in queryset:
            config.separador_csv = ','
            config.incluir_encabezados = True
            config.formato_fecha = '%d/%m/%Y'
            config.incluir_proyecto = True
            config.incluir_cliente = True
            config.incluir_descripcion = True
            config.incluir_tipo_tarea = True
            config.incluir_periodo = False
            config.agrupar_por_proyecto = False
            config.agrupar_por_fecha = False
            config.incluir_totales = True
            config.save()
        self.message_user(request, f'{queryset.count()} configuración(es) reseteada(s)')
    resetear_configuraciones.short_description = 'Resetear a valores por defecto'
