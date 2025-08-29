from django.contrib import admin
from django.utils.html import format_html
from .models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente', 'usuario', 'activo_badge', 'año', 'total_horas_badge', 'color_preview')
    list_filter = ('activo', 'año', 'usuario', 'created_at')
    search_fields = ('nombre', 'cliente', 'descripcion', 'usuario__username')
    readonly_fields = ('año', 'created_at', 'updated_at', 'total_horas_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'cliente', 'descripcion', 'usuario')
        }),
        ('Configuración', {
            'fields': ('activo', 'color_hex')
        }),
        ('Fechas del Proyecto', {
            'fields': ('fecha_inicio', 'fecha_fin', 'año')
        }),
        ('Estadísticas', {
            'fields': ('total_horas_display',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def activo_badge(self, obj):
        if obj.activo:
            return format_html('<span style="color: green;">✓ Activo</span>')
        return format_html('<span style="color: red;">✗ Inactivo</span>')
    activo_badge.short_description = 'Estado'
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color_hex
        )
    color_preview.short_description = 'Color'
    
    def total_horas_badge(self, obj):
        total = obj.total_horas_registradas
        if total > 0:
            return format_html('<span style="font-weight: bold; color: #007bff;">{}h</span>', total)
        return format_html('<span style="color: #6c757d;">0h</span>')
    total_horas_badge.short_description = 'Horas'
    
    def total_horas_display(self, obj):
        total = obj.total_horas_registradas
        if total > 0:
            horas_por_tipo = obj.get_horas_por_tipo()
            detalle = []
            for tipo in horas_por_tipo:
                detalle.append(f"{tipo['tipo_tarea']}: {tipo['total_horas']}h")
            return f"{total}h total ({', '.join(detalle)})"
        return "Sin registros de horas"
    total_horas_display.short_description = 'Detalle de Horas'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
    
    actions = ['activar_proyectos', 'desactivar_proyectos', 'duplicar_proyectos']
    
    def activar_proyectos(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f'{queryset.count()} proyecto(s) activado(s)')
    activar_proyectos.short_description = 'Activar proyectos seleccionados'
    
    def desactivar_proyectos(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f'{queryset.count()} proyecto(s) desactivado(s)')
    desactivar_proyectos.short_description = 'Desactivar proyectos seleccionados'
    
    def duplicar_proyectos(self, request, queryset):
        duplicados = 0
        for proyecto in queryset:
            nuevo_proyecto = Proyecto.objects.create(
                nombre=f"{proyecto.nombre} (Copia)",
                descripcion=proyecto.descripcion,
                cliente=proyecto.cliente,
                color_hex=proyecto.color_hex,
                usuario=proyecto.usuario,
                activo=False
            )
            duplicados += 1
        self.message_user(request, f'{duplicados} proyecto(s) duplicado(s)')
    duplicar_proyectos.short_description = 'Duplicar proyectos seleccionados'
