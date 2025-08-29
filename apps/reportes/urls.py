from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Vistas web
    path('', views.ReporteListView.as_view(), name='reporte_list'),
    path('exportar/', views.ExportarView.as_view(), name='exportar'),
    path('configuracion/', views.ConfiguracionView.as_view(), name='configuracion'),
    
    # API endpoints (solo cuando se accede desde /api/reportes/)
    path('api/exportar/csv/', views.ExportarCSVAPIView.as_view(), name='api_exportar_csv'),
    path('api/exportar/xlsx/', views.ExportarXLSXAPIView.as_view(), name='api_exportar_xlsx'),
    path('api/historial/', views.HistorialExportacionAPIView.as_view(), name='api_historial'),
]
