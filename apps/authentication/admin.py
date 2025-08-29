from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_horas_max_dia')
    list_filter = BaseUserAdmin.list_filter + ('profile__horas_max_dia',)
    
    def get_horas_max_dia(self, obj):
        return obj.profile.horas_max_dia if hasattr(obj, 'profile') else 'N/A'
    get_horas_max_dia.short_description = 'Horas Máx/Día'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre_completo', 'horas_max_dia', 'timezone', 'tema')
    list_filter = ('horas_max_dia', 'tema', 'timezone')
    search_fields = ('user__username', 'user__email', 'nombre_completo')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'nombre_completo')
        }),
        ('Configuración', {
            'fields': ('horas_max_dia', 'timezone', 'formato_fecha', 'tema')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
