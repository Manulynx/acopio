from django.contrib import admin
from .models import (
    TipoArrendatario,
    Arrendatario,
    DocumentoArrendatario,
    ContratoArriendo
)


@admin.register(TipoArrendatario)
class TipoArrendatarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)


class DocumentoArrendatarioInline(admin.TabularInline):
    model = DocumentoArrendatario
    extra = 0
    fields = ('tipo', 'titulo', 'archivo', 'fecha_emision', 'fecha_vencimiento')
    readonly_fields = ('fecha_creacion',)


class ContratoArriendoInline(admin.TabularInline):
    model = ContratoArriendo
    extra = 0
    fields = ('numero_contrato', 'inmueble', 'fecha_inicio', 'fecha_fin', 'valor_arriendo', 'estado')
    readonly_fields = ('numero_contrato',)


@admin.register(Arrendatario)
class ArrendatarioAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'get_nombre_completo',
        'tipo_persona',
        'identificacion',
        'telefono_principal',
        'email',
        'estado',
        'activo'
    )
    list_filter = (
        'tipo_persona',
        'estado',
        'activo',
        'tipo_arrendatario',
        'fecha_registro'
    )
    search_fields = (
        'codigo',
        'nombres',
        'apellidos',
        'razon_social',
        'identificacion',
        'email',
        'telefono_principal'
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'creado_por')
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'codigo',
                'tipo_persona',
                'tipo_arrendatario',
                'identificacion'
            )
        }),
        ('Información - Persona Natural', {
            'fields': ('nombres', 'apellidos'),
            'classes': ('collapse',)
        }),
        ('Información - Persona Jurídica', {
            'fields': ('razon_social', 'nombre_comercial'),
            'classes': ('collapse',)
        }),
        ('Contacto', {
            'fields': (
                'telefono_principal',
                'telefono_secundario',
                'email',
                'email_secundario'
            )
        }),
        ('Dirección', {
            'fields': (
                'direccion',
                'ciudad',
                'provincia',
                'codigo_postal',
                'pais'
            )
        }),
        ('Información Laboral', {
            'fields': (
                'ocupacion',
                'lugar_trabajo',
                'telefono_trabajo',
                'ingresos_mensuales'
            ),
            'classes': ('collapse',)
        }),
        ('Referencia Personal', {
            'fields': (
                'referencia_nombre',
                'referencia_telefono',
                'referencia_relacion'
            ),
            'classes': ('collapse',)
        }),
        ('Contacto de Emergencia', {
            'fields': (
                'emergencia_nombre',
                'emergencia_telefono',
                'emergencia_relacion'
            ),
            'classes': ('collapse',)
        }),
        ('Representante Legal', {
            'fields': (
                'representante_nombre',
                'representante_identificacion',
                'representante_telefono',
                'representante_email'
            ),
            'classes': ('collapse',)
        }),
        ('Estado y Calificación', {
            'fields': (
                'estado',
                'calificacion',
                'historial_crediticio'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'notas_internas'),
            'classes': ('collapse',)
        }),
        ('Control', {
            'fields': (
                'activo',
                'fecha_registro',
                'fecha_creacion',
                'fecha_actualizacion',
                'creado_por'
            )
        }),
    )
    
    inlines = [DocumentoArrendatarioInline, ContratoArriendoInline]
    
    def get_nombre_completo(self, obj):
        return obj.nombre_completo
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(DocumentoArrendatario)
class DocumentoArrendatarioAdmin(admin.ModelAdmin):
    list_display = (
        'arrendatario',
        'tipo',
        'titulo',
        'fecha_emision',
        'fecha_vencimiento',
        'get_estado_vencimiento',
        'fecha_creacion'
    )
    list_filter = ('tipo', 'fecha_emision', 'fecha_vencimiento', 'fecha_creacion')
    search_fields = ('arrendatario__codigo', 'arrendatario__nombres', 'titulo')
    readonly_fields = ('fecha_creacion', 'subido_por')
    
    fieldsets = (
        ('Información del Documento', {
            'fields': (
                'arrendatario',
                'tipo',
                'titulo',
                'archivo'
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_emision',
                'fecha_vencimiento'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'subido_por'),
            'classes': ('collapse',)
        }),
    )
    
    def get_estado_vencimiento(self, obj):
        if obj.esta_vencido:
            return '❌ Vencido'
        elif obj.fecha_vencimiento:
            return '✅ Vigente'
        return '—'
    get_estado_vencimiento.short_description = 'Estado'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContratoArriendo)
class ContratoArriendoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_contrato',
        'get_arrendatario',
        'get_inmueble',
        'fecha_inicio',
        'fecha_fin',
        'valor_arriendo',
        'estado',
        'get_vigencia'
    )
    list_filter = (
        'estado',
        'tipo_pago',
        'fecha_inicio',
        'fecha_fin',
        'permite_incremento',
        'requiere_seguro'
    )
    search_fields = (
        'numero_contrato',
        'arrendatario__codigo',
        'arrendatario__nombres',
        'arrendatario__razon_social',
        'inmueble__nombre'
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'creado_por')
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'numero_contrato',
                'arrendatario',
                'inmueble'
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_inicio',
                'fecha_fin',
                'fecha_firma'
            )
        }),
        ('Condiciones Económicas', {
            'fields': (
                'valor_arriendo',
                'valor_deposito',
                'gastos_comunes',
                'tipo_pago',
                'dia_pago'
            )
        }),
        ('Incremento', {
            'fields': (
                'permite_incremento',
                'porcentaje_incremento'
            ),
            'classes': ('collapse',)
        }),
        ('Condiciones Adicionales', {
            'fields': (
                'incluye_servicios',
                'servicios_incluidos',
                'permite_subarriendo',
                'requiere_seguro'
            ),
            'classes': ('collapse',)
        }),
        ('Cláusulas', {
            'fields': ('clausulas_especiales',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': (
                'estado',
                'archivo_contrato',
                'observaciones'
            )
        }),
        ('Metadata', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
                'creado_por'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_arrendatario(self, obj):
        return obj.arrendatario.nombre_completo
    get_arrendatario.short_description = 'Arrendatario'
    
    def get_inmueble(self, obj):
        return obj.inmueble.nombre
    get_inmueble.short_description = 'Inmueble'
    
    def get_vigencia(self, obj):
        if obj.esta_vigente:
            return '✅ Vigente'
        elif obj.esta_por_vencer:
            return '⚠️ Por vencer'
        return '—'
    get_vigencia.short_description = 'Vigencia'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
