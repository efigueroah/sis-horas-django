from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Proyecto
from .forms import ProyectoForm, ProyectoFiltroForm, ProyectoRapidoForm


class ProyectoListView(LoginRequiredMixin, ListView):
    """Lista de proyectos con filtros y separación por estado"""
    model = Proyecto
    template_name = 'proyectos/proyecto_list.html'
    context_object_name = 'proyectos'
    
    def get_queryset(self):
        queryset = Proyecto.objects.filter(usuario=self.request.user).order_by('-activo', 'nombre')
        
        # Filtros
        nombre = self.request.GET.get('nombre', '').strip()
        cliente = self.request.GET.get('cliente', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        if cliente:
            queryset = queryset.filter(cliente__icontains=cliente)
        
        if estado == 'activo':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Separar proyectos por estado
        all_projects = list(context['proyectos'])
        context['proyectos_activos'] = [p for p in all_projects if p.activo]
        context['proyectos_inactivos'] = [p for p in all_projects if not p.activo]
        
        # Información de filtros
        context['filtros_aplicados'] = bool(
            self.request.GET.get('nombre') or 
            self.request.GET.get('cliente') or 
            self.request.GET.get('estado')
        )
        
        return context


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    """Crear proyecto"""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'
    success_url = reverse_lazy('proyectos:proyecto_list')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Proyecto creado exitosamente')
        return super().form_valid(form)


class ProyectoDetailView(LoginRequiredMixin, DetailView):
    """Detalle de proyecto"""
    model = Proyecto
    template_name = 'proyectos/proyecto_detail.html'
    
    def get_queryset(self):
        return Proyecto.objects.filter(usuario=self.request.user)


class ProyectoUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar proyecto"""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'
    success_url = reverse_lazy('proyectos:proyecto_list')
    
    def get_queryset(self):
        return Proyecto.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Proyecto actualizado exitosamente')
        return super().form_valid(form)


class ProyectoToggleView(LoginRequiredMixin, View):
    """Activar/desactivar proyecto"""
    def post(self, request, pk):
        try:
            proyecto = get_object_or_404(Proyecto, pk=pk, usuario=request.user)
            proyecto.activo = not proyecto.activo
            proyecto.save()
            
            estado = "activado" if proyecto.activo else "desactivado"
            messages.success(request, f'Proyecto "{proyecto.nombre}" {estado} exitosamente')
            
            return JsonResponse({'success': True, 'activo': proyecto.activo})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class ProyectoDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar proyecto"""
    model = Proyecto
    template_name = 'proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyectos:proyecto_list')
    
    def get_queryset(self):
        return Proyecto.objects.filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        proyecto = self.get_object()
        nombre = proyecto.nombre
        messages.success(request, f'Proyecto "{nombre}" eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


# API Views
class ProyectoAPIView(APIView):
    """API de proyectos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        proyectos = Proyecto.objects.filter(usuario=request.user).order_by('-created_at')
        data = [{
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'cliente': p.cliente,
            'activo': p.activo,
            'año': p.año,
            'color_hex': p.color_hex,
            'fecha_inicio': p.fecha_inicio.strftime('%Y-%m-%d') if p.fecha_inicio else None,
            'fecha_fin': p.fecha_fin.strftime('%Y-%m-%d') if p.fecha_fin else None,
        } for p in proyectos]
        return Response(data)


class ProyectoDetailAPIView(APIView):
    """API detalle de proyecto"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            proyecto = get_object_or_404(Proyecto, pk=pk, usuario=request.user)
            data = {
                'id': proyecto.id,
                'nombre': proyecto.nombre,
                'descripcion': proyecto.descripcion,
                'cliente': proyecto.cliente,
                'activo': proyecto.activo,
                'año': proyecto.año,
                'color_hex': proyecto.color_hex,
                'fecha_inicio': proyecto.fecha_inicio.strftime('%Y-%m-%d') if proyecto.fecha_inicio else None,
                'fecha_fin': proyecto.fecha_fin.strftime('%Y-%m-%d') if proyecto.fecha_fin else None,
            }
            return Response(data)
        except Proyecto.DoesNotExist:
            return Response({'error': 'Proyecto no encontrado'}, status=404)


class ProyectoAñosAPIView(APIView):
    """API de años de proyectos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        años = Proyecto.objects.filter(
            usuario=request.user
        ).values_list('año', flat=True).distinct().order_by('-año')
        return Response(list(años))


class ProyectoActivosAPIView(APIView):
    """API de proyectos activos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        proyectos = Proyecto.objects.filter(usuario=request.user, activo=True).order_by('nombre')
        data = [{
            'id': p.id,
            'nombre': p.nombre,
            'cliente': p.cliente,
            'color_hex': p.color_hex
        } for p in proyectos]
        return Response(data)


class ProyectoFavoritosAPIView(APIView):
    """API para obtener proyectos favoritos y todos los proyectos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count
        from apps.horas.models import RegistroHora
        from datetime import date, timedelta
        
        # Obtener todos los proyectos activos
        proyectos = Proyecto.objects.filter(
            usuario=request.user,
            activo=True
        ).order_by('nombre')
        
        # Calcular favoritos basado en uso frecuente (últimos 30 días)
        fecha_limite = date.today() - timedelta(days=30)
        
        favoritos_ids = RegistroHora.objects.filter(
            usuario=request.user,
            fecha__gte=fecha_limite
        ).values('proyecto').annotate(
            uso_count=Count('id')
        ).order_by('-uso_count')[:5].values_list('proyecto', flat=True)
        
        # Serializar datos
        todos_data = []
        favoritos_data = []
        
        for proyecto in proyectos:
            proyecto_data = {
                'id': proyecto.id,
                'nombre': proyecto.nombre,
                'cliente': proyecto.cliente,
                'color': proyecto.color_hex
            }
            todos_data.append(proyecto_data)
            
            if proyecto.id in favoritos_ids:
                favoritos_data.append(proyecto_data)
        
        # Ordenar favoritos por frecuencia de uso
        favoritos_data.sort(key=lambda x: list(favoritos_ids).index(x['id']))
        
        return Response({
            'favoritos': favoritos_data,
            'todos': todos_data
        })
