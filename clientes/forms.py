from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, TipoCliente, ContactoCliente, DireccionCliente


class TipoClienteForm(forms.ModelForm):
    class Meta:
        model = TipoCliente
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de cliente'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar 'activo' como True por defecto para nuevos tipos
        if not self.instance.pk:
            self.fields['activo'].initial = True


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'codigo', 'identificacion', 'razon_social', 'nombre_comercial', 'tipo_cliente',
            'tipo_empresa', 'telefono_principal', 'telefono_secundario', 'email', 'sitio_web',
            'direccion', 'ciudad', 'provincia', 'codigo_postal', 'pais',
            'nombre_contacto', 'cargo_contacto', 'telefono_contacto', 'email_contacto',
            'descuento_porcentaje', 'estado', 'calificacion', 'observaciones', 'notas_internas', 'activo'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código (se genera automático si se deja vacío)'
            }),
            'identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de identificación'
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Razón social o nombre de la empresa'
            }),
            'nombre_comercial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre comercial'
            }),
            'tipo_cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_empresa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'telefono_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono principal'
            }),
            'telefono_secundario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono secundario (opcional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@empresa.com'
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.empresa.com'
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
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            }),
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto principal'
            }),
            'cargo_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo del contacto'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del contacto'
            }),
            'email_contacto': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@contacto.com'
            }),
            'descuento_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Porcentaje de descuento'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre el cliente'
            }),
            'notas_internas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas de uso interno'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo tipos de clientes activos
        self.fields['tipo_cliente'].queryset = TipoCliente.objects.filter(activo=True)
        self.fields['tipo_cliente'].required = False
        # Hacer el código opcional (se genera automáticamente)
        self.fields['codigo'].required = False
        # Configurar valores por defecto para campos opcionales
        self.fields['pais'].initial = 'Ecuador'
        self.fields['descuento_porcentaje'].initial = 0
        self.fields['estado'].initial = 'ACTIVO'
        self.fields['calificacion'].initial = 5
        self.fields['tipo_empresa'].initial = 'PRIVADA'

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if identificacion:
            # Verificar que la identificación sea única
            existing = Cliente.objects.filter(identificacion=identificacion)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Ya existe un cliente con esta identificación.')
        
        return identificacion

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar que el email sea único
            existing = Cliente.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Ya existe un cliente con este email.')
        
        return email


class ContactoClienteForm(forms.ModelForm):
    class Meta:
        model = ContactoCliente
        fields = [
            'cliente', 'nombre', 'cargo', 'telefono', 'email',
            'es_principal', 'observaciones', 'activo'
        ]
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo en la empresa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@contacto.com'
            }),
            'es_principal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)


class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        fields = [
            'cliente', 'tipo', 'nombre_referencia', 'direccion',
            'ciudad', 'provincia', 'codigo_postal', 'telefono',
            'persona_recibe', 'es_principal', 'observaciones', 'activo'
        ]
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nombre_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bodega Central, Sucursal Norte'
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
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'persona_recibe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Persona que recibe'
            }),
            'es_principal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)


class BusquedaClienteForm(forms.Form):
    """Formulario para búsqueda y filtrado de clientes"""
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nombre, identificación o email...'
        })
    )
    
    tipo_cliente = forms.ModelChoiceField(
        queryset=TipoCliente.objects.filter(activo=True),
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Cliente.ESTADO_CHOICES,
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
