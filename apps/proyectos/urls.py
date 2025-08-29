from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    # Vistas web
    path('', views.ProyectoListView.as_view(), name='proyecto_list'),
    path('crear/', views.ProyectoCreateView.as_view(), name='proyecto_create'),
    path('<int:pk>/', views.ProyectoDetailView.as_view(), name='proyecto_detail'),
    path('<int:pk>/editar/', views.ProyectoUpdateView.as_view(), name='proyecto_update'),
    path('<int:pk>/eliminar/', views.ProyectoDeleteView.as_view(), name='proyecto_delete'),
    path('<int:pk>/toggle/', views.ProyectoToggleView.as_view(), name='proyecto_toggle'),
    
    # API endpoints (solo cuando se accede desde /api/proyectos/)
    path('api/', views.ProyectoAPIView.as_view(), name='api_list'),
    path('api/<int:pk>/', views.ProyectoDetailAPIView.as_view(), name='api_detail'),
    path('api/años/', views.ProyectoAñosAPIView.as_view(), name='api_años'),
    path('api/activos/', views.ProyectoActivosAPIView.as_view(), name='api_activos'),
    path('api/favoritos/', views.ProyectoFavoritosAPIView.as_view(), name='api_favoritos'),
]
