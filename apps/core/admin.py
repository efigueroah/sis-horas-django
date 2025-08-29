from django.contrib import admin
from django.utils.html import format_html
from .models import Periodo, DiaFeriado


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_inicio', 'fecha_fin', 'horas_objetivo', 'activo_badge', 'año')
    list_filter = ('activo', 'año', 'usuario', 'created_at')
    search_fields = ('nombre', 'usuario__username')
    readonly_fields = ('año', 'created_at', 'updated_at')
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'usuario', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'año')
        }),
        ('Configuración de Horas', {
            'fields': ('horas_objetivo', 'horas_max_dia')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def activo_badge(self, obj):
        if obj.activo:
            return format_html('<span class="badge badge-success">✓ Activo</span>')
        return format_html('<span class="badge badge-secondary">Inactivo</span>')
    activo_badge.short_description = 'Estado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    actions = ['activar_periodos', 'desactivar_periodos']
    
    def activar_periodos(self, request, queryset):
        # Solo permitir un período activo por usuario
        for periodo in queryset:
            Periodo.objects.filter(usuario=periodo.usuario, activo=True).update(activo=False)
            periodo.activo = True
            periodo.save()
        self.message_user(request, f'{queryset.count()} período(s) activado(s)')
    activar_periodos.short_description = 'Activar períodos seleccionados'
    
    def desactivar_periodos(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f'{queryset.count()} período(s) desactivado(s)')
    desactivar_periodos.short_description = 'Desactivar períodos seleccionados'


@admin.register(DiaFeriado)
class DiaFeriadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'usuario', 'año_feriado', 'es_pasado_badge')
    list_filter = ('fecha', 'usuario', 'created_at')
    search_fields = ('nombre', 'usuario__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información del Feriado', {
            'fields': ('nombre', 'fecha', 'usuario')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def año_feriado(self, obj):
        return obj.año
    año_feriado.short_description = 'Año'
    
    def es_pasado_badge(self, obj):
        if obj.es_pasado:
            return format_html('<span class="badge badge-secondary">Pasado</span>')
        elif obj.es_futuro:
            return format_html('<span class="badge badge-info">Futuro</span>')
        return format_html('<span class="badge badge-warning">Hoy</span>')
    es_pasado_badge.short_description = 'Estado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    actions = ['duplicar_para_siguiente_año']
    
    def duplicar_para_siguiente_año(self, request, queryset):
        duplicados = 0
        for feriado in queryset:
            nueva_fecha = feriado.fecha.replace(year=feriado.fecha.year + 1)
            DiaFeriado.objects.get_or_create(
                fecha=nueva_fecha,
                usuario=feriado.usuario,
                defaults={'nombre': feriado.nombre}
            )
            duplicados += 1
        self.message_user(request, f'{duplicados} feriado(s) duplicado(s) para el siguiente año')
    duplicar_para_siguiente_año.short_description = 'Duplicar para el siguiente año'
