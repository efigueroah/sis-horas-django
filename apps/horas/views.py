from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RegistroHora
from .forms import RegistroHoraForm, FiltroHorasForm, RegistroHoraBloqueForm, VistaCompletaDiaForm
from apps.proyectos.models import Proyecto
from apps.core.models import Periodo, DiaFeriado


class TestCalendarView(TemplateView):
    """Vista de prueba para el widget de calendario"""
    template_name = 'test_calendar.html'


class TestHoursWidgetView(TemplateView):
    """Vista de prueba para el widget de horas"""
    template_name = 'test_hours_widget.html'


class HoraListView(LoginRequiredMixin, ListView):
    """Lista de horas con filtros y ordenamiento"""
    model = RegistroHora
    template_name = 'horas/hora_list.html'
    context_object_name = 'horas'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = RegistroHora.objects.filter(usuario=self.request.user).select_related('proyecto')
        
        # Filtros
        proyecto_id = self.request.GET.get('proyecto')
        fecha = self.request.GET.get('fecha')
        
        if proyecto_id:
            queryset = queryset.filter(proyecto_id=proyecto_id)
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        
        # Ordenamiento (por defecto: fecha ascendente)
        orden = self.request.GET.get('orden', 'fecha')
        if orden == 'proyecto':
            queryset = queryset.order_by('proyecto__nombre', 'fecha')
        else:  # fecha (default)
            queryset = queryset.order_by('fecha', 'created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Proyectos para el filtro
        context['proyectos'] = Proyecto.objects.filter(
            usuario=self.request.user, 
            activo=True
        ).order_by('nombre')
        
        # Valores actuales de filtros
        context['filtro_proyecto'] = self.request.GET.get('proyecto', '')
        context['filtro_fecha'] = self.request.GET.get('fecha', '')
        context['orden_actual'] = self.request.GET.get('orden', 'fecha')
        
        # Total de horas de los registros mostrados
        context['total_horas'] = self.get_queryset().aggregate(
            total=Sum('horas')
        )['total'] or 0
        
        return context


class HoraCreateSimpleView(LoginRequiredMixin, CreateView):
    """Crear registro de horas simple (un solo registro)"""
    model = RegistroHora
    form_class = RegistroHoraForm
    template_name = 'horas/hora_simple_form.html'
    success_url = reverse_lazy('horas:hora_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fecha actual
        context['today'] = date.today().isoformat()
        
        # Configuración de horas del usuario
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            context['incremento_horas'] = float(profile.incremento_horas)
            context['horas_minimas'] = float(profile.horas_minimas)
            context['horas_maximas'] = float(profile.horas_maximas)
        else:
            context['incremento_horas'] = 0.5
            context['horas_minimas'] = 0.5
            context['horas_maximas'] = 12.0
        
        return context
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class HoraCreateView(LoginRequiredMixin, CreateView):
    """Crear registro de horas con soporte para múltiples registros"""
    model = RegistroHora
    form_class = RegistroHoraForm
    template_name = 'horas/hora_form.html'
    success_url = reverse_lazy('horas:hora_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar proyectos activos para el JavaScript
        context['proyectos'] = Proyecto.objects.filter(
            usuario=self.request.user,
            activo=True
        ).order_by('nombre')
        
        # Fecha actual
        context['today'] = date.today().isoformat()
        
        # Configuración de horas del usuario
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            context['incremento_horas'] = float(profile.incremento_horas)
            context['horas_minimas'] = float(profile.horas_minimas)
            context['horas_maximas'] = float(profile.horas_maximas)
        else:
            context['incremento_horas'] = 0.5
            context['horas_minimas'] = 0.5
            context['horas_maximas'] = 12.0
        
        # Límite diario del período activo
        try:
            periodo_activo = Periodo.objects.get(usuario=self.request.user, activo=True)
            context['limite_diario'] = float(periodo_activo.horas_max_dia)
        except Periodo.DoesNotExist:
            context['limite_diario'] = 8.0
        
        return context
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class HoraDetailView(LoginRequiredMixin, DetailView):
    """Detalle de registro de horas"""
    model = RegistroHora
    template_name = 'horas/hora_detail.html'
    
    def get_queryset(self):
        return RegistroHora.objects.filter(usuario=self.request.user)


class HoraUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar registro de horas"""
    model = RegistroHora
    form_class = RegistroHoraForm
    template_name = 'horas/hora_edit_form.html'
    success_url = reverse_lazy('horas:hora_list')
    
    def get_queryset(self):
        return RegistroHora.objects.filter(usuario=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar proyectos activos para el JavaScript
        context['proyectos'] = Proyecto.objects.filter(
            usuario=self.request.user,
            activo=True
        ).order_by('nombre')
        
        # Fecha actual
        context['today'] = date.today().isoformat()
        
        # Configuración de horas del usuario
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            context['incremento_horas'] = float(profile.incremento_horas)
            context['horas_minimas'] = float(profile.horas_minimas)
            context['horas_maximas'] = float(profile.horas_maximas)
        else:
            context['incremento_horas'] = 0.5
            context['horas_minimas'] = 0.5
            context['horas_maximas'] = 12.0
        
        # Límite diario del período activo
        try:
            periodo_activo = Periodo.objects.get(usuario=self.request.user, activo=True)
            context['limite_diario'] = float(periodo_activo.horas_max_dia)
        except Periodo.DoesNotExist:
            context['limite_diario'] = 8.0
        
        return context


class HoraDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar registro de horas"""
    model = RegistroHora
    template_name = 'horas/hora_confirm_delete.html'
    success_url = reverse_lazy('horas:hora_list')
    
    def get_queryset(self):
        return RegistroHora.objects.filter(usuario=self.request.user)


# API Views
class HoraAPIView(APIView):
    """API de horas mejorada para FullCalendar"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Obtener parámetros de filtro
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        proyecto_id = request.GET.get('proyecto')
        
        # Filtrar horas del usuario
        horas = RegistroHora.objects.filter(usuario=request.user).select_related('proyecto')
        
        # Aplicar filtros de fecha si se proporcionan
        if fecha_inicio:
            horas = horas.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            horas = horas.filter(fecha__lte=fecha_fin)
        if proyecto_id:
            horas = horas.filter(proyecto_id=proyecto_id)
        
        # Ordenar por fecha
        horas = horas.order_by('fecha', 'created_at')
        
        # Serializar datos con más detalles para FullCalendar
        data = []
        for h in horas:
            data.append({
                'id': h.id,
                'fecha': h.fecha.strftime('%Y-%m-%d'),
                'proyecto_id': h.proyecto.id,
                'proyecto_nombre': h.proyecto.nombre,
                'proyecto_color': h.proyecto.color_hex,
                'horas': float(h.horas),
                'descripcion': h.descripcion,
                'tipo_tarea': h.tipo_tarea,
                'tipo_tarea_display': h.get_tipo_tarea_display(),
                'created_at': h.created_at.isoformat(),
                'updated_at': h.updated_at.isoformat()
            })
        
        return Response(data)
    
    def post(self, request):
        """Crear nuevo registro de horas"""
        try:
            # Obtener datos del request
            fecha = request.data.get('fecha')
            proyecto_id = request.data.get('proyecto')
            horas = request.data.get('horas')
            descripcion = request.data.get('descripcion', '')
            tipo_tarea = request.data.get('tipo_tarea', 'desarrollo')
            
            # Validar datos requeridos
            if not fecha or not proyecto_id or not horas:
                return Response({
                    'success': False,
                    'error': 'Faltan campos requeridos: fecha, proyecto, horas'
                }, status=400)
            
            # Convertir fecha si es string
            if isinstance(fecha, str):
                from datetime import datetime
                try:
                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                except ValueError:
                    return Response({
                        'success': False,
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                    }, status=400)
            
            # Validar que el proyecto pertenezca al usuario
            try:
                from apps.proyectos.models import Proyecto
                proyecto = Proyecto.objects.get(id=proyecto_id, usuario=request.user)
            except Proyecto.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Proyecto no encontrado o no pertenece al usuario'
                }, status=400)
            
            # Crear registro de hora
            registro = RegistroHora.objects.create(
                usuario=request.user,
                fecha=fecha,
                proyecto=proyecto,
                horas=float(horas),
                descripcion=descripcion,
                tipo_tarea=tipo_tarea
            )
            
            return Response({
                'success': True,
                'message': 'Registro creado exitosamente',
                'data': {
                    'id': registro.id,
                    'fecha': registro.fecha.strftime('%Y-%m-%d'),
                    'proyecto_nombre': registro.proyecto.nombre,
                    'horas': float(registro.horas)
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)


class HoraDetailAPIView(APIView):
    """API detalle de horas"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            hora = RegistroHora.objects.get(pk=pk, usuario=request.user)
            data = {
                'id': hora.id,
                'fecha': hora.fecha,
                'proyecto': hora.proyecto.nombre,
                'horas': float(hora.horas),
                'descripcion': hora.descripcion,
                'tipo_tarea': hora.tipo_tarea
            }
            return Response(data)
        except RegistroHora.DoesNotExist:
            return Response({'error': 'Registro no encontrado'}, status=404)


class HoraResumenAPIView(APIView):
    """API resumen de horas"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Resumen de horas'})


class HoraPorFechaAPIView(APIView):
    """API horas por fecha"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, fecha):
        horas = RegistroHora.objects.filter(usuario=request.user, fecha=fecha)
        data = [{
            'id': h.id,
            'proyecto': h.proyecto.nombre,
            'horas': float(h.horas),
            'tipo_tarea': h.tipo_tarea,
            'descripcion': h.descripcion
        } for h in horas]
        return Response(data)


class ValidarHorasAPIView(APIView):
    """API validar horas"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'valid': True})


# ============================================================================
# VISTAS PARA CARGA EN BLOQUE Y VISTA COMPLETA DE DÍA
# ============================================================================

class RegistroHoraBloqueView(LoginRequiredMixin, View):
    """Vista para registro de horas en bloque (múltiples fechas)"""
    template_name = 'horas/hora_bloque_form.html'
    
    def get(self, request):
        form = RegistroHoraBloqueForm(user=request.user)
        
        # Obtener información del período activo para el contexto
        periodo_activo = None
        try:
            periodo_activo = Periodo.objects.get(usuario=request.user, activo=True)
        except Periodo.DoesNotExist:
            messages.warning(request, 'No hay un período activo configurado. Configure un período antes de continuar.')
        
        # Obtener feriados del usuario para el JavaScript
        feriados = list(DiaFeriado.objects.filter(
            usuario=request.user
        ).values_list('fecha', flat=True))
        
        return render(request, self.template_name, {
            'form': form,
            'title': 'Registro de Horas en Bloque',
            'subtitle': 'Registre la misma tarea en múltiples fechas',
            'periodo_activo': periodo_activo,
            'feriados': [f.isoformat() for f in feriados],
            'limite_diario': float(periodo_activo.horas_max_dia) if periodo_activo else 8.0
        })
    
    def post(self, request):
        form = RegistroHoraBloqueForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                # Generar fechas según el patrón seleccionado
                fechas = form.generar_fechas()
                
                if not fechas:
                    messages.warning(request, 'No se generaron fechas válidas con los criterios especificados.')
                    return render(request, self.template_name, {
                        'form': form,
                        'title': 'Registro de Horas en Bloque',
                        'subtitle': 'Registre la misma tarea en múltiples fechas'
                    })
                
                # Crear registros para cada fecha
                registros_creados = []
                registros_omitidos = []
                
                for fecha in fechas:
                    # Verificar si ya existe un registro para esta fecha, proyecto y descripción
                    existe = RegistroHora.objects.filter(
                        usuario=request.user,
                        fecha=fecha,
                        proyecto=form.cleaned_data['proyecto'],
                        descripcion=form.cleaned_data['descripcion']
                    ).exists()
                    
                    if existe:
                        registros_omitidos.append(fecha)
                        continue
                    
                    # Crear el registro
                    registro = RegistroHora.objects.create(
                        usuario=request.user,
                        fecha=fecha,
                        proyecto=form.cleaned_data['proyecto'],
                        horas=form.cleaned_data['horas'],
                        descripcion=form.cleaned_data['descripcion'],
                        tipo_tarea=form.cleaned_data['tipo_tarea']
                    )
                    registros_creados.append(registro)
                
                # Mostrar mensajes de resultado
                if registros_creados:
                    messages.success(
                        request,
                        f'Se crearon {len(registros_creados)} registros de horas exitosamente.'
                    )
                
                if registros_omitidos:
                    messages.info(
                        request,
                        f'Se omitieron {len(registros_omitidos)} fechas por tener registros duplicados.'
                    )
                
                # Redirigir a la lista de horas
                return redirect('horas:hora_list')
                
            except Exception as e:
                messages.error(request, f'Error al crear los registros: {str(e)}')
        
        return render(request, self.template_name, {
            'form': form,
            'title': 'Registro de Horas en Bloque',
            'subtitle': 'Registre la misma tarea en múltiples fechas'
        })


class RegistroBloquePrevisualizacionView(LoginRequiredMixin, View):
    """Vista para previsualizar las fechas que se generarán en el registro en bloque"""
    
    def post(self, request):
        form = RegistroHoraBloqueForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                fechas = form.generar_fechas()
                
                # Verificar registros existentes
                fechas_con_info = []
                for fecha in fechas:
                    existe = RegistroHora.objects.filter(
                        usuario=request.user,
                        fecha=fecha,
                        proyecto=form.cleaned_data['proyecto'],
                        descripcion=form.cleaned_data['descripcion']
                    ).exists()
                    
                    fechas_con_info.append({
                        'fecha': fecha.strftime('%Y-%m-%d'),
                        'fecha_display': fecha.strftime('%d/%m/%Y'),
                        'dia_semana': fecha.strftime('%A'),
                        'existe': existe
                    })
                
                return JsonResponse({
                    'success': True,
                    'fechas': fechas_con_info,
                    'total': len(fechas_con_info),
                    'nuevos': len([f for f in fechas_con_info if not f['existe']]),
                    'existentes': len([f for f in fechas_con_info if f['existe']])
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


class VistaCompletaDiaView(LoginRequiredMixin, View):
    """Vista para mostrar todas las tareas de un día específico"""
    template_name = 'horas/vista_completa_dia.html'
    
    def get(self, request):
        form = VistaCompletaDiaForm(user=request.user)
        fecha_seleccionada = request.GET.get('fecha')
        
        if fecha_seleccionada:
            try:
                fecha = date.fromisoformat(fecha_seleccionada)
                form = VistaCompletaDiaForm({'fecha': fecha}, user=request.user)
                if form.is_valid():
                    return self.mostrar_dia(request, fecha)
            except ValueError:
                messages.error(request, 'Fecha inválida.')
        
        return render(request, self.template_name, {
            'form': form,
            'title': 'Vista Completa del Día',
            'subtitle': 'Vea todas las tareas registradas en una fecha específica'
        })
    
    def post(self, request):
        form = VistaCompletaDiaForm(request.POST, user=request.user)
        
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            return self.mostrar_dia(request, fecha)
        
        return render(request, self.template_name, {
            'form': form,
            'title': 'Vista Completa del Día',
            'subtitle': 'Vea todas las tareas registradas en una fecha específica'
        })
    
    def mostrar_dia(self, request, fecha):
        # Obtener todos los registros del día
        registros = RegistroHora.objects.filter(
            usuario=request.user,
            fecha=fecha
        ).select_related('proyecto').order_by('created_at')
        
        # Calcular estadísticas
        total_horas = registros.aggregate(total=Sum('horas'))['total'] or 0
        
        # Obtener período activo para calcular porcentajes
        try:
            periodo_activo = Periodo.objects.get(usuario=request.user, activo=True)
            horas_max_dia = float(periodo_activo.horas_max_dia)
            porcentaje_cumplido = min((float(total_horas) / horas_max_dia) * 100, 100)
        except Periodo.DoesNotExist:
            horas_max_dia = 8.0
            porcentaje_cumplido = (float(total_horas) / horas_max_dia) * 100
        
        # Agrupar por proyecto
        registros_por_proyecto = {}
        for registro in registros:
            proyecto_id = registro.proyecto.id
            if proyecto_id not in registros_por_proyecto:
                registros_por_proyecto[proyecto_id] = {
                    'proyecto': registro.proyecto,
                    'registros': [],
                    'total_horas': 0
                }
            
            registros_por_proyecto[proyecto_id]['registros'].append(registro)
            registros_por_proyecto[proyecto_id]['total_horas'] += float(registro.horas)
        
        # Verificar si es feriado
        es_feriado = DiaFeriado.objects.filter(usuario=request.user, fecha=fecha).exists()
        
        # Información del día
        info_dia = {
            'fecha': fecha,
            'dia_semana': fecha.strftime('%A'),
            'es_fin_semana': fecha.weekday() >= 5,
            'es_feriado': es_feriado,
            'es_hoy': fecha == date.today(),
        }
        
        form = VistaCompletaDiaForm({'fecha': fecha}, user=request.user)
        
        return render(request, self.template_name, {
            'form': form,
            'fecha_seleccionada': fecha,
            'registros': registros,
            'registros_por_proyecto': registros_por_proyecto.values(),
            'total_horas': total_horas,
            'horas_max_dia': horas_max_dia,
            'porcentaje_cumplido': porcentaje_cumplido,
            'info_dia': info_dia,
            'title': f'Vista Completa del {fecha.strftime("%d/%m/%Y")}',
            'subtitle': f'Todas las tareas del {fecha.strftime("%A, %d de %B de %Y")}'
        })
