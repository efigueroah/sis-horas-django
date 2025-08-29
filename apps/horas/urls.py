from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'horas'

urlpatterns = [
    # Vistas web
    path('', views.HoraListView.as_view(), name='hora_list'),
    path('registrar/', views.HoraCreateSimpleView.as_view(), name='hora_create'),
    path('registrar/multiple/', views.HoraCreateView.as_view(), name='hora_create_multiple'),
    
    # Redirección para compatibilidad (crear -> registrar)
    path('crear/', RedirectView.as_view(pattern_name='horas:hora_create', permanent=True)),
    
    path('<int:pk>/', views.HoraDetailView.as_view(), name='hora_detail'),
    path('<int:pk>/editar/', views.HoraUpdateView.as_view(), name='hora_update'),
    path('<int:pk>/eliminar/', views.HoraDeleteView.as_view(), name='hora_delete'),
    
    # Nuevas funcionalidades
    path('bloque/', views.RegistroHoraBloqueView.as_view(), name='hora_bloque'),
    
    # Página de prueba del calendario
    path('test-calendar/', views.TestCalendarView.as_view(), name='test_calendar'),
    
    # Página de prueba del widget de horas
    path('test-hours/', views.TestHoursWidgetView.as_view(), name='test_hours'),
    path('bloque/preview/', views.RegistroBloquePrevisualizacionView.as_view(), name='hora_bloque_preview'),
    path('dia/', views.VistaCompletaDiaView.as_view(), name='vista_completa_dia'),
    
    # API endpoints (solo cuando se accede desde /api/horas/)
    path('api/', views.HoraAPIView.as_view(), name='api_list'),
    path('api/<int:pk>/', views.HoraDetailAPIView.as_view(), name='api_detail'),
    path('api/resumen/', views.HoraResumenAPIView.as_view(), name='api_resumen'),
    path('api/fecha/<str:fecha>/', views.HoraPorFechaAPIView.as_view(), name='api_por_fecha'),
    path('api/validar/', views.ValidarHorasAPIView.as_view(), name='api_validar'),
]
