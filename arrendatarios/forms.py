from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    TipoArrendatario,
    Arrendatario,
    DocumentoArrendatario,
    ContratoArriendo
)


class TipoArrendatarioForm(forms.ModelForm):
    """Formulario para tipos de arrendatarios"""
    
    class Meta:
        model = TipoArrendatario
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Persona Natural, Empresa, etc.'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de arrendatario'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'activo': 'Activo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar 'activo' como True por defecto para nuevos tipos
        if not self.instance.pk:
            self.fields['activo'].initial = True


class ArrendatarioForm(forms.ModelForm):
    """Formulario para arrendatarios"""
    
    class Meta:
        model = Arrendatario
        fields = [
            'codigo', 'tipo_persona', 'tipo_arrendatario',
            # Persona Natural
            'nombres', 'apellidos',
            # Persona Jurídica
            'razon_social', 'nombre_comercial',
            # Identificación
            'identificacion',
            # Contacto
            'telefono_principal', 'telefono_secundario',
            'email', 'email_secundario',
            # Dirección
            'direccion', 'ciudad', 'provincia', 'codigo_postal', 'pais',
            # Información laboral/empresarial
            'ocupacion', 'lugar_trabajo', 'telefono_trabajo', 'ingresos_mensuales',
            # Referencia personal
            'referencia_nombre', 'referencia_telefono', 'referencia_relacion',
            # Contacto de emergencia
            'emergencia_nombre', 'emergencia_telefono', 'emergencia_relacion',
            # Representante legal
            'representante_nombre', 'representante_identificacion',
            'representante_telefono', 'representante_email',
            # Estado
            'estado', 'calificacion', 'historial_crediticio',
            # Observaciones
            'observaciones', 'notas_internas',
            'activo', 'fecha_registro',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dejar vacío para generar automáticamente'
            }),
            'tipo_persona': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_persona'
            }),
            'tipo_arrendatario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control persona-natural',
                'placeholder': 'Nombres completos'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control persona-natural',
                'placeholder': 'Apellidos completos'
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control persona-juridica',
                'placeholder': 'Razón social de la empresa'
            }),
            'nombre_comercial': forms.TextInput(attrs={
                'class': 'form-control persona-juridica',
                'placeholder': 'Nombre comercial'
            }),
            'identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cédula, RUC, Pasaporte, etc.'
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
                'placeholder': 'correo@ejemplo.com'
            }),
            'email_secundario': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo2@ejemplo.com (opcional)'
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
            'ocupacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ocupación o actividad económica'
            }),
            'lugar_trabajo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de trabajo o empresa'
            }),
            'telefono_trabajo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del trabajo'
            }),
            'ingresos_mensuales': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'referencia_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la referencia personal'
            }),
            'referencia_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de la referencia'
            }),
            'referencia_relacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Familiar, Amigo, etc.'
            }),
            'emergencia_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto de emergencia'
            }),
            'emergencia_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de emergencia'
            }),
            'emergencia_relacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relación con el contacto'
            }),
            'representante_nombre': forms.TextInput(attrs={
                'class': 'form-control persona-juridica',
                'placeholder': 'Nombre del representante legal'
            }),
            'representante_identificacion': forms.TextInput(attrs={
                'class': 'form-control persona-juridica',
                'placeholder': 'Cédula del representante'
            }),
            'representante_telefono': forms.TextInput(attrs={
                'class': 'form-control persona-juridica',
                'placeholder': 'Teléfono del representante'
            }),
            'representante_email': forms.EmailInput(attrs={
                'class': 'form-control persona-juridica',
                'placeholder': 'Email del representante'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'historial_crediticio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Información sobre historial crediticio'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales'
            }),
            'notas_internas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas de uso interno'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fecha_registro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'codigo': 'Código',
            'tipo_persona': 'Tipo de Persona',
            'tipo_arrendatario': 'Tipo de Arrendatario',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'razon_social': 'Razón Social',
            'nombre_comercial': 'Nombre Comercial',
            'identificacion': 'Identificación',
            'telefono_principal': 'Teléfono Principal',
            'telefono_secundario': 'Teléfono Secundario',
            'email': 'Email',
            'email_secundario': 'Email Secundario',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'provincia': 'Provincia',
            'codigo_postal': 'Código Postal',
            'pais': 'País',
            'ocupacion': 'Ocupación',
            'lugar_trabajo': 'Lugar de Trabajo',
            'telefono_trabajo': 'Teléfono del Trabajo',
            'ingresos_mensuales': 'Ingresos Mensuales',
            'referencia_nombre': 'Referencia - Nombre',
            'referencia_telefono': 'Referencia - Teléfono',
            'referencia_relacion': 'Referencia - Relación',
            'emergencia_nombre': 'Emergencia - Nombre',
            'emergencia_telefono': 'Emergencia - Teléfono',
            'emergencia_relacion': 'Emergencia - Relación',
            'representante_nombre': 'Representante Legal - Nombre',
            'representante_identificacion': 'Representante Legal - Identificación',
            'representante_telefono': 'Representante Legal - Teléfono',
            'representante_email': 'Representante Legal - Email',
            'estado': 'Estado',
            'calificacion': 'Calificación (1-5)',
            'historial_crediticio': 'Historial Crediticio',
            'observaciones': 'Observaciones',
            'notas_internas': 'Notas Internas',
            'activo': 'Activo',
            'fecha_registro': 'Fecha de Registro',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el código opcional
        self.fields['codigo'].required = False
        # Configurar valores por defecto para campos con default en el modelo
        self.fields['pais'].initial = 'Ecuador'
        self.fields['estado'].initial = 'ACTIVO'
        self.fields['calificacion'].initial = 5
        # Configurar fecha_registro con fecha actual
        from django.utils import timezone
        self.fields['fecha_registro'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_persona = cleaned_data.get('tipo_persona')
        
        # Validar campos según tipo de persona
        if tipo_persona == 'NATURAL':
            if not cleaned_data.get('nombres') and not cleaned_data.get('apellidos'):
                raise ValidationError(
                    'Debe proporcionar al menos nombres o apellidos para persona natural.'
                )
        elif tipo_persona == 'JURIDICA':
            if not cleaned_data.get('razon_social'):
                raise ValidationError(
                    'Debe proporcionar la razón social para persona jurídica.'
                )
        
        return cleaned_data


class DocumentoArrendatarioForm(forms.ModelForm):
    """Formulario para documentos de arrendatarios"""
    
    class Meta:
        model = DocumentoArrendatario
        fields = [
            'tipo', 'titulo', 'archivo',
            'fecha_emision', 'fecha_vencimiento',
            'observaciones'
        ]
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título o descripción del documento'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'fecha_emision': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre el documento'
            }),
        }
        labels = {
            'tipo': 'Tipo de Documento',
            'titulo': 'Título',
            'archivo': 'Archivo',
            'fecha_emision': 'Fecha de Emisión',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'observaciones': 'Observaciones',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_emision = cleaned_data.get('fecha_emision')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        # Validar que la fecha de vencimiento sea posterior a la de emisión
        if fecha_emision and fecha_vencimiento:
            if fecha_vencimiento <= fecha_emision:
                raise ValidationError(
                    'La fecha de vencimiento debe ser posterior a la fecha de emisión.'
                )
        
        return cleaned_data


class ContratoArriendoForm(forms.ModelForm):
    """Formulario para contratos de arriendo"""
    
    class Meta:
        model = ContratoArriendo
        fields = [
            'numero_contrato', 'arrendatario', 'inmueble',
            'fecha_inicio', 'fecha_fin',
            'valor_arriendo', 'valor_deposito', 'gastos_comunes',
            'tipo_pago', 'dia_pago',
            'permite_incremento', 'porcentaje_incremento',
            'incluye_servicios', 'servicios_incluidos',
            'permite_subarriendo', 'requiere_seguro',
            'clausulas_especiales',
            'estado', 'fecha_firma', 'archivo_contrato',
            'observaciones'
        ]
        widgets = {
            'numero_contrato': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dejar vacío para generar automáticamente'
            }),
            'arrendatario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'inmueble': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_arriendo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'valor_deposito': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'gastos_comunes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'tipo_pago': forms.Select(attrs={
                'class': 'form-select'
            }),
            'dia_pago': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '31'
            }),
            'permite_incremento': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'porcentaje_incremento': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'incluye_servicios': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicios_incluidos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalle de servicios incluidos'
            }),
            'permite_subarriendo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_seguro': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'clausulas_especiales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cláusulas especiales del contrato'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_firma': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'archivo_contrato': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales'
            }),
        }
        labels = {
            'numero_contrato': 'Número de Contrato',
            'arrendatario': 'Arrendatario',
            'inmueble': 'Inmueble',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'valor_arriendo': 'Valor del Arriendo',
            'valor_deposito': 'Valor del Depósito',
            'gastos_comunes': 'Gastos Comunes',
            'tipo_pago': 'Tipo de Pago',
            'dia_pago': 'Día de Pago',
            'permite_incremento': 'Permite Incremento Anual',
            'porcentaje_incremento': 'Porcentaje de Incremento (%)',
            'incluye_servicios': 'Incluye Servicios',
            'servicios_incluidos': 'Servicios Incluidos',
            'permite_subarriendo': 'Permite Subarriendo',
            'requiere_seguro': 'Requiere Seguro',
            'clausulas_especiales': 'Cláusulas Especiales',
            'estado': 'Estado',
            'fecha_firma': 'Fecha de Firma',
            'archivo_contrato': 'Archivo del Contrato',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el número de contrato opcional
        self.fields['numero_contrato'].required = False
        
        # Filtrar solo arrendatarios activos y que pueden arrendar
        self.fields['arrendatario'].queryset = Arrendatario.objects.filter(
            activo=True
        ).exclude(
            estado__in=['VETADO', 'SUSPENDIDO']
        )
        
        # Filtrar solo inmuebles disponibles para arrendar
        from inmuebles.models import Inmueble
        self.fields['inmueble'].queryset = Inmueble.objects.filter(
            activo=True,
            estado='DISPONIBLE'
        )
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        fecha_firma = cleaned_data.get('fecha_firma')
        arrendatario = cleaned_data.get('arrendatario')
        inmueble = cleaned_data.get('inmueble')
        
        # Validar que la fecha de fin sea posterior a la de inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise ValidationError(
                    'La fecha de finalización debe ser posterior a la fecha de inicio.'
                )
        
        # Validar que la fecha de firma no sea posterior a la fecha de inicio
        if fecha_firma and fecha_inicio:
            if fecha_firma > fecha_inicio:
                raise ValidationError(
                    'La fecha de firma no puede ser posterior a la fecha de inicio del contrato.'
                )
        
        # Validar que el arrendatario pueda arrendar
        if arrendatario and not arrendatario.puede_arrendar:
            raise ValidationError(
                f'El arrendatario {arrendatario.nombre_completo} no puede arrendar debido a su estado.'
            )
        
        # Validar que el inmueble esté disponible
        if inmueble and inmueble.estado != 'DISPONIBLE':
            raise ValidationError(
                f'El inmueble {inmueble.nombre} no está disponible para arriendo.'
            )
        
        return cleaned_data


class BusquedaArrendatarioForm(forms.Form):
    """Formulario para buscar arrendatarios"""
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nombre, identificación...'
        })
    )
    
    tipo_persona = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(Arrendatario.TIPO_PERSONA_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(Arrendatario.ESTADO_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tipo_arrendatario = forms.ModelChoiceField(
        required=False,
        queryset=TipoArrendatario.objects.filter(activo=True),
        empty_label='Todos',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    solo_activos = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Solo arrendatarios activos'
    )


class BusquedaContratoForm(forms.Form):
    """Formulario para buscar contratos"""
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número de contrato, arrendatario...'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(ContratoArriendo.ESTADO_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    arrendatario = forms.ModelChoiceField(
        required=False,
        queryset=Arrendatario.objects.filter(activo=True),
        empty_label='Todos',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
