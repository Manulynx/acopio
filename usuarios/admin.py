from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import CustomUser, Perfil, SesionUsuario, LogAuditoria


class PerfilInline(admin.StackedInline):
    """Inline para mostrar perfil en la administración de usuarios"""
    model = Perfil
    extra = 0
    fields = (
        'biografia', 'especialidades', 'certificaciones',
        'linkedin', 'twitter',
        'mostrar_email_publico', 'mostrar_telefono_publico', 'perfil_publico'
    )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administración personalizada para usuarios"""
    
    inlines = [PerfilInline]
    
    # Campos que se muestran en la lista
    list_display = (
        'username', 'email', 'get_full_name', 'cargo', 'departamento',
        'is_active', 'is_staff', 'is_superuser', 'fecha_ingreso',
        'get_avatar_thumbnail', 'esta_bloqueado'
    )
    
    # Campos por los que se puede filtrar
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'departamento',
        'fecha_ingreso', 'date_joined', 'requiere_cambio_password'
    )
    
    # Campos por los que se puede buscar
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cedula', 'cargo')
    
    # Campos que se pueden editar desde la lista
    list_editable = ('is_active',)
    
    # Ordenamiento
    ordering = ('username',)
    
    # Configuración de campos en el formulario
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal Extendida', {
            'fields': ('cedula', 'telefono', 'direccion', 'avatar')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'departamento', 'fecha_ingreso', 'salario')
        }),
        ('Configuraciones de Seguridad', {
            'fields': (
                'intentos_fallidos', 'bloqueado_hasta', 
                'ultimo_cambio_password', 'requiere_cambio_password'
            )
        }),
        ('Configuraciones del Sistema', {
            'fields': ('tema_preferido', 'idioma_preferido', 'notificaciones_email')
        }),
        ('Información de Conexión', {
            'fields': ('ip_ultima_conexion', 'navegador_ultima_conexion')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'creado_por')
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = (
        'fecha_creacion', 'fecha_actualizacion', 'last_login', 
        'date_joined', 'intentos_fallidos'
    )
    
    def get_avatar_thumbnail(self, obj):
        """Muestra miniatura del avatar"""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%;" />',
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 30px; height: 30px; background: #ddd; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px;">{}</div>',
            obj.username[0].upper()
        )
    get_avatar_thumbnail.short_description = 'Avatar'
    
    def esta_bloqueado(self, obj):
        """Indica si el usuario está bloqueado"""
        if obj.esta_bloqueado:
            return format_html(
                '<span style="color: red;">Bloqueado hasta {}</span>',
                obj.bloqueado_hasta.strftime('%d/%m/%Y %H:%M')
            )
        return format_html('<span style="color: green;">Activo</span>')
    esta_bloqueado.short_description = 'Estado de Bloqueo'
    
    def save_model(self, request, obj, form, change):
        """Personalizar guardado del modelo"""
        if not change:  # Si es nuevo usuario
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Administración de perfiles"""
    
    list_display = (
        'usuario', 'get_email', 'perfil_publico', 
        'fecha_creacion', 'fecha_actualizacion'
    )
    
    list_filter = ('perfil_publico', 'mostrar_email_publico', 'fecha_creacion')
    
    search_fields = ('usuario__username', 'usuario__email', 'biografia')
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Email'


@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    """Administración de sesiones de usuario"""
    
    list_display = (
        'usuario', 'fecha_inicio', 'fecha_fin', 'get_duracion',
        'ip_address', 'pais', 'ciudad', 'activa'
    )
    
    list_filter = ('activa', 'fecha_inicio', 'pais')
    
    search_fields = ('usuario__username', 'ip_address', 'pais', 'ciudad')
    
    readonly_fields = ('fecha_inicio', 'duracion', 'session_key')
    
    ordering = ('-fecha_inicio',)
    
    def get_duracion(self, obj):
        """Calcula y muestra la duración de la sesión"""
        duracion = obj.duracion
        if duracion:
            horas = duracion.total_seconds() // 3600
            minutos = (duracion.total_seconds() % 3600) // 60
            return f"{int(horas)}h {int(minutos)}m"
        return "En curso"
    get_duracion.short_description = 'Duración'


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Administración de logs de auditoría"""
    
    list_display = (
        'usuario', 'accion', 'modelo_afectado', 'objeto_id',
        'fecha_creacion', 'ip_address', 'get_codigo_respuesta'
    )
    
    list_filter = (
        'accion', 'modelo_afectado', 'fecha_creacion',
        'codigo_respuesta', 'metodo_http'
    )
    
    search_fields = (
        'usuario__username', 'descripcion', 'modelo_afectado',
        'objeto_id', 'ip_address'
    )
    
    readonly_fields = (
        'usuario', 'accion', 'modelo_afectado', 'objeto_id',
        'descripcion', 'datos_anteriores', 'datos_nuevos',
        'ip_address', 'user_agent', 'fecha_creacion',
        'url_solicitada', 'metodo_http', 'codigo_respuesta'
    )
    
    ordering = ('-fecha_creacion',)
    
    date_hierarchy = 'fecha_creacion'
    
    def get_codigo_respuesta(self, obj):
        """Muestra código de respuesta con color"""
        if obj.codigo_respuesta:
            if obj.codigo_respuesta < 300:
                color = 'green'
            elif obj.codigo_respuesta < 400:
                color = 'orange'
            else:
                color = 'red'
            
            return format_html(
                '<span style="color: {};">{}</span>',
                color, obj.codigo_respuesta
            )
        return '-'
    get_codigo_respuesta.short_description = 'Código'
    
    def has_add_permission(self, request):
        """Los logs de auditoría no se pueden crear manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Los logs de auditoría no se pueden modificar"""
        return False


# Personalizar el sitio de administración
admin.site.site_header = "Administración UEB Acopio Bayamo"
admin.site.site_title = "UEB Acopio Bayamo"
admin.site.index_title = "Panel de Administración"
