from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import RegistroHora


@admin.register(RegistroHora)
class RegistroHoraAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'proyecto_info', 'horas_badge', 'tipo_tarea_badge', 'usuario', 'periodo_info')
    list_filter = ('tipo_tarea', 'fecha', 'usuario', 'proyecto', 'periodo', 'created_at')
    search_fields = ('descripcion', 'proyecto__nombre', 'proyecto__cliente', 'usuario__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('fecha', 'usuario', 'periodo')
        }),
        ('Detalles del Trabajo', {
            'fields': ('proyecto', 'horas', 'tipo_tarea', 'descripcion')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def proyecto_info(self, obj):
        if obj.proyecto.cliente:
            return format_html(
                '<strong>{}</strong><br><small style="color: #6c757d;">{}</small>',
                obj.proyecto.nombre,
                obj.proyecto.cliente
            )
        return obj.proyecto.nombre
    proyecto_info.short_description = 'Proyecto'
    
    def horas_badge(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}h</span>',
            obj.horas
        )
    horas_badge.short_description = 'Horas'
    
    def tipo_tarea_badge(self, obj):
        colors = {
            'tarea': '#007bff',
            'reunion': '#ffc107'
        }
        icons = {
            'tarea': '📋',
            'reunion': '👥'
        }
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(obj.tipo_tarea, '#6c757d'),
            icons.get(obj.tipo_tarea, ''),
            obj.get_tipo_tarea_display()
        )
    tipo_tarea_badge.short_description = 'Tipo'
    
    def periodo_info(self, obj):
        if obj.periodo:
            activo = "🟢" if obj.periodo.activo else "⚪"
            return format_html('{} {}', activo, obj.periodo.nombre)
        return "Sin período"
    periodo_info.short_description = 'Período'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'proyecto', 'periodo')
    
    actions = ['cambiar_tipo_tarea', 'duplicar_registros', 'exportar_csv']
    
    def cambiar_tipo_tarea(self, request, queryset):
        # Cambiar entre tarea y reunión
        for registro in queryset:
            registro.tipo_tarea = 'reunion' if registro.tipo_tarea == 'tarea' else 'tarea'
            registro.save()
        self.message_user(request, f'Tipo de tarea cambiado para {queryset.count()} registro(s)')
    cambiar_tipo_tarea.short_description = 'Cambiar tipo de tarea'
    
    def duplicar_registros(self, request, queryset):
        duplicados = 0
        for registro in queryset:
            RegistroHora.objects.create(
                fecha=registro.fecha,
                proyecto=registro.proyecto,
                horas=registro.horas,
                descripcion=f"[COPIA] {registro.descripcion}",
                tipo_tarea=registro.tipo_tarea,
                periodo=registro.periodo,
                usuario=registro.usuario
            )
            duplicados += 1
        self.message_user(request, f'{duplicados} registro(s) duplicado(s)')
    duplicar_registros.short_description = 'Duplicar registros seleccionados'
    
    def exportar_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registros_horas.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Proyecto', 'Cliente', 'Horas', 'Tipo', 'Descripción', 'Usuario'])
        
        for registro in queryset:
            writer.writerow([
                registro.fecha,
                registro.proyecto.nombre,
                registro.proyecto.cliente or '',
                registro.horas,
                registro.get_tipo_tarea_display(),
                registro.descripcion,
                registro.usuario.username
            ])
        
        return response
    exportar_csv.short_description = 'Exportar a CSV'
    
    # Agregar información de resumen en el changelist
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
            total_horas = qs.aggregate(Sum('horas'))['horas__sum'] or 0
            total_registros = qs.count()
            
            response.context_data['summary'] = {
                'total_horas': total_horas,
                'total_registros': total_registros,
            }
        except (AttributeError, KeyError):
            pass
        
        return response
