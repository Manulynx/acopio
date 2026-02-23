from django.contrib import admin
from .models import Venta, DetalleVentaProducto, DetalleVentaMercancia


class DetalleVentaProductoInline(admin.TabularInline):
    model = DetalleVentaProducto
    extra = 0
    min_num = 0
    autocomplete_fields = ['producto', 'lote']
    fields = ['producto', 'lote', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


class DetalleVentaMercanciaInline(admin.TabularInline):
    model = DetalleVentaMercancia
    extra = 0
    min_num = 0
    autocomplete_fields = ['mercancia', 'lote']
    fields = ['mercancia', 'lote', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'cliente', 'fecha_venta', 'total', 'estado']
    list_filter = ['estado', 'fecha_venta', 'cliente']
    search_fields = ['codigo', 'cliente__nombre', 'notas']
    readonly_fields = ['codigo', 'subtotal', 'impuestos', 'total']
    autocomplete_fields = ['cliente']
    date_hierarchy = 'fecha_venta'
    
    fieldsets = [
        ('Información Básica', {
            'fields': ('codigo', 'fecha_venta', 'cliente', 'estado')
        }),
        ('Totales', {
            'fields': ('subtotal', 'impuestos', 'total')
        }),
        ('Observaciones', {
            'fields': ('notas',)
        }),
    ]
    
    inlines = [DetalleVentaProductoInline, DetalleVentaMercanciaInline]
    
    def save_model(self, request, obj, form, change):
        """Guarda el usuario que crea la venta"""
        if not change:  # Si es una nueva venta
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Recalcula totales después de guardar los detalles"""
        super().save_formset(request, form, formset, change)
        if formset.model in [DetalleVentaProducto, DetalleVentaMercancia]:
            form.instance.calcular_total()
