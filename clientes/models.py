from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class TipoCliente(models.Model):
    """Tipos de clientes"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Cliente"
        verbose_name_plural = "Tipos de Clientes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    """Modelo para empresas clientes"""
    
    TIPO_EMPRESA_CHOICES = [
        ('PRIVADA', 'Empresa Privada'),
        ('PUBLICA', 'Empresa Pública'),
        ('MIXTA', 'Empresa Mixta'),
        ('COOPERATIVA', 'Cooperativa'),
        ('INDIVIDUAL', 'Persona Natural'),
        ('ONG', 'ONG'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('MOROSO', 'Moroso'),
    ]
    
    # Identificación
    codigo = models.CharField(
        max_length=20, 
        unique=True,
        blank=True,
        help_text="Código único del cliente"
    )
    
    identificacion = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número de identificación"
    )
    
    # Información básica
    razon_social = models.CharField(
        max_length=200,
        help_text="Razón social o nombre de la empresa"
    )
    nombre_comercial = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Nombre comercial"
    )
    
    tipo_cliente = models.ForeignKey(
        TipoCliente,
        on_delete=models.PROTECT,
        related_name='clientes',
        null=True,
        blank=True
    )
    
    tipo_empresa = models.CharField(
        max_length=20,
        choices=TIPO_EMPRESA_CHOICES,
        default='PRIVADA'
    )
    
    # Información de contacto
    telefono_principal = models.CharField(max_length=20)
    telefono_secundario = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    sitio_web = models.URLField(blank=True, null=True)
    
    # Dirección
    direccion = models.TextField(help_text="Dirección completa")
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Ecuador')
    
    # Contacto principal
    nombre_contacto = models.CharField(
        max_length=200,
        help_text="Nombre del contacto principal"
    )
    cargo_contacto = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Cargo del contacto"
    )
    telefono_contacto = models.CharField(max_length=20)
    email_contacto = models.EmailField()
    
    # Información comercial
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento"
    )
    
    # Estado y calificación
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO'
    )
    
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        help_text="Calificación del cliente (1-5 estrellas)"
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    notas_internas = models.TextField(
        blank=True, 
        null=True,
        help_text="Notas de uso interno"
    )
    
    # Control
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clientes_creados'
    )
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['razon_social']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['identificacion']),
            models.Index(fields=['razon_social']),
            models.Index(fields=['estado', 'activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.razon_social}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre comercial o la razón social"""
        return self.nombre_comercial or self.razon_social
    
    @property
    def esta_moroso(self):
        """Verifica si el cliente está moroso"""
        return self.estado == 'MOROSO'
    
    @property
    def puede_comprar(self):
        """Verifica si el cliente puede realizar compras"""
        return self.activo and self.estado in ['ACTIVO', 'MOROSO']
    
    def save(self, *args, **kwargs):
        """Validaciones adicionales al guardar"""
        # Generar código automático si no se proporciona
        if not self.codigo:
            self.codigo = self.generar_codigo()
        
        # Convertir razon_social a mayúsculas
        if self.razon_social:
            self.razon_social = self.razon_social.upper()
        
        super().save(*args, **kwargs)
    
    def generar_codigo(self):
        """Genera un código automático para el cliente"""
        from django.utils.crypto import get_random_string
        
        # Prefijo CLI + 6 números
        ultimo_numero = Cliente.objects.count() + 1
        return f"CLI{str(ultimo_numero).zfill(6)}"


class ContactoCliente(models.Model):
    """Contactos adicionales del cliente"""
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='contactos'
    )
    
    nombre = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    es_principal = models.BooleanField(default=False)
    
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contacto de Cliente"
        verbose_name_plural = "Contactos de Clientes"
        ordering = ['-es_principal', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.cliente.razon_social}"
    
    def save(self, *args, **kwargs):
        """Si es principal, quitar el flag a los demás contactos"""
        if self.es_principal:
            ContactoCliente.objects.filter(
                cliente=self.cliente, 
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        
        super().save(*args, **kwargs)


class DireccionCliente(models.Model):
    """Direcciones adicionales del cliente para entregas"""
    
    TIPO_DIRECCION_CHOICES = [
        ('PRINCIPAL', 'Dirección Principal'),
        ('ENTREGA', 'Dirección de Entrega'),
        ('FACTURACION', 'Dirección de Facturación'),
        ('OTRA', 'Otra'),
    ]
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='direcciones'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_DIRECCION_CHOICES,
        default='ENTREGA'
    )
    
    nombre_referencia = models.CharField(
        max_length=100,
        help_text="Nombre de referencia (ej: Bodega Central, Sucursal Norte)"
    )
    
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    persona_recibe = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Persona que recibe en esta dirección"
    )
    
    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dirección de Cliente"
        verbose_name_plural = "Direcciones de Clientes"
        ordering = ['-es_principal', 'nombre_referencia']
    
    def __str__(self):
        return f"{self.nombre_referencia} - {self.cliente.razon_social}"
    
    def save(self, *args, **kwargs):
        """Si es principal, quitar el flag a las demás direcciones"""
        if self.es_principal:
            DireccionCliente.objects.filter(
                cliente=self.cliente,
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        
        super().save(*args, **kwargs)
