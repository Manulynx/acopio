from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.core.validators import RegexValidator
from PIL import Image
import os


class CustomUser(AbstractUser):
    """
    Modelo extendido de usuario para UEB Acopio Bayamo
    Incluye información adicional para empleados del sistema de inventarios
    """
    
    # Información personal extendida
    cedula = models.CharField(
        max_length=11, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[RegexValidator(regex=r'^\d{11}$', message='La cédula debe tener 11 dígitos')],
        help_text="Número de cédula de identidad (11 dígitos)"
    )
    
    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{8,15}$', message='Número de teléfono válido')],
        help_text="Número de teléfono de contacto"
    )
    
    direccion = models.TextField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Dirección de residencia"
    )
    
    # Información laboral
    cargo = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Cargo o posición en la empresa"
    )
    
    departamento = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        choices=[
            ('ADMINISTRACION', 'Administración'),
            ('INVENTARIO', 'Inventario'),
            ('ALMACEN', 'Almacén'),
            ('VENTAS', 'Ventas'),
            ('COMPRAS', 'Compras'),
            ('CONTABILIDAD', 'Contabilidad'),
            ('RECURSOS_HUMANOS', 'Recursos Humanos'),
            ('SISTEMAS', 'Sistemas'),
        ],
        help_text="Departamento al que pertenece"
    )
    
    fecha_ingreso = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de ingreso a la empresa"
    )
    
    salario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Salario mensual"
    )
    
    # Información de avatar
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        help_text="Foto de perfil del usuario"
    )
    
    # Configuraciones de sesión y seguridad
    intentos_fallidos = models.PositiveIntegerField(
        default=0,
        help_text="Número de intentos de login fallidos consecutivos"
    )
    
    bloqueado_hasta = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha hasta la cual el usuario está bloqueado"
    )
    
    ultimo_cambio_password = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha del último cambio de contraseña"
    )
    
    requiere_cambio_password = models.BooleanField(
        default=False,
        help_text="Si el usuario debe cambiar su contraseña en el próximo login"
    )
    
    # Configuraciones del sistema
    tema_preferido = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Oscuro'),
            ('auto', 'Automático'),
        ],
        default='light',
        help_text="Tema visual preferido"
    )
    
    idioma_preferido = models.CharField(
        max_length=10,
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        default='es',
        help_text="Idioma preferido"
    )
    
    notificaciones_email = models.BooleanField(
        default=True,
        help_text="Recibir notificaciones por email"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='usuarios_creados',
        help_text="Usuario que creó este registro"
    )
    
    # Campos adicionales para auditoría
    ip_ultima_conexion = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP de la última conexión"
    )
    
    navegador_ultima_conexion = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Navegador usado en la última conexión"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']
        permissions = [
            ("can_view_all_users", "Puede ver todos los usuarios"),
            ("can_manage_user_permissions", "Puede gestionar permisos de usuarios"),
            ("can_reset_passwords", "Puede resetear contraseñas"),
            ("can_block_users", "Puede bloquear/desbloquear usuarios"),
            ("can_view_audit_logs", "Puede ver logs de auditoría"),
        ]

    def __str__(self):
        return f"{self.username} - {self.get_full_name() or 'Sin nombre'}"

    def save(self, *args, **kwargs):
        # Procesar avatar si existe
        super().save(*args, **kwargs)
        
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                
                # Redimensionar si es muy grande
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass  # Si hay error procesando imagen, continuar
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario"""
        return self.first_name or self.username
    
    @property
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado"""
        if self.bloqueado_hasta:
            return timezone.now() < self.bloqueado_hasta
        return False
    
    @property
    def dias_sin_cambiar_password(self):
        """Calcula días desde el último cambio de contraseña"""
        if self.ultimo_cambio_password:
            return (timezone.now() - self.ultimo_cambio_password).days
        return None
    
    @property
    def necesita_cambio_password(self):
        """Verifica si necesita cambiar contraseña (más de 90 días)"""
        dias = self.dias_sin_cambiar_password
        return self.requiere_cambio_password or (dias and dias > 90)
    
    def bloquear_usuario(self, minutos=30):
        """Bloquea el usuario por X minutos"""
        self.bloqueado_hasta = timezone.now() + timezone.timedelta(minutes=minutos)
        self.save(update_fields=['bloqueado_hasta'])
    
    def desbloquear_usuario(self):
        """Desbloquea el usuario"""
        self.bloqueado_hasta = None
        self.intentos_fallidos = 0
        self.save(update_fields=['bloqueado_hasta', 'intentos_fallidos'])
    
    def incrementar_intentos_fallidos(self):
        """Incrementa el contador de intentos fallidos"""
        self.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos fallidos
        if self.intentos_fallidos >= 5:
            self.bloquear_usuario()
        
        self.save(update_fields=['intentos_fallidos'])
    
    def resetear_intentos_fallidos(self):
        """Resetea el contador de intentos fallidos"""
        self.intentos_fallidos = 0
        self.save(update_fields=['intentos_fallidos'])
    
    def puede_ver_usuario(self, otro_usuario):
        """Verifica si puede ver la información de otro usuario"""
        # Superusuario puede ver todo
        if self.is_superuser:
            return True
        
        # Staff puede ver usuarios normales
        if self.is_staff and not otro_usuario.is_staff:
            return True
        
        # Usuario puede ver su propio perfil
        if self == otro_usuario:
            return True
        
        # Verificar permisos específicos
        return self.has_perm('usuarios.can_view_all_users')
    
    def puede_editar_usuario(self, otro_usuario):
        """Verifica si puede editar otro usuario"""
        # Superusuario puede editar todo (excepto otros superusuarios)
        if self.is_superuser:
            return True
        
        # Staff puede editar usuarios normales
        if self.is_staff and not otro_usuario.is_staff and not otro_usuario.is_superuser:
            return True
        
        # Usuario puede editar su propio perfil (limitado)
        if self == otro_usuario:
            return True
        
        return False
    
    def puede_eliminar_usuario(self, otro_usuario):
        """Verifica si puede eliminar otro usuario"""
        # No puede eliminarse a sí mismo
        if self == otro_usuario:
            return False
        
        # Solo superusuarios pueden eliminar
        if not self.is_superuser:
            return False
        
        # No puede eliminar otros superusuarios
        if otro_usuario.is_superuser:
            return False
        
        return True


class Perfil(models.Model):
    """
    Modelo para información adicional del perfil de usuario
    """
    usuario = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='perfil'
    )
    
    # Información profesional
    biografia = models.TextField(
        max_length=1000, 
        blank=True, 
        null=True,
        help_text="Biografía o descripción profesional"
    )
    
    especialidades = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Especialidades o áreas de expertise (separadas por comas)"
    )
    
    certificaciones = models.TextField(
        max_length=1000, 
        blank=True, 
        null=True,
        help_text="Certificaciones profesionales"
    )
    
    # Redes sociales y contacto
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.CharField(max_length=50, blank=True, null=True)
    
    # Configuraciones de privacidad
    mostrar_email_publico = models.BooleanField(
        default=False,
        help_text="Mostrar email en perfil público"
    )
    
    mostrar_telefono_publico = models.BooleanField(
        default=False,
        help_text="Mostrar teléfono en perfil público"
    )
    
    perfil_publico = models.BooleanField(
        default=False,
        help_text="Hacer el perfil visible públicamente"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class SesionUsuario(models.Model):
    """
    Modelo para trackear sesiones de usuarios
    """
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sesiones'
    )
    
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    session_key = models.CharField(max_length=40, blank=True, null=True)
    
    # Información de ubicación (opcional)
    pais = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuario"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Sesión de {self.usuario.username} - {self.fecha_inicio}"
    
    @property
    def duracion(self):
        """Calcula la duración de la sesión"""
        fin = self.fecha_fin or timezone.now()
        return fin - self.fecha_inicio


class LogAuditoria(models.Model):
    """
    Modelo para auditoría de acciones de usuarios
    """
    ACCIONES = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('VIEW', 'Visualización'),
        ('EXPORT', 'Exportación'),
        ('IMPORT', 'Importación'),
        ('PASSWORD_CHANGE', 'Cambio de contraseña'),
        ('PASSWORD_RESET', 'Reset de contraseña'),
        ('PERMISSION_CHANGE', 'Cambio de permisos'),
        ('BLOCK', 'Bloqueo de usuario'),
        ('UNBLOCK', 'Desbloqueo de usuario'),
    ]
    
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='logs_auditoria'
    )
    
    accion = models.CharField(max_length=20, choices=ACCIONES)
    
    modelo_afectado = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Nombre del modelo afectado"
    )
    
    objeto_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="ID del objeto afectado"
    )
    
    descripcion = models.TextField(
        help_text="Descripción detallada de la acción"
    )
    
    datos_anteriores = models.JSONField(
        null=True, 
        blank=True,
        help_text="Datos antes del cambio (JSON)"
    )
    
    datos_nuevos = models.JSONField(
        null=True, 
        blank=True,
        help_text="Datos después del cambio (JSON)"
    )
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Campos adicionales para contexto
    url_solicitada = models.CharField(max_length=500, blank=True, null=True)
    metodo_http = models.CharField(max_length=10, blank=True, null=True)
    codigo_respuesta = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'accion']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['modelo_afectado', 'objeto_id']),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"{usuario_str} - {self.get_accion_display()} - {self.fecha_creacion}"
