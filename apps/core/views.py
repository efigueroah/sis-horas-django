from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date
import calendar
from .models import Periodo, DiaFeriado, ConfiguracionSistema
from .forms import PeriodoForm, DiaFeriadoForm, CalendarioFiltroForm, RangoFechasForm
from apps.horas.models import RegistroHora
from apps.proyectos.models import Proyecto


class ConfiguracionSistemaView(LoginRequiredMixin, TemplateView):
    """Vista para configurar parámetros del sistema y reportes"""
    template_name = 'core/configuracion_sistema.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración del sistema
        context['config_sistema'] = ConfiguracionSistema.get_config()
        
        # Configuración de reportes del usuario
        from apps.reportes.models import ConfiguracionReporte
        from apps.reportes.forms import ConfiguracionReporteForm
        
        context['form_reportes'] = ConfiguracionReporteForm(usuario=self.request.user)
        
        return context
    
    def post(self, request, *args, **kwargs):
        from apps.reportes.forms import ConfiguracionReporteForm
        from apps.reportes.models import ConfiguracionReporte
        
        # Si es configuración de reportes
        if 'save_reportes' in request.POST:
            form_reportes = ConfiguracionReporteForm(request.POST, usuario=request.user)
            if form_reportes.is_valid():
                form_reportes.save()
                messages.success(request, 'Configuración de reportes actualizada exitosamente.')
            else:
                messages.error(request, 'Error al guardar la configuración de reportes.')
        
        # Si es configuración del sistema (solo superusuarios)
        elif 'save_sistema' in request.POST and request.user.is_superuser:
            config_sistema = ConfiguracionSistema.get_config()
            # Actualizar campos del sistema
            for field in ['incremento_horas_default', 'horas_minimas_default', 'horas_maximas_default',
                         'horas_max_dia_default', 'formato_fecha_default', 'permitir_fines_semana',
                         'validar_feriados', 'duracion_periodo_default', 'nombre_sistema']:
                if field in request.POST:
                    value = request.POST[field]
                    if field in ['permitir_fines_semana', 'validar_feriados']:
                        value = value == 'on'
                    setattr(config_sistema, field, value)
            config_sistema.save()
            messages.success(request, 'Configuración del sistema actualizada exitosamente.')
        
        return redirect('core:configuracion_sistema')


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista principal del dashboard"""
    template_name = 'dashboard/dashboard_working.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener período activo
        try:
            periodo_activo = Periodo.objects.get(usuario=self.request.user, activo=True)
            context['periodo_activo'] = periodo_activo
            
            # Obtener estadísticas del período
            horas_periodo = RegistroHora.objects.filter(
                usuario=self.request.user,
                periodo=periodo_activo
            )
            
            total_horas = sum(h.horas for h in horas_periodo)
            context['total_horas'] = total_horas
            context['horas_objetivo'] = periodo_activo.horas_objetivo
            context['porcentaje_completacion'] = (total_horas / periodo_activo.horas_objetivo * 100) if periodo_activo.horas_objetivo > 0 else 0
            context['horas_faltantes'] = max(0, periodo_activo.horas_objetivo - total_horas)
            
            # Días con registros
            fechas_unicas = set(h.fecha for h in horas_periodo)
            context['dias_trabajados'] = len(fechas_unicas)
            
        except Periodo.DoesNotExist:
            context['periodo_activo'] = None
            context['total_horas'] = 0
            context['porcentaje_completacion'] = 0
            context['horas_faltantes'] = 0
            context['dias_trabajados'] = 0
        
        return context


class PeriodoListView(LoginRequiredMixin, ListView):
    """Lista de períodos"""
    model = Periodo
    template_name = 'core/periodo_list.html'
    context_object_name = 'periodos'
    
    def get_queryset(self):
        return Periodo.objects.filter(usuario=self.request.user).order_by('-fecha_inicio')


class PeriodoCreateView(LoginRequiredMixin, CreateView):
    """Crear período"""
    model = Periodo
    form_class = PeriodoForm
    template_name = 'core/periodo_form.html'
    success_url = reverse_lazy('core:periodo_list')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Período creado exitosamente')
        return super().form_valid(form)


class PeriodoDetailView(LoginRequiredMixin, DetailView):
    """Detalle de período"""
    model = Periodo
    template_name = 'core/periodo_detail.html'
    
    def get_queryset(self):
        return Periodo.objects.filter(usuario=self.request.user)


class PeriodoUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar período"""
    model = Periodo
    form_class = PeriodoForm
    template_name = 'core/periodo_form.html'
    success_url = reverse_lazy('core:periodo_list')
    
    def get_queryset(self):
        return Periodo.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Período actualizado exitosamente')
        return super().form_valid(form)


class ActivarPeriodoView(LoginRequiredMixin, View):
    """Activar período"""
    def post(self, request, pk):
        try:
            periodo = get_object_or_404(Periodo, pk=pk, usuario=request.user)
            
            # Desactivar otros períodos
            Periodo.objects.filter(usuario=request.user, activo=True).update(activo=False)
            
            # Activar este período
            periodo.activo = True
            periodo.save()
            
            messages.success(request, f'Período "{periodo.nombre}" activado exitosamente')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class FeriadoListView(LoginRequiredMixin, ListView):
    """Lista de feriados"""
    model = DiaFeriado
    template_name = 'core/feriado_list.html'
    context_object_name = 'feriados'
    
    def get_queryset(self):
        return DiaFeriado.objects.filter(usuario=self.request.user).order_by('fecha')


class FeriadoCreateView(LoginRequiredMixin, CreateView):
    """Crear feriado"""
    model = DiaFeriado
    form_class = DiaFeriadoForm
    template_name = 'core/feriado_form.html'
    success_url = reverse_lazy('core:feriado_list')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Feriado creado exitosamente')
        return super().form_valid(form)


class FeriadoUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar feriado"""
    model = DiaFeriado
    form_class = DiaFeriadoForm
    template_name = 'core/feriado_form.html'
    success_url = reverse_lazy('core:feriado_list')
    
    def get_queryset(self):
        return DiaFeriado.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Feriado actualizado exitosamente')
        return super().form_valid(form)


class FeriadoDeleteView(LoginRequiredMixin, View):
    """Eliminar feriado"""
    def post(self, request, pk):
        try:
            feriado = get_object_or_404(DiaFeriado, pk=pk, usuario=request.user)
            nombre = feriado.nombre
            feriado.delete()
            messages.success(request, f'Feriado "{nombre}" eliminado exitosamente')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# API Views
class DashboardAPIView(APIView):
    """API del dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            periodo_activo = Periodo.objects.get(usuario=request.user, activo=True)
            
            # Obtener horas del período
            horas_periodo = RegistroHora.objects.filter(
                usuario=request.user,
                periodo=periodo_activo
            ).select_related('proyecto')
            
            total_horas = sum(float(h.horas) for h in horas_periodo)
            
            # Agrupar por proyecto
            horas_por_proyecto = {}
            for hora in horas_periodo:
                proyecto_nombre = hora.proyecto.nombre
                if proyecto_nombre not in horas_por_proyecto:
                    horas_por_proyecto[proyecto_nombre] = 0
                horas_por_proyecto[proyecto_nombre] += float(hora.horas)
            
            # Agrupar por tipo de tarea
            horas_por_tipo = {'tarea': 0, 'reunion': 0}
            for hora in horas_periodo:
                horas_por_tipo[hora.tipo_tarea] += float(hora.horas)
            
            # Días con registros
            fechas_unicas = set(h.fecha for h in horas_periodo)
            dias_trabajados = len(fechas_unicas)
            
            # Calcular porcentajes
            porcentaje_completacion = (total_horas / periodo_activo.horas_objetivo * 100) if periodo_activo.horas_objetivo > 0 else 0
            horas_faltantes = max(0, periodo_activo.horas_objetivo - total_horas)
            
            return Response({
                'success': True,
                'total_horas': total_horas,
                'porcentaje_completacion': round(porcentaje_completacion, 1),
                'horas_faltantes': horas_faltantes,
                'dias_trabajados': dias_trabajados,
                'horas_por_proyecto': horas_por_proyecto,
                'horas_por_tipo': horas_por_tipo,
                'periodo': {
                    'id': periodo_activo.id,
                    'nombre': periodo_activo.nombre,
                    'horas_objetivo': periodo_activo.horas_objetivo
                }
            })
        except Periodo.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No hay período activo'
            }, status=404)


class CalendarioAPIView(APIView):
    """API del calendario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, year, month):
        try:
            # Obtener período activo
            periodo_activo = Periodo.objects.get(usuario=request.user, activo=True)
            
            # Obtener días del mes
            cal = calendar.monthcalendar(year, month)
            
            # Obtener feriados
            feriados = DiaFeriado.objects.filter(usuario=request.user)
            fechas_feriados = [f.fecha.strftime('%Y-%m-%d') for f in feriados]
            
            # Obtener registros de horas del mes del período activo
            horas_mes = RegistroHora.objects.filter(
                usuario=request.user,
                fecha__year=year,
                fecha__month=month,
                periodo=periodo_activo
            )
            
            # Agrupar horas por fecha
            horas_por_fecha = {}
            for hora in horas_mes:
                fecha_str = hora.fecha.strftime('%Y-%m-%d')
                if fecha_str not in horas_por_fecha:
                    horas_por_fecha[fecha_str] = 0
                horas_por_fecha[fecha_str] += float(hora.horas)
            
            # Procesar calendario
            calendario_data = []
            for semana in cal:
                semana_data = []
                for dia in semana:
                    if dia == 0:
                        semana_data.append(None)
                    else:
                        fecha_str = f"{year}-{month:02d}-{dia:02d}"
                        es_feriado = fecha_str in fechas_feriados
                        horas_dia = horas_por_fecha.get(fecha_str, 0)
                        es_fin_semana = date(year, month, dia).weekday() >= 5
                        
                        # Determinar estado
                        if es_fin_semana:
                            estado = 'fin_semana'
                        elif es_feriado:
                            estado = 'feriado'
                        elif horas_dia >= periodo_activo.horas_max_dia:
                            estado = 'completo'
                        elif horas_dia > 0:
                            estado = 'incompleto'
                        else:
                            estado = 'sin_horas'
                        
                        semana_data.append({
                            'dia': dia,
                            'fecha': fecha_str,
                            'horas': horas_dia,
                            'estado': estado,
                            'es_feriado': es_feriado,
                            'es_fin_semana': es_fin_semana
                        })
                calendario_data.append(semana_data)
            
            return Response({
                'success': True,
                'calendario': calendario_data,
                'mes': month,
                'año': year,
                'nombre_mes': calendar.month_name[month]
            })
            
        except Periodo.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No hay período activo'
            }, status=404)


class PeriodoAPIView(APIView):
    """API de períodos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        periodos = Periodo.objects.filter(usuario=request.user).order_by('-fecha_inicio')
        data = [{
            'id': p.id,
            'nombre': p.nombre,
            'fecha_inicio': p.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': p.fecha_fin.strftime('%Y-%m-%d'),
            'horas_objetivo': p.horas_objetivo,
            'horas_max_dia': p.horas_max_dia,
            'activo': p.activo
        } for p in periodos]
        return Response(data)


class PeriodoActivoAPIView(APIView):
    """API del período activo"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            periodo = Periodo.objects.get(usuario=request.user, activo=True)
            data = {
                'success': True,
                'periodo': {
                    'id': periodo.id,
                    'nombre': periodo.nombre,
                    'fecha_inicio': periodo.fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': periodo.fecha_fin.strftime('%Y-%m-%d'),
                    'horas_objetivo': periodo.horas_objetivo,
                    'horas_max_dia': periodo.horas_max_dia,
                    'activo': periodo.activo
                }
            }
            return Response(data)
        except Periodo.DoesNotExist:
            # Retornar respuesta exitosa pero sin período activo
            return Response({
                'success': True,
                'periodo': None,
                'message': 'No hay período activo configurado'
            })


class FeriadoAPIView(APIView):
    """API de feriados"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        feriados = DiaFeriado.objects.filter(usuario=request.user).order_by('fecha')
        data = [{
            'id': f.id,
            'fecha': f.fecha.strftime('%Y-%m-%d'),
            'nombre': f.nombre
        } for f in feriados]
        return Response(data)


# ============================================================================
# VISTAS CRUD DE DÍAS FERIADOS
# ============================================================================

class FeriadoListView(LoginRequiredMixin, ListView):
    """Lista de días feriados"""
    model = DiaFeriado
    template_name = 'core/feriado_list.html'
    context_object_name = 'feriados'
    paginate_by = 20
    
    def get_queryset(self):
        return DiaFeriado.objects.filter(usuario=self.request.user).order_by('fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestión de Días Feriados'
        
        # Estadísticas
        feriados = self.get_queryset()
        context['total_feriados'] = feriados.count()
        context['feriados_este_año'] = feriados.filter(fecha__year=date.today().year).count()
        
        return context


class FeriadoDetailView(LoginRequiredMixin, DetailView):
    """Detalle de día feriado"""
    model = DiaFeriado
    template_name = 'core/feriado_detail.html'
    context_object_name = 'feriado'
    
    def get_queryset(self):
        return DiaFeriado.objects.filter(usuario=self.request.user)


class FeriadoCreateView(LoginRequiredMixin, CreateView):
    """Crear día feriado"""
    model = DiaFeriado
    form_class = DiaFeriadoForm
    template_name = 'core/feriado_form.html'
    success_url = reverse_lazy('core:feriado_list')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, f'Día feriado "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Día Feriado'
        context['action'] = 'Crear'
        return context


class FeriadoUpdateView(LoginRequiredMixin, UpdateView):
    """Editar día feriado"""
    model = DiaFeriado
    form_class = DiaFeriadoForm
    template_name = 'core/feriado_form.html'
    success_url = reverse_lazy('core:feriado_list')
    
    def get_queryset(self):
        return DiaFeriado.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'Día feriado "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Día Feriado'
        context['action'] = 'Actualizar'
        return context


class FeriadoDeleteView(LoginRequiredMixin, View):
    """Eliminar día feriado"""
    
    def post(self, request, pk):
        feriado = get_object_or_404(DiaFeriado, pk=pk, usuario=request.user)
        nombre = feriado.nombre
        feriado.delete()
        messages.success(request, f'Día feriado "{nombre}" eliminado exitosamente.')
        return redirect('core:feriado_list')


# ============================================================================
# VISTAS DE GESTIÓN DE FERIADOS EN PERÍODOS
# ============================================================================

class PeriodoFeriadosView(LoginRequiredMixin, DetailView):
    """Vista para gestionar feriados de un período específico"""
    model = Periodo
    template_name = 'core/periodo_feriados.html'
    context_object_name = 'periodo'
    pk_url_kwarg = 'periodo_id'
    
    def get_queryset(self):
        return Periodo.objects.filter(usuario=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.object
        
        # Feriados dentro del período
        feriados_periodo = DiaFeriado.objects.filter(
            usuario=self.request.user,
            fecha__gte=periodo.fecha_inicio,
            fecha__lte=periodo.fecha_fin
        ).order_by('fecha')
        
        # Todos los feriados del usuario
        todos_feriados = DiaFeriado.objects.filter(usuario=self.request.user).order_by('fecha')
        
        context.update({
            'title': f'Feriados del Período: {periodo.nombre}',
            'feriados_periodo': feriados_periodo,
            'todos_feriados': todos_feriados,
            'total_feriados_periodo': feriados_periodo.count(),
        })
        
        return context


class AgregarFeriadoPeriodoView(LoginRequiredMixin, CreateView):
    """Agregar feriado específico para un período"""
    model = DiaFeriado
    form_class = DiaFeriadoForm
    template_name = 'core/periodo_feriado_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.periodo = get_object_or_404(
            Periodo, 
            pk=kwargs['periodo_id'], 
            usuario=request.user
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Validar que la fecha esté dentro del período
        fecha = form.cleaned_data['fecha']
        if not (self.periodo.fecha_inicio <= fecha <= self.periodo.fecha_fin):
            form.add_error('fecha', 
                f'La fecha debe estar entre {self.periodo.fecha_inicio} y {self.periodo.fecha_fin}')
            return self.form_invalid(form)
        
        form.instance.usuario = self.request.user
        messages.success(
            self.request, 
            f'Feriado "{form.instance.nombre}" agregado al período "{self.periodo.nombre}".'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:periodo_feriados', kwargs={'periodo_id': self.periodo.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Agregar Feriado al Período: {self.periodo.nombre}',
            'periodo': self.periodo,
            'action': 'Agregar'
        })
        return context
