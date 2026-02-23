from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .models import (
    CategoriaMercancia, Proveedor, 
    Mercancia, LoteMercancia, MovimientoStock
)


class CategoriaMercanciaForm(forms.ModelForm):
    class Meta:
        model = CategoriaMercancia
        fields = ['nombre', 'descripcion', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar 'activa' como True por defecto para nuevas categorías
        if not self.instance.pk:
            self.fields['activa'].initial = True


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'codigo', 'nombre', 'nombre_comercial', 'tipo', 'telefono',
            'email', 'direccion', 'ciudad', 'provincia', 'identificacion',
            'licencia_sanitaria', 'fecha_vencimiento_licencia',
            'activo', 'calificacion'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único del proveedor'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre o razón social'
            }),
            'nombre_comercial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre comercial'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia'
            }),
            'identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'NIT o identificación'
            }),
            'licencia_sanitaria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de licencia sanitaria'
            }),
            'fecha_vencimiento_licencia': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            })
        }

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if identificacion:
            # Verificar que la identificación sea única
            existing = Proveedor.objects.filter(identificacion=identificacion)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Ya existe un proveedor con esta identificación.')
        
        return identificacion


class MercanciaForm(forms.ModelForm):
    class Meta:
        model = Mercancia
        fields = [
            'codigo', 'nombre', 'descripcion', 'categoria',
            'peso_unitario', 'volumen_unitario', 'stock_actual',
            'precio_compra', 'precio_venta',
            'requiere_vencimiento', 'requiere_lote', 'dias_vida_util',
            'temperatura_almacenamiento', 'observaciones',
            'activo', 'visible_venta'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de la mercancía (opcional - se genera automático)'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la mercancía'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la mercancía'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'peso_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Peso en kg'
            }),
            'volumen_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Volumen en litros'
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'placeholder': 'Stock actual'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Precio de compra'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Precio de venta'
            }),
            'requiere_vencimiento': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_lote': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'dias_vida_util': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Días de vida útil'
            }),
            'temperatura_almacenamiento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'visible_venta': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo categorías activas
        self.fields['categoria'].queryset = CategoriaMercancia.objects.filter(activa=True)
        # Hacer el código opcional (se genera automáticamente)
        self.fields['codigo'].required = False
        # Configurar valores por defecto para campos con default en el modelo
        self.fields['stock_actual'].initial = 0
        self.fields['temperatura_almacenamiento'].initial = 'AMBIENTE'

    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get('precio_compra')
        precio_venta = cleaned_data.get('precio_venta')
        requiere_vencimiento = cleaned_data.get('requiere_vencimiento')
        dias_vida_util = cleaned_data.get('dias_vida_util')

        # Validar precios
        if precio_compra is not None and precio_venta is not None:
            if precio_venta < precio_compra:
                raise ValidationError({
                    'precio_venta': 'El precio de venta no puede ser menor que el precio de compra.'
                })

        # Validar días de vida útil si requiere vencimiento
        if requiere_vencimiento and not dias_vida_util:
            raise ValidationError({
                'dias_vida_util': 'Debe especificar los días de vida útil si la mercancía requiere control de vencimiento.'
            })

        return cleaned_data


class LoteMercanciaForm(forms.ModelForm):
    class Meta:
        model = LoteMercancia
        fields = [
            'mercancia', 'numero_lote', 'fecha_produccion', 'fecha_vencimiento',
            'proveedor', 'cantidad_inicial', 'costo_unitario', 'estado_calidad',
            'observaciones', 'activo'
        ]
        widgets = {
            'mercancia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_lote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número del lote'
            }),
            'fecha_produccion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cantidad_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Cantidad inicial'
            }),
            'costo_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Costo por unidad'
            }),
            'estado_calidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones del lote'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo mercancías activas
        self.fields['mercancia'].queryset = Mercancia.objects.filter(activo=True)
        # Filtrar solo proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)

    def clean(self):
        cleaned_data = super().clean()
        mercancia = cleaned_data.get('mercancia')
        fecha_produccion = cleaned_data.get('fecha_produccion')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        numero_lote = cleaned_data.get('numero_lote')

        # Validar fechas
        if fecha_produccion and fecha_vencimiento:
            if fecha_vencimiento <= fecha_produccion:
                raise ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior a la fecha de producción.'
                })

        # Validar fecha de producción no sea futura
        if fecha_produccion and fecha_produccion > timezone.now().date():
            raise ValidationError({
                'fecha_produccion': 'La fecha de producción no puede ser futura.'
            })

        # Validar que la mercancía requiera control de lotes
        if mercancia and not mercancia.requiere_lote:
            raise ValidationError({
                'mercancia': 'Esta mercancía no requiere control por lotes.'
            })

        # Validar fecha de vencimiento si la mercancía lo requiere
        if mercancia and mercancia.requiere_vencimiento and not fecha_vencimiento:
            raise ValidationError({
                'fecha_vencimiento': 'Esta mercancía requiere fecha de vencimiento.'
            })

        # Validar unicidad del lote para la mercancía
        if mercancia and numero_lote:
            existing_lote = LoteMercancia.objects.filter(
                mercancia=mercancia, 
                numero_lote=numero_lote
            )
            if self.instance.pk:
                existing_lote = existing_lote.exclude(pk=self.instance.pk)
            
            if existing_lote.exists():
                raise ValidationError({
                    'numero_lote': f'Ya existe un lote con este número para la mercancía {mercancia.nombre}.'
                })

        return cleaned_data


class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = [
            'mercancia', 'lote', 'tipo_movimiento', 'cantidad',
            'fecha_movimiento', 'razon', 'observaciones',
            'documento_referencia', 'usuario_responsable'
        ]
        widgets = {
            'mercancia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lote': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_movimiento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Cantidad del movimiento'
            }),
            'fecha_movimiento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'razon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Razón del movimiento'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento de referencia'
            }),
            'usuario_responsable': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo mercancías activas
        self.fields['mercancia'].queryset = Mercancia.objects.filter(activo=True)
        # El campo lote se filtrará dinámicamente con JavaScript

    def clean(self):
        cleaned_data = super().clean()
        mercancia = cleaned_data.get('mercancia')
        lote = cleaned_data.get('lote')
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        cantidad = cleaned_data.get('cantidad')

        # Validar que el lote pertenezca a la mercancía
        if mercancia and lote and lote.mercancia != mercancia:
            raise ValidationError({
                'lote': 'El lote seleccionado no pertenece a la mercancía elegida.'
            })

        # Validar cantidad para salidas
        if tipo_movimiento in ['SALIDA', 'AJUSTE_NEGATIVO', 'TRANSFERENCIA_SALIDA', 'MERMA', 'VENCIMIENTO']:
            if mercancia and cantidad:
                if lote:
                    # Verificar stock del lote
                    if cantidad > lote.cantidad_actual:
                        raise ValidationError({
                            'cantidad': f'No hay suficiente stock en el lote. Disponible: {lote.cantidad_actual}'
                        })
                else:
                    # Verificar stock general de la mercancía
                    if cantidad > mercancia.stock_actual:
                        raise ValidationError({
                            'cantidad': f'No hay suficiente stock de la mercancía. Disponible: {mercancia.stock_actual}'
                        })

        return cleaned_data


class BusquedaMercanciaForm(forms.Form):
    """Formulario para búsqueda y filtrado de mercancías"""
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nombre o descripción...'
        })
    )
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaMercancia.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado_stock = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('sin_stock', 'Sin Stock'),
            ('normal', 'Con Stock'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    activo = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('true', 'Activos'),
            ('false', 'Inactivos'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
