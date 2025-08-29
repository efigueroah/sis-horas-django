from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Configuración del sistema (solo superusuarios)
    path('configuracion/', views.ConfiguracionSistemaView.as_view(), name='configuracion_sistema'),
    
    # Períodos
    path('periodos/', views.PeriodoListView.as_view(), name='periodo_list'),
    path('periodos/crear/', views.PeriodoCreateView.as_view(), name='periodo_create'),
    path('periodos/<int:pk>/', views.PeriodoDetailView.as_view(), name='periodo_detail'),
    path('periodos/<int:pk>/editar/', views.PeriodoUpdateView.as_view(), name='periodo_update'),
    path('periodos/<int:pk>/activar/', views.ActivarPeriodoView.as_view(), name='periodo_activate'),
    
    # Días feriados - CRUD completo
    path('feriados/', views.FeriadoListView.as_view(), name='feriado_list'),
    path('feriados/crear/', views.FeriadoCreateView.as_view(), name='feriado_create'),
    path('feriados/<int:pk>/', views.FeriadoDetailView.as_view(), name='feriado_detail'),
    path('feriados/<int:pk>/editar/', views.FeriadoUpdateView.as_view(), name='feriado_update'),
    path('feriados/<int:pk>/eliminar/', views.FeriadoDeleteView.as_view(), name='feriado_delete'),
    
    # Gestión de feriados en períodos
    path('periodos/<int:periodo_id>/feriados/', views.PeriodoFeriadosView.as_view(), name='periodo_feriados'),
    path('periodos/<int:periodo_id>/feriados/agregar/', views.AgregarFeriadoPeriodoView.as_view(), name='periodo_feriado_add'),
]
