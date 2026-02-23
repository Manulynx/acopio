from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.db.models import F

from clientes.models import Cliente
from productos.models import Producto, LoteProducto
from mercancia.models import Mercancia, LoteMercancia

User = get_user_model()

class Venta(models.Model):
    """Registro de ventas a clientes"""
    
    # Información básica
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    fecha_venta = models.DateTimeField(default=timezone.now)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ventas'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    impuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Estado
    ESTADOS_VENTA = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_VENTA,
        default='PENDIENTE'
    )
    
    # Observaciones
    notas = models.TextField(blank=True, null=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ventas_creadas'
    )
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']
        indexes = [
            models.Index(fields=['fecha_venta']),
            models.Index(fields=['cliente', 'estado']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.cliente.nombre} ({self.fecha_venta.strftime('%d/%m/%Y')})"
    
    def calcular_total(self):
        """Calcula los totales de la venta"""
        self.subtotal = sum(
            detalle.subtotal 
            for detalle in self.detalles_productos.all()
        ) + sum(
            detalle.subtotal 
            for detalle in self.detalles_mercancias.all()
        )
        
        # Impuestos (ejemplo: 12%)
        self.impuestos = self.subtotal * Decimal('0.12')
        self.total = self.subtotal + self.impuestos
        self.save()
    
    def actualizar_stock(self):
        """Actualiza el stock de productos y mercancías"""
        from productos.models import MovimientoStock
        from mercancia.models import MovimientoStock as MovimientoStockMercancia
        
        if self.estado in ['PENDIENTE', 'COMPLETADA']:
            # Actualizar stock de productos
            for detalle in self.detalles_productos.all():
                producto = detalle.producto
                # Obtener el valor actual del stock
                producto.refresh_from_db()
                stock_anterior = producto.stock_actual
                
                # Actualizar stock del producto directamente
                producto.stock_actual = stock_anterior - detalle.cantidad
                producto.save()
                
                # Actualizar stock del lote si existe
                if detalle.lote:
                    detalle.lote.refresh_from_db()
                    detalle.lote.cantidad_actual -= detalle.cantidad
                    detalle.lote.save()
                
                # Registrar movimiento
                MovimientoStock.objects.create(
                    producto=producto,
                    lote=detalle.lote,
                    tipo_movimiento='SALIDA',
                    cantidad=detalle.cantidad,
                    stock_anterior=stock_anterior,
                    stock_posterior=producto.stock_actual,
                    fecha_movimiento=self.fecha_venta,
                    razon=f'Salida por venta {self.codigo}',
                    documento_referencia=self.codigo,
                    usuario_responsable=self.creado_por,
                    creado_por=self.creado_por
                )
            
            # Actualizar stock de mercancías
            for detalle in self.detalles_mercancias.all():
                mercancia = detalle.mercancia
                # Obtener el valor actual del stock
                mercancia.refresh_from_db()
                stock_anterior = mercancia.stock_actual
                
                # Actualizar stock de la mercancía directamente
                mercancia.stock_actual = stock_anterior - detalle.cantidad
                mercancia.save()
                
                # Actualizar stock del lote si existe
                if detalle.lote:
                    detalle.lote.refresh_from_db()
                    detalle.lote.cantidad_actual -= detalle.cantidad
                    detalle.lote.save()
                
                # Registrar movimiento
                MovimientoStockMercancia.objects.create(
                    mercancia=mercancia,
                    lote=detalle.lote,
                    tipo_movimiento='SALIDA',
                    cantidad=detalle.cantidad,
                    stock_anterior=stock_anterior,
                    stock_posterior=mercancia.stock_actual,
                    fecha_movimiento=self.fecha_venta,
                    razon=f'Salida por venta {self.codigo}',
                    documento_referencia=self.codigo,
                    usuario_responsable=self.creado_por,
                    creado_por=self.creado_por
                )
    
    def restaurar_stock(self):
        """Restaura el stock al cancelar una venta"""
        from productos.models import MovimientoStock
        from mercancia.models import MovimientoStock as MovimientoStockMercancia
        
        if self.estado == 'CANCELADA':
            # Restaurar stock de productos
            for detalle in self.detalles_productos.all():
                producto = detalle.producto
                # Obtener el valor actual del stock
                producto.refresh_from_db()
                stock_anterior = producto.stock_actual
                
                # Restaurar stock del producto directamente
                producto.stock_actual = stock_anterior + detalle.cantidad
                producto.save()
                
                # Restaurar stock del lote si existe
                if detalle.lote:
                    detalle.lote.refresh_from_db()
                    detalle.lote.cantidad_actual += detalle.cantidad
                    detalle.lote.save()
                
                # Registrar movimiento
                MovimientoStock.objects.create(
                    producto=producto,
                    lote=detalle.lote,
                    tipo_movimiento='AJUSTE_POSITIVO',
                    cantidad=detalle.cantidad,
                    stock_anterior=stock_anterior,
                    stock_posterior=producto.stock_actual,
                    fecha_movimiento=timezone.now(),
                    razon=f'Restauración de stock por cancelación de venta {self.codigo}',
                    documento_referencia=self.codigo,
                    usuario_responsable=self.creado_por,
                    creado_por=self.creado_por
                )
            
            # Restaurar stock de mercancías
            for detalle in self.detalles_mercancias.all():
                mercancia = detalle.mercancia
                # Obtener el valor actual del stock
                mercancia.refresh_from_db()
                stock_anterior = mercancia.stock_actual
                
                # Restaurar stock de la mercancía directamente
                mercancia.stock_actual = stock_anterior + detalle.cantidad
                mercancia.save()
                
                # Restaurar stock del lote si existe
                if detalle.lote:
                    detalle.lote.refresh_from_db()
                    detalle.lote.cantidad_actual += detalle.cantidad
                    detalle.lote.save()
                
                # Registrar movimiento
                MovimientoStockMercancia.objects.create(
                    mercancia=mercancia,
                    lote=detalle.lote,
                    tipo_movimiento='AJUSTE_POSITIVO',
                    cantidad=detalle.cantidad,
                    stock_anterior=stock_anterior,
                    stock_posterior=mercancia.stock_actual,
                    fecha_movimiento=timezone.now(),
                    razon=f'Restauración de stock por cancelación de venta {self.codigo}',
                    documento_referencia=self.codigo,
                    usuario_responsable=self.creado_por,
                    creado_por=self.creado_por
                )
    
    def save(self, *args, **kwargs):
        """Genera código automático si no existe"""
        # Generar código si es nuevo
        if not self.codigo:
            ultimo = Venta.objects.order_by('-fecha_creacion').first()
            if ultimo:
                ultimo_num = int(ultimo.codigo.split('-')[1])
                siguiente_num = ultimo_num + 1
            else:
                siguiente_num = 1
            self.codigo = f"V-{str(siguiente_num).zfill(6)}"
        
        super().save(*args, **kwargs)


class DetalleVentaProducto(models.Model):
    """Detalle de productos vendidos"""
    
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles_productos'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='ventas_producto'
    )
    lote = models.ForeignKey(
        LoteProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_lote'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = "Detalle de Venta - Producto"
        verbose_name_plural = "Detalles de Venta - Productos"
        indexes = [
            models.Index(fields=['venta', 'producto']),
            models.Index(fields=['lote']),
        ]
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"
    
    def clean(self):
        """Valida que haya stock suficiente y calcula el subtotal"""
        from django.core.exceptions import ValidationError

        # Calcular subtotal antes de validar
        if self.cantidad and self.precio_unitario:
            self.subtotal = self.cantidad * self.precio_unitario
        
        # Solo validar stock si la venta está en estado PENDIENTE o COMPLETADA
        if not self.venta_id or self.venta.estado in ['PENDIENTE', 'COMPLETADA']:
            # Validar stock en lote si se especifica
            if self.lote and self.lote.cantidad_actual < self.cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente en el lote. Disponible: {self.lote.cantidad_actual}'
                })
            
            # Validar stock general del producto
            if self.producto.stock_actual < self.cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {self.producto.stock_actual}'
                })
        
        return super().clean()
    
    def save(self, *args, **kwargs):
        """Guarda el detalle y actualiza totales"""
        self.full_clean()  # Ejecuta validaciones
        super().save(*args, **kwargs)
        
        # Actualizar totales de la venta solo si ya existe en la base de datos
        if self.venta_id:
            self.venta.calcular_total()
    

class DetalleVentaMercancia(models.Model):
    """Detalle de mercancías vendidas"""
    
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles_mercancias'
    )
    mercancia = models.ForeignKey(
        Mercancia,
        on_delete=models.PROTECT,
        related_name='ventas_mercancia'
    )
    lote = models.ForeignKey(
        LoteMercancia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_lote'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = "Detalle de Venta - Mercancía"
        verbose_name_plural = "Detalles de Venta - Mercancías"
        indexes = [
            models.Index(fields=['venta', 'mercancia']),
            models.Index(fields=['lote']),
        ]
    
    def __str__(self):
        return f"{self.mercancia.nombre} - {self.cantidad}"
    
    def clean(self):
        """Valida que haya stock suficiente y calcula el subtotal"""
        from django.core.exceptions import ValidationError

        # Calcular subtotal antes de validar
        if self.cantidad and self.precio_unitario:
            self.subtotal = self.cantidad * self.precio_unitario
        
        # Solo validar stock si la venta está en estado PENDIENTE o COMPLETADA
        if not self.venta_id or self.venta.estado in ['PENDIENTE', 'COMPLETADA']:
            # Validar stock en lote si se especifica
            if self.lote and self.lote.cantidad_actual < self.cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente en el lote. Disponible: {self.lote.cantidad_actual}'
                })
            
            # Validar stock general de la mercancía
            if self.mercancia.stock_actual < self.cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {self.mercancia.stock_actual}'
                })
        
        return super().clean()
    
    def save(self, *args, **kwargs):
        """Guarda el detalle y actualiza totales"""
        self.full_clean()  # Ejecuta validaciones
        super().save(*args, **kwargs)
        
        # Actualizar totales de la venta solo si ya existe en la base de datos
        if self.venta_id:
            self.venta.calcular_total()
