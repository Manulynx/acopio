from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from inmuebles.models import Inmueble

User = get_user_model()


class TipoArrendatario(models.Model):
    """Tipos de arrendatarios (Persona Natural, Empresa, etc.)"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Arrendatario"
        verbose_name_plural = "Tipos de Arrendatarios"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Arrendatario(models.Model):
    """Modelo para personas o empresas que alquilan inmuebles"""
    
    TIPO_PERSONA_CHOICES = [
        ('NATURAL', 'Persona Natural'),
        ('JURIDICA', 'Persona Jurídica'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MOROSO', 'Moroso'),
        ('SUSPENDIDO', 'Suspendido'),
        ('VETADO', 'Vetado'),
    ]
    
    # Identificación
    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Código único del arrendatario"
    )
    
    tipo_persona = models.CharField(
        max_length=20,
        choices=TIPO_PERSONA_CHOICES,
        default='NATURAL'
    )
    
    tipo_arrendatario = models.ForeignKey(
        TipoArrendatario,
        on_delete=models.PROTECT,
        related_name='arrendatarios',
        null=True,
        blank=True
    )
    
    # Información básica - Persona Natural
    nombres = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombres completos (para persona natural)"
    )
    
    apellidos = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Apellidos completos (para persona natural)"
    )
    
    # Información básica - Persona Jurídica
    razon_social = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Razón social (para persona jurídica)"
    )
    
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre comercial"
    )
    
    # Documentación
    identificacion = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número de identificación (cédula, RUC, pasaporte, etc.)"
    )
    
    # Información de contacto
    telefono_principal = models.CharField(max_length=20)
    telefono_secundario = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    email_secundario = models.EmailField(blank=True, null=True)
    
    # Dirección personal/fiscal
    direccion = models.TextField(help_text="Dirección de domicilio o fiscal")
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Ecuador')
    
    # Información laboral/empresarial
    ocupacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Ocupación o actividad económica"
    )
    
    lugar_trabajo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Lugar de trabajo o empresa"
    )
    
    telefono_trabajo = models.CharField(max_length=20, blank=True, null=True)
    
    ingresos_mensuales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Ingresos mensuales aproximados"
    )
    
    # Referencia personal
    referencia_nombre = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre de referencia personal"
    )
    
    referencia_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    referencia_relacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Relación con la referencia"
    )
    
    # Contacto de emergencia
    emergencia_nombre = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre del contacto de emergencia"
    )
    
    emergencia_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    emergencia_relacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Relación con el contacto de emergencia"
    )
    
    # Representante legal (para personas jurídicas)
    representante_nombre = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nombre del representante legal"
    )
    
    representante_identificacion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Identificación del representante legal"
    )
    
    representante_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    representante_email = models.EmailField(blank=True, null=True)
    
    # Estado y calificación
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO'
    )
    
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        help_text="Calificación como arrendatario (1-5 estrellas)"
    )
    
    historial_crediticio = models.TextField(
        blank=True,
        null=True,
        help_text="Notas sobre historial crediticio"
    )
    
    # Observaciones
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones generales"
    )
    
    notas_internas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas de uso interno"
    )
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateField(
        default=timezone.now,
        help_text="Fecha de registro como arrendatario"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='arrendatarios_creados'
    )
    
    class Meta:
        verbose_name = "Arrendatario"
        verbose_name_plural = "Arrendatarios"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['identificacion']),
            models.Index(fields=['estado', 'activo']),
            models.Index(fields=['tipo_persona']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre_completo}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo según el tipo de persona"""
        if self.tipo_persona == 'NATURAL':
            return f"{self.nombres} {self.apellidos}".strip() if self.nombres and self.apellidos else self.nombres or self.apellidos or "Sin nombre"
        else:
            return self.razon_social or self.nombre_comercial or "Sin nombre"
    
    @property
    def tiene_arriendos_activos(self):
        """Verifica si tiene arriendos activos"""
        return self.contratos.filter(
            estado__in=['VIGENTE', 'RENOVADO']
        ).exists()
    
    @property
    def total_arriendos(self):
        """Cuenta el total de arriendos"""
        return self.contratos.count()
    
    @property
    def es_moroso(self):
        """Verifica si el arrendatario está moroso"""
        return self.estado == 'MOROSO'
    
    @property
    def puede_arrendar(self):
        """Verifica si puede arrendar inmuebles"""
        return self.activo and self.estado not in ['VETADO', 'SUSPENDIDO']
    
    def save(self, *args, **kwargs):
        """Validaciones adicionales al guardar"""
        # Generar código automático si no se proporciona
        if not self.codigo:
            self.codigo = self.generar_codigo()
        
        super().save(*args, **kwargs)
    
    def generar_codigo(self):
        """Genera un código automático para el arrendatario"""
        # Prefijo ARR + 6 números
        ultimo_numero = Arrendatario.objects.count() + 1
        return f"ARR{str(ultimo_numero).zfill(6)}"


class DocumentoArrendatario(models.Model):
    """Documentos del arrendatario"""
    
    TIPO_DOCUMENTO_CHOICES = [
        ('CEDULA', 'Cédula de Identidad'),
        ('PASAPORTE', 'Pasaporte'),
        ('RUC', 'RUC'),
        ('CONSTANCIA_TRABAJO', 'Constancia de Trabajo'),
        ('CARTA_RECOMENDACION', 'Carta de Recomendación'),
        ('CERTIFICADO_BANCARIO', 'Certificado Bancario'),
        ('CONTRATO_ANTERIOR', 'Contrato de Arriendo Anterior'),
        ('OTRO', 'Otro'),
    ]
    
    arrendatario = models.ForeignKey(
        Arrendatario,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_DOCUMENTO_CHOICES
    )
    
    titulo = models.CharField(
        max_length=200,
        help_text="Título o descripción del documento"
    )
    
    archivo = models.FileField(
        upload_to='arrendatarios/documentos/%Y/%m/',
        help_text="Archivo del documento"
    )
    
    fecha_emision = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de emisión del documento"
    )
    
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de vencimiento del documento"
    )
    
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos_arrendatarios_subidos'
    )
    
    class Meta:
        verbose_name = "Documento de Arrendatario"
        verbose_name_plural = "Documentos de Arrendatarios"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.arrendatario.nombre_completo} - {self.titulo}"
    
    @property
    def esta_vencido(self):
        """Verifica si el documento está vencido"""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < timezone.now().date()


class ContratoArriendo(models.Model):
    """Contratos de arriendo entre arrendatarios e inmuebles"""
    
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('VIGENTE', 'Vigente'),
        ('RENOVADO', 'Renovado'),
        ('FINALIZADO', 'Finalizado'),
        ('RESCINDIDO', 'Rescindido'),
        ('VENCIDO', 'Vencido'),
    ]
    
    TIPO_PAGO_CHOICES = [
        ('MENSUAL', 'Mensual'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
    ]
    
    # Identificación
    numero_contrato = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número único del contrato"
    )
    
    # Partes del contrato
    arrendatario = models.ForeignKey(
        Arrendatario,
        on_delete=models.PROTECT,
        related_name='contratos'
    )
    
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.PROTECT,
        related_name='contratos'
    )
    
    # Fechas del contrato
    fecha_inicio = models.DateField(help_text="Fecha de inicio del contrato")
    fecha_fin = models.DateField(help_text="Fecha de finalización del contrato")
    
    # Condiciones económicas
    valor_arriendo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Valor mensual del arriendo"
    )
    
    valor_deposito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Valor del depósito de garantía"
    )
    
    gastos_comunes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Gastos comunes mensuales"
    )
    
    tipo_pago = models.CharField(
        max_length=20,
        choices=TIPO_PAGO_CHOICES,
        default='MENSUAL'
    )
    
    dia_pago = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        default=5,
        help_text="Día del mes para realizar el pago"
    )
    
    # Incremento de arriendo
    permite_incremento = models.BooleanField(
        default=True,
        help_text="¿Se permite incremento anual del arriendo?"
    )
    
    porcentaje_incremento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Porcentaje de incremento anual"
    )
    
    # Condiciones adicionales
    incluye_servicios = models.BooleanField(
        default=False,
        help_text="¿El arriendo incluye servicios básicos?"
    )
    
    servicios_incluidos = models.TextField(
        blank=True,
        null=True,
        help_text="Detalle de servicios incluidos"
    )
    
    permite_subarriendo = models.BooleanField(
        default=False,
        help_text="¿Se permite subarrendar?"
    )
    
    requiere_seguro = models.BooleanField(
        default=False,
        help_text="¿Se requiere seguro del inmueble?"
    )
    
    # Cláusulas especiales
    clausulas_especiales = models.TextField(
        blank=True,
        null=True,
        help_text="Cláusulas especiales del contrato"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='BORRADOR'
    )
    
    fecha_firma = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de firma del contrato"
    )
    
    archivo_contrato = models.FileField(
        upload_to='contratos/%Y/%m/',
        blank=True,
        null=True,
        help_text="Archivo PDF del contrato firmado"
    )
    
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contratos_creados'
    )
    
    class Meta:
        verbose_name = "Contrato de Arriendo"
        verbose_name_plural = "Contratos de Arriendo"
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['numero_contrato']),
            models.Index(fields=['arrendatario', 'estado']),
            models.Index(fields=['inmueble', 'estado']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.numero_contrato} - {self.arrendatario.nombre_completo} - {self.inmueble.nombre}"
    
    @property
    def esta_vigente(self):
        """Verifica si el contrato está vigente"""
        hoy = timezone.now().date()
        return self.estado in ['VIGENTE', 'RENOVADO'] and self.fecha_inicio <= hoy <= self.fecha_fin
    
    @property
    def dias_restantes(self):
        """Calcula días restantes del contrato"""
        if not self.fecha_fin:
            return None
        delta = self.fecha_fin - timezone.now().date()
        return delta.days if delta.days > 0 else 0
    
    @property
    def esta_por_vencer(self):
        """Verifica si está por vencer (menos de 30 días)"""
        dias = self.dias_restantes
        return dias is not None and 0 < dias <= 30
    
    @property
    def duracion_meses(self):
        """Calcula la duración en meses"""
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.days // 30
        return 0
    
    @property
    def costo_total_mensual(self):
        """Calcula el costo total mensual (arriendo + gastos comunes)"""
        return self.valor_arriendo + self.gastos_comunes
    
    def save(self, *args, **kwargs):
        """Validaciones adicionales al guardar"""
        # Generar número de contrato automático si no se proporciona
        if not self.numero_contrato:
            self.numero_contrato = self.generar_numero_contrato()
        
        # Validar fechas
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de finalización debe ser posterior a la fecha de inicio")
        
        super().save(*args, **kwargs)
    
    def generar_numero_contrato(self):
        """Genera un número de contrato automático"""
        from django.utils.crypto import get_random_string
        import datetime
        
        # Formato: CTR-AÑO-NÚMERO
        anio = datetime.datetime.now().year
        ultimo_numero = ContratoArriendo.objects.filter(
            numero_contrato__startswith=f'CTR-{anio}'
        ).count() + 1
        
        return f"CTR-{anio}-{str(ultimo_numero).zfill(4)}"
