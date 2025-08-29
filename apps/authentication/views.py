from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm


class CustomLoginView(LoginView):
    """Vista personalizada de login"""
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido, {form.get_user().username}!')
        return super().form_valid(form)


class RegisterView(CreateView):
    """Vista de registro de nuevos usuarios"""
    form_class = CustomUserCreationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Loguear automáticamente al usuario después del registro
        login(self.request, self.object)
        messages.success(self.request, '¡Cuenta creada exitosamente!')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        # Redirigir usuarios autenticados
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista del perfil de usuario"""
    template_name = 'authentication/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user.profile
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Vista para editar el perfil de usuario"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'authentication/profile_edit.html'
    success_url = reverse_lazy('authentication:profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente')
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Vista personalizada para cambio de contraseña"""
    template_name = 'authentication/password_change.html'
    success_url = reverse_lazy('authentication:password_change_done')
    
    def form_valid(self, form):
        messages.success(self.request, 'Contraseña cambiada exitosamente')
        return super().form_valid(form)
