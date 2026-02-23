from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVentaProducto, DetalleVentaMercancia

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['fecha_venta', 'cliente', 'estado', 'notas']
        widgets = {
            'fecha_venta': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

DetalleVentaProductoFormSet = inlineformset_factory(
    Venta,
    DetalleVentaProducto,
    fields=['producto', 'lote', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
)

DetalleVentaMercanciaFormSet = inlineformset_factory(
    Venta,
    DetalleVentaMercancia,
    fields=['mercancia', 'lote', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
)
