from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class TipoInmueble(models.Model):
    """Tipos de inmuebles (Bodega, Almacén, Depósito, etc.)"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Inmueble"
        verbose_name_plural = "Tipos de Inmuebles"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Inmueble(models.Model):
    """Modelo principal para propiedades disponibles para arriendo"""
    
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('ARRENDADO', 'Arrendado'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
        ('RESERVADO', 'Reservado'),
        ('NO_DISPONIBLE', 'No Disponible'),
    ]
    
    TIPO_USO_CHOICES = [
        ('ALMACENAMIENTO', 'Almacenamiento'),
        ('REFRIGERACION', 'Refrigeración'),
        ('CONGELACION', 'Congelación'),
        ('OFICINA', 'Oficina'),
        ('MIXTO', 'Uso Mixto'),
    ]
    
    CONDICION_CHOICES = [
        ('EXCELENTE', 'Excelente'),
        ('BUENA', 'Buena'),
        ('REGULAR', 'Regular'),
        ('REQUIERE_REPARACION', 'Requiere Reparación'),
    ]
    
    # Identificación
    codigo = models.CharField(
        max_length=20, 
        unique=True,
        blank=True,
        help_text="Código único del inmueble"
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre o identificación del inmueble"
    )
    
    tipo = models.ForeignKey(
        TipoInmueble,
        on_delete=models.PROTECT,
        related_name='inmuebles'
    )
    
    # Características físicas
    area_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Área total en metros cuadrados"
    )
    
    area_util = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Área útil en metros cuadrados"
    )
    
    altura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Altura en metros"
    )
    
    capacidad_carga = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Capacidad de carga en toneladas"
    )
    
    numero_ambientes = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=1,
        help_text="Número de ambientes o divisiones"
    )
    
    numero_banos = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de baños"
    )
    
    numero_estacionamientos = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Número de estacionamientos"
    )
    
    # Ubicación
    direccion = models.TextField(help_text="Dirección completa")
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    coordenadas_lat = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        help_text="Latitud"
    )
    
    coordenadas_lng = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        help_text="Longitud"
    )
    
    # Características del inmueble
    tipo_uso = models.CharField(
        max_length=20,
        choices=TIPO_USO_CHOICES,
        default='ALMACENAMIENTO'
    )
    
    condicion = models.CharField(
        max_length=30,
        choices=CONDICION_CHOICES,
        default='BUENA'
    )
    
    ano_construccion = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        blank=True,
        null=True,
        help_text="Año de construcción"
    )
    
    # Servicios e instalaciones
    tiene_electricidad = models.BooleanField(default=True)
    tiene_agua = models.BooleanField(default=True)
    tiene_gas = models.BooleanField(default=False)
    tiene_internet = models.BooleanField(default=False)
    tiene_seguridad = models.BooleanField(default=False)
    tiene_vigilancia_24h = models.BooleanField(default=False)
    tiene_camaras = models.BooleanField(default=False)
    tiene_alarma = models.BooleanField(default=False)
    tiene_extintor = models.BooleanField(default=False)
    tiene_rociadores = models.BooleanField(default=False)
    tiene_carga_descarga = models.BooleanField(default=False)
    tiene_montacargas = models.BooleanField(default=False)
    tiene_rampa = models.BooleanField(default=False)
    
    # Información de arriendo
    precio_arriendo_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio de arriendo mensual"
    )
    
    gastos_comunes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Gastos comunes mensuales"
    )
    
    deposito_garantia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Depósito de garantía requerido"
    )
    
    dias_preaviso = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=30,
        help_text="Días de preaviso para desocupar"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='DISPONIBLE'
    )
    
    fecha_disponibilidad = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha desde la cual está disponible"
    )
    
    # Información adicional
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del inmueble"
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones internas"
    )
    
    # Control
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(
        default=False,
        help_text="Marcar como destacado en listados"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inmuebles_creados'
    )
    
    class Meta:
        verbose_name = "Inmueble"
        verbose_name_plural = "Inmuebles"
        ordering = ['-destacado', 'nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['estado', 'activo']),
            models.Index(fields=['tipo', 'ciudad']),
            models.Index(fields=['precio_arriendo_mensual']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def esta_disponible(self):
        """Verifica si el inmueble está disponible para arriendo"""
        return self.activo and self.estado == 'DISPONIBLE'
    
    @property
    def costo_total_mensual(self):
        """Calcula el costo total mensual (arriendo + gastos comunes)"""
        return self.precio_arriendo_mensual + self.gastos_comunes
    
    @property
    def area_disponible_porcentaje(self):
        """Calcula el porcentaje de área útil respecto al área total"""
        if self.area_util and self.area_total:
            return (self.area_util / self.area_total) * 100
        return 100
    
    def save(self, *args, **kwargs):
        """Validaciones adicionales al guardar"""
        # Generar código automático si no se proporciona
        if not self.codigo:
            self.codigo = self.generar_codigo()
        
        super().save(*args, **kwargs)
    
    def generar_codigo(self):
        """Genera un código automático para el inmueble"""
        # Prefijo INM + 6 números
        ultimo_numero = Inmueble.objects.count() + 1
        return f"INM{str(ultimo_numero).zfill(6)}"


class ImagenInmueble(models.Model):
    """Imágenes del inmueble"""
    
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    
    imagen = models.ImageField(
        upload_to='inmuebles/%Y/%m/',
        help_text="Imagen del inmueble"
    )
    
    titulo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Título o descripción de la imagen"
    )
    
    es_principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Inmueble"
        verbose_name_plural = "Imágenes de Inmuebles"
        ordering = ['-es_principal', 'orden', 'fecha_creacion']
    
    def __str__(self):
        return f"Imagen de {self.inmueble.nombre}"
    
    def save(self, *args, **kwargs):
        """Si es principal, quitar el flag a las demás imágenes"""
        if self.es_principal:
            ImagenInmueble.objects.filter(
                inmueble=self.inmueble,
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        
        super().save(*args, **kwargs)


class CaracteristicaAdicional(models.Model):
    """Características adicionales configurables"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Clase de icono FontAwesome"
    )
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Característica Adicional"
        verbose_name_plural = "Características Adicionales"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class InmuebleCaracteristica(models.Model):
    """Relación entre inmuebles y características adicionales"""
    
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='caracteristicas_adicionales'
    )
    
    caracteristica = models.ForeignKey(
        CaracteristicaAdicional,
        on_delete=models.CASCADE
    )
    
    valor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Valor específico de la característica (opcional)"
    )
    
    class Meta:
        verbose_name = "Característica del Inmueble"
        verbose_name_plural = "Características de Inmuebles"
        unique_together = ['inmueble', 'caracteristica']
    
    def __str__(self):
        return f"{self.inmueble.nombre} - {self.caracteristica.nombre}"


class MantenimientoInmueble(models.Model):
    """Registro de mantenimientos del inmueble"""
    
    TIPO_MANTENIMIENTO_CHOICES = [
        ('PREVENTIVO', 'Preventivo'),
        ('CORRECTIVO', 'Correctivo'),
        ('EMERGENCIA', 'Emergencia'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='mantenimientos'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_MANTENIMIENTO_CHOICES
    )
    
    descripcion = models.TextField(help_text="Descripción del mantenimiento")
    
    fecha_programada = models.DateField(
        help_text="Fecha programada para el mantenimiento"
    )
    
    fecha_realizacion = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha en que se realizó el mantenimiento"
    )
    
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Costo del mantenimiento"
    )
    
    proveedor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Proveedor que realizó el mantenimiento"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_creados'
    )
    
    class Meta:
        verbose_name = "Mantenimiento de Inmueble"
        verbose_name_plural = "Mantenimientos de Inmuebles"
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.inmueble.nombre} - {self.tipo} - {self.fecha_programada}"
