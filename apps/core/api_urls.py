from django.urls import path
from . import views

app_name = 'core_api'

urlpatterns = [
    # API endpoints específicos
    path('', views.DashboardAPIView.as_view(), name='dashboard'),
    path('<int:year>/<int:month>/', views.CalendarioAPIView.as_view(), name='calendario'),
    path('', views.PeriodoAPIView.as_view(), name='periodos'),
    path('activo/', views.PeriodoActivoAPIView.as_view(), name='periodo_activo'),
    path('', views.FeriadoAPIView.as_view(), name='feriados'),
]
