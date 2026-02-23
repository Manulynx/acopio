from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Inmueble, TipoInmueble, ImagenInmueble, 
    CaracteristicaAdicional, InmuebleCaracteristica, MantenimientoInmueble
)


class TipoInmuebleForm(forms.ModelForm):
    class Meta:
        model = TipoInmueble
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de inmueble'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': 'checked'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar 'activo' como True por defecto para nuevos tipos
        if not self.instance.pk:
            self.fields['activo'].initial = True


class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = [
            'codigo', 'nombre', 'tipo', 'area_total', 'area_util', 'altura',
            'capacidad_carga', 'numero_ambientes', 'numero_banos', 'numero_estacionamientos',
            'direccion', 'ciudad', 'provincia', 'codigo_postal',
            'coordenadas_lat', 'coordenadas_lng', 'tipo_uso', 'condicion', 'ano_construccion',
            'tiene_electricidad', 'tiene_agua', 'tiene_gas', 'tiene_internet',
            'tiene_seguridad', 'tiene_vigilancia_24h', 'tiene_camaras', 'tiene_alarma',
            'tiene_extintor', 'tiene_rociadores', 'tiene_carga_descarga',
            'tiene_montacargas', 'tiene_rampa',
            'precio_arriendo_mensual', 'gastos_comunes', 'deposito_garantia', 'dias_preaviso',
            'estado', 'fecha_disponibilidad', 'descripcion', 'observaciones',
            'activo', 'destacado'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código (se genera automático si se deja vacío)'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del inmueble'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'area_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Área total en m²'
            }),
            'area_util': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Área útil en m²'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Altura en metros'
            }),
            'capacidad_carga': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Capacidad en toneladas'
            }),
            'numero_ambientes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'numero_banos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'numero_estacionamientos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
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
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'coordenadas_lat': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'Latitud'
            }),
            'coordenadas_lng': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'Longitud'
            }),
            'tipo_uso': forms.Select(attrs={
                'class': 'form-select'
            }),
            'condicion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ano_construccion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Año de construcción'
            }),
            'tiene_electricidad': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_agua': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_gas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_internet': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_seguridad': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_vigilancia_24h': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_camaras': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_alarma': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_extintor': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_rociadores': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_carga_descarga': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_montacargas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tiene_rampa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'precio_arriendo_mensual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Precio de arriendo mensual'
            }),
            'gastos_comunes': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Gastos comunes'
            }),
            'deposito_garantia': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Depósito de garantía'
            }),
            'dias_preaviso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_disponibilidad': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del inmueble'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones internas'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'destacado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo tipos activos
        self.fields['tipo'].queryset = TipoInmueble.objects.filter(activo=True)
        # Hacer el código opcional (se genera automáticamente)
        self.fields['codigo'].required = False
        # Configurar valores por defecto para campos con default en el modelo
        self.fields['numero_ambientes'].initial = 1
        self.fields['numero_banos'].initial = 0
        self.fields['numero_estacionamientos'].initial = 0
        self.fields['tipo_uso'].initial = 'ALMACENAMIENTO'
        self.fields['condicion'].initial = 'BUENA'
        self.fields['gastos_comunes'].initial = 0
        self.fields['dias_preaviso'].initial = 30
        self.fields['estado'].initial = 'DISPONIBLE'

    def clean(self):
        cleaned_data = super().clean()
        area_total = cleaned_data.get('area_total')
        area_util = cleaned_data.get('area_util')

        # Validar que área útil no sea mayor que área total
        if area_total and area_util and area_util > area_total:
            raise ValidationError({
                'area_util': 'El área útil no puede ser mayor que el área total.'
            })

        return cleaned_data


class ImagenInmuebleForm(forms.ModelForm):
    class Meta:
        model = ImagenInmueble
        fields = ['inmueble', 'imagen', 'titulo', 'es_principal', 'orden']
        widgets = {
            'inmueble': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la imagen'
            }),
            'es_principal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }


class CaracteristicaAdicionalForm(forms.ModelForm):
    class Meta:
        model = CaracteristicaAdicional
        fields = ['nombre', 'descripcion', 'icono', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la característica'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clase de icono FontAwesome (ej: fa-wifi)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MantenimientoInmuebleForm(forms.ModelForm):
    class Meta:
        model = MantenimientoInmueble
        fields = [
            'inmueble', 'tipo', 'descripcion', 'fecha_programada',
            'fecha_realizacion', 'costo', 'proveedor', 'estado', 'observaciones'
        ]
        widgets = {
            'inmueble': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del mantenimiento'
            }),
            'fecha_programada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_realizacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Costo del mantenimiento'
            }),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Proveedor que realiza el mantenimiento'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones'
            })
        }


class BusquedaInmuebleForm(forms.Form):
    """Formulario para búsqueda y filtrado de inmuebles"""
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nombre o dirección...'
        })
    )
    
    tipo = forms.ModelChoiceField(
        queryset=TipoInmueble.objects.filter(activo=True),
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Inmueble.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ciudad'
        })
    )
    
    precio_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Precio mínimo'
        })
    )
    
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Precio máximo'
        })
    )
    
    area_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Área mínima (m²)'
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
