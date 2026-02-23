from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class CategoriaMercancia(models.Model):
    """Categorías de mercancias"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Categoría de Mercancía"
        verbose_name_plural = "Categorías de Mercancías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre




   


class Proveedor(models.Model):
    """Proveedores de mercancias"""
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    nombre = models.CharField(max_length=200)
    nombre_comercial = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('PERSONA', 'Persona Natural'),
            ('EMPRESA', 'Empresa'),
            ('COOPERATIVA', 'Cooperativa'),
            ('ESTATAL', 'Entidad Estatal'),
        ],
        default='EMPRESA'
    )
    
    # Información de contacto
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    
    # Información legal/comercial
    identificacion = models.CharField(max_length=20, blank=True, null=True, unique=True)
    licencia_sanitaria = models.CharField(max_length=50, blank=True, null=True)
    fecha_vencimiento_licencia = models.DateField(blank=True, null=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        help_text="Calificación del proveedor (1-5)"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def licencia_vigente(self):
        """Verifica si la licencia sanitaria está vigente"""
        if not self.fecha_vencimiento_licencia:
            return None
        return self.fecha_vencimiento_licencia >= timezone.now().date()


class Mercancia(models.Model):
    """Modelo principal de mercancias"""
    
    # Identificación
    codigo = models.CharField(max_length=50, unique=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    
    # Clasificación
    categoria = models.ForeignKey(
        CategoriaMercancia, 
        on_delete=models.PROTECT,
        related_name='mercancias'
    )
    
    
    
    peso_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        blank=True, 
        null=True,
        help_text="Peso unitario en kg"
    )
    
    volumen_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        blank=True, 
        null=True,
        help_text="Volumen unitario en litros"
    )
    
    # Control de inventario
    stock_actual = models.DecimalField(
        max_digits=15, 
        decimal_places=3, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    
    
    # Precios
    precio_compra = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    precio_venta = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Control de calidad y vencimiento
    requiere_vencimiento = models.BooleanField(
        default=False,
        help_text="Si la mercancia tiene fecha de vencimiento"
    )
    
    requiere_lote = models.BooleanField(
        default=False,
        help_text="Si la mercancia requiere control por lotes"
    )
    
    dias_vida_util = models.IntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Días de vida útil desde la fecha de producción"
    )
    
    temperatura_almacenamiento = models.CharField(
        max_length=20,
        choices=[
            ('AMBIENTE', 'Temperatura Ambiente'),
            ('REFRIGERADO', 'Refrigerado (2-8°C)'),
            ('CONGELADO', 'Congelado (-18°C)'),
            ('SECO', 'Lugar Seco'),
        ],
        default='AMBIENTE'
    )
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    visible_venta = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='mercancias_creadas'
    )

    class Meta:
        verbose_name = "Mercancía"
        verbose_name_plural = "Mercancías"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['stock_actual']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def valor_inventario(self):
        """Calcula el valor total del inventario actual"""
        if self.precio_compra:
            return self.stock_actual * self.precio_compra
        return Decimal('0.00')

    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia porcentual"""
        if self.precio_compra and self.precio_venta and self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return None

    def save(self, *args, **kwargs):
        """Validaciones adicionales al guardar"""
        # Generar código automático si no se proporciona
        if not self.codigo:
            self.codigo = self.generar_codigo()
        
        super().save(*args, **kwargs)

    def generar_codigo(self):
        """Genera un código automático para la mercancia"""
        from django.utils.crypto import get_random_string
        
        # Usar las primeras 3 letras de la categoría + 4 números aleatorios
        prefijo = self.categoria.nombre[:3].upper() if self.categoria else 'PRD'
        sufijo = get_random_string(4, '0123456789')
        return f"{prefijo}{sufijo}"


class LoteMercancia(models.Model):
    """Control de lotes de mercancia"""
    
    mercancia = models.ForeignKey(
        Mercancia, 
        on_delete=models.CASCADE,
        related_name='lotes'
    )
    
    numero_lote = models.CharField(max_length=100)
    fecha_produccion = models.DateField()
    fecha_vencimiento = models.DateField(blank=True, null=True)
    
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='lotes_mercancias'
    )
    
    # Control de inventario por lote
    cantidad_inicial = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    
    cantidad_actual = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    
    costo_unitario = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Control de calidad
    estado_calidad = models.CharField(
        max_length=20,
        choices=[
            ('BUENO', 'Bueno'),
            ('REGULAR', 'Regular'),
            ('VENCIDO', 'Vencido'),
            ('DAÑADO', 'Dañado'),
            ('CUARENTENA', 'En Cuarentena'),
        ],
        default='BUENO'
    )
    
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Lote de Mercancia"
        verbose_name_plural = "Lotes de Mercancias"
        ordering = ['-fecha_produccion']
        unique_together = [['mercancia', 'numero_lote']]
        indexes = [
            models.Index(fields=['numero_lote']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['estado_calidad']),
        ]

    def __str__(self):
        return f"{self.mercancia.nombre} - Lote {self.numero_lote}"

    @property
    def esta_vencido(self):
        """Verifica si el lote está vencido"""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < timezone.now().date()

    @property
    def dias_para_vencer(self):
        """Calcula días para el vencimiento"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days

    @property
    def proximo_a_vencer(self):
        """Verifica si está próximo a vencer (menos de 30 días)"""
        dias = self.dias_para_vencer
        return dias is not None and 0 <= dias <= 30

    @property
    def valor_total(self):
        """Calcula el valor total del lote"""
        if self.costo_unitario:
            return self.cantidad_actual * self.costo_unitario
        return Decimal('0.00')


class MovimientoStock(models.Model):
    """Registro de movimientos de stock de mercancias"""
    
    TIPOS_MOVIMIENTO = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE_POSITIVO', 'Ajuste Positivo'),
        ('AJUSTE_NEGATIVO', 'Ajuste Negativo'),
        ('TRANSFERENCIA_ENTRADA', 'Transferencia Entrada'),
        ('TRANSFERENCIA_SALIDA', 'Transferencia Salida'),
        ('MERMA', 'Merma'),
        ('VENCIMIENTO', 'Por Vencimiento'),
    ]
    
    mercancia = models.ForeignKey(
        Mercancia, 
        on_delete=models.CASCADE,
        related_name='movimientos_mercancias_stock'
    )
    
    lote = models.ForeignKey(
        LoteMercancia, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimientos_mercancias'
    )
    
    tipo_movimiento = models.CharField(max_length=25, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    
    # Stock antes y después del movimiento
    stock_anterior = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    
    stock_posterior = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    
    # Información del movimiento
    fecha_movimiento = models.DateTimeField(default=timezone.now)
    razon = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Referencias
    documento_referencia = models.CharField(max_length=100, blank=True, null=True)
    usuario_responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='movimientos_mercancia_responsable'
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='movimientos_mercancia_creados'
    )

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['mercancia', 'fecha_movimiento']),
            models.Index(fields=['tipo_movimiento']),
            models.Index(fields=['fecha_movimiento']),
        ]

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.mercancia.nombre} - {self.cantidad}"
