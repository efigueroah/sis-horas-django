"""
URL configuration for sis_horas project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importar vistas directamente para APIs
from apps.core import views as core_views
from apps.proyectos import views as proyecto_views
from apps.horas import views as hora_views
from apps.reportes import views as reporte_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    
    # Autenticación
    path('auth/', include('apps.authentication.urls')),
    
    # Dashboard principal (página de inicio)
    path('', include('apps.core.urls')),
    
    # Vistas web principales
    path('horas/', include('apps.horas.urls')),
    path('proyectos/', include('apps.proyectos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    
    # APIs específicas - rutas directas
    path('api/dashboard/', core_views.DashboardAPIView.as_view(), name='api_dashboard'),
    path('api/calendario/<int:year>/<int:month>/', core_views.CalendarioAPIView.as_view(), name='api_calendario'),
    path('api/periodos/', core_views.PeriodoAPIView.as_view(), name='api_periodos'),
    path('api/periodos/activo/', core_views.PeriodoActivoAPIView.as_view(), name='api_periodo_activo'),
    path('api/feriados/', core_views.FeriadoAPIView.as_view(), name='api_feriados'),
    
    # APIs de proyectos
    path('api/proyectos/', proyecto_views.ProyectoAPIView.as_view(), name='api_proyectos'),
    path('api/proyectos/activos/', proyecto_views.ProyectoActivosAPIView.as_view(), name='api_proyectos_activos'),
    
    # APIs de horas
    path('api/horas/', hora_views.HoraAPIView.as_view(), name='api_horas'),
    
    # APIs de reportes
    path('api/reportes/api/exportar/csv/', reporte_views.ExportarCSVAPIView.as_view(), name='api_reportes_exportar_csv'),
    path('api/reportes/api/historial/', reporte_views.HistorialExportacionAPIView.as_view(), name='api_reportes_historial'),
    
    # API de autenticación
    path('api/auth/', include('rest_framework.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Configurar títulos del admin
admin.site.site_header = "Sistema de Gestión de Horas"
admin.site.site_title = "SisHoras Admin"
admin.site.index_title = "Panel de Administración"
