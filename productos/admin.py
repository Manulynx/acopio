from django.contrib import admin
from django.db.models import Sum, F
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CategoriaProducto, Proveedor, 
    Producto, LoteProducto, MovimientoStock
)


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'total_productos', 'fecha_creacion']
    list_filter = ['activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'activa')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def total_productos(self, obj):
        return obj.productos.filter(activo=True).count()
    total_productos.short_description = 'Total Productos'
    
    def save_model(self, request, obj, form, change):
        # Guardar el modelo sin modificar campos adicionales
        super().save_model(request, obj, form, change)




@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'tipo', 'telefono', 'email', 
        'licencia_estado', 'calificacion', 'activo'
    ]
    list_filter = ['tipo', 'activo', 'calificacion', 'provincia']
    search_fields = ['codigo', 'nombre', 'nombre_comercial', 'nit', 'email']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'nombre_comercial', 'tipo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'ciudad', 'provincia')
        }),
        ('Información Legal', {
            'fields': ('nit', 'licencia_sanitaria', 'fecha_vencimiento_licencia')
        }),
        ('Estado y Calificación', {
            'fields': ('activo', 'calificacion')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def licencia_estado(self, obj):
        if not obj.licencia_sanitaria:
            return format_html('<span style="color: gray;">Sin licencia</span>')
        
        estado = obj.licencia_vigente
        if estado is None:
            return format_html('<span style="color: orange;">Sin fecha</span>')
        elif estado:
            return format_html('<span style="color: green;">Vigente</span>')
        else:
            return format_html('<span style="color: red;">Vencida</span>')
    licencia_estado.short_description = 'Estado Licencia'
    
    def save_model(self, request, obj, form, change):
        # Guardar el modelo sin modificar campos adicionales
        super().save_model(request, obj, form, change)


class LoteProductoInline(admin.TabularInline):
    model = LoteProducto
    extra = 0
    readonly_fields = ['cantidad_actual', 'fecha_creacion']
    fields = [
        'numero_lote', 'fecha_produccion', 'fecha_vencimiento',
        'cantidad_inicial', 'cantidad_actual', 'estado_calidad'
    ]


class MovimientoStockInline(admin.TabularInline):
    model = MovimientoStock
    extra = 0
    readonly_fields = ['fecha_creacion', 'stock_anterior', 'stock_posterior']
    fields = [
        'tipo_movimiento', 'cantidad', 'stock_anterior', 'stock_posterior',
        'fecha_movimiento', 'razon'
    ]
    ordering = ['-fecha_movimiento']
    
    def has_add_permission(self, request, obj=None):
        return False  # No permitir agregar movimientos desde aquí


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'categoria', 'stock_actual',
        'stock_status', 'precio_venta', 'activo', 'visible_venta'
    ]
    list_filter = [
        'categoria', 'activo', 'visible_venta',
        'requiere_vencimiento', 'requiere_lote', 'temperatura_almacenamiento'
    ]
    search_fields = ['codigo', 'nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'valor_inventario', 'margen_ganancia']
    inlines = [LoteProductoInline, MovimientoStockInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'marca', 'modelo')
        }),
        
        ('Control de Inventario', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo')
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta', 'valor_inventario', 'margen_ganancia')
        }),
        ('Control de Calidad', {
            'fields': (
                'requiere_vencimiento', 'requiere_lote', 'dias_vida_util',
                'temperatura_almacenamiento'
            )
        }),
        ('Estado', {
            'fields': ('activo', 'visible_venta')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        if obj.stock_critico:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ Crítico</span>'
            )
        elif obj.stock_actual == 0:
            return format_html(
                '<span style="color: red;">Sin Stock</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">Normal</span>'
            )
    stock_status.short_description = 'Estado Stock'
    
    def save_model(self, request, obj, form, change):
        # Guardar el modelo sin modificar campos adicionales
        super().save_model(request, obj, form, change)


@admin.register(LoteProducto)
class LoteProductoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_lote', 'producto', 'fecha_produccion', 'fecha_vencimiento',
        'cantidad_actual', 'estado_calidad', 'vencimiento_status'
    ]
    list_filter = [
        'estado_calidad', 'fecha_produccion', 'fecha_vencimiento',
        'producto__categoria', 'activo'
    ]
    search_fields = ['numero_lote', 'producto__nombre', 'producto__codigo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'valor_total']
    
    fieldsets = (
        ('Información del Lote', {
            'fields': ('producto', 'numero_lote', 'proveedor')
        }),
        ('Fechas', {
            'fields': ('fecha_produccion', 'fecha_vencimiento')
        }),
        ('Inventario', {
            'fields': ('cantidad_inicial', 'cantidad_actual', 'costo_unitario', 'valor_total')
        }),
        ('Control de Calidad', {
            'fields': ('estado_calidad', 'observaciones')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def vencimiento_status(self, obj):
        if obj.esta_vencido:
            return format_html('<span style="color: red;">Vencido</span>')
        elif obj.proximo_a_vencer:
            return format_html('<span style="color: orange;">Próximo a vencer</span>')
        else:
            return format_html('<span style="color: green;">Vigente</span>')
    vencimiento_status.short_description = 'Estado Vencimiento'
    
    def save_model(self, request, obj, form, change):
        # Guardar el modelo sin modificar campos adicionales
        super().save_model(request, obj, form, change)


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = [
        'fecha_movimiento', 'producto', 'tipo_movimiento', 'cantidad',
        'stock_anterior', 'stock_posterior', 'usuario_responsable'
    ]
    list_filter = [
        'tipo_movimiento', 'fecha_movimiento', 'producto__categoria'
    ]
    search_fields = [
        'producto__nombre', 'producto__codigo', 'razon', 'documento_referencia'
    ]
    readonly_fields = ['fecha_creacion']
    date_hierarchy = 'fecha_movimiento'
    
    fieldsets = (
        ('Movimiento', {
            'fields': ('producto', 'lote', 'tipo_movimiento', 'cantidad')
        }),
        ('Stock', {
            'fields': ('stock_anterior', 'stock_posterior')
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_movimiento', 'razon', 'observaciones',
                'documento_referencia', 'usuario_responsable'
            )
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Guardar el modelo sin modificar campos adicionales
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        # Los movimientos de stock no se pueden eliminar para mantener la trazabilidad
        return False


# Personalización del admin site
admin.site.site_header = "UEB Acopio Bayamo - Gestión de Productos"
admin.site.site_title = "Gestión de Productos"
admin.site.index_title = "Panel de Administración de Productos"
