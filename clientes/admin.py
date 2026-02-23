from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, TipoCliente, ContactoCliente, DireccionCliente


@admin.register(TipoCliente)
class TipoClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'total_clientes', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def total_clientes(self, obj):
        return obj.clientes.filter(activo=True).count()
    total_clientes.short_description = 'Total Clientes'


class ContactoClienteInline(admin.TabularInline):
    model = ContactoCliente
    extra = 0
    fields = ['nombre', 'cargo', 'telefono', 'email', 'es_principal', 'activo']


class DireccionClienteInline(admin.TabularInline):
    model = DireccionCliente
    extra = 0
    fields = ['tipo', 'nombre_referencia', 'ciudad', 'es_principal', 'activo']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'razon_social', 'identificacion', 'telefono_principal',
        'email', 'estado_badge', 'calificacion', 'activo'
    ]
    list_filter = ['tipo_empresa', 'estado', 'activo', 'provincia', 'calificacion']
    search_fields = [
        'codigo', 'razon_social', 'nombre_comercial', 'identificacion',
        'email', 'telefono_principal'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [ContactoClienteInline, DireccionClienteInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'identificacion', 'razon_social', 'nombre_comercial', 'tipo_cliente')
        }),
        ('Información Legal', {
            'fields': ('tipo_empresa',)
        }),
        ('Contacto Principal', {
            'fields': (
                'telefono_principal', 'telefono_secundario', 'email', 'sitio_web'
            )
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'provincia', 'codigo_postal', 'pais')
        }),
        ('Contacto Designado', {
            'fields': (
                'nombre_contacto', 'cargo_contacto', 'telefono_contacto', 'email_contacto'
            )
        }),
        ('Información Comercial', {
            'fields': ('descuento_porcentaje',)
        }),
        ('Estado y Calificación', {
            'fields': ('estado', 'calificacion', 'activo')
        }),
        ('Notas', {
            'fields': ('observaciones', 'notas_internas'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'ACTIVO': 'green',
            'INACTIVO': 'gray',
            'SUSPENDIDO': 'orange',
            'MOROSO': 'red',
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'


@admin.register(ContactoCliente)
class ContactoClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cliente', 'cargo', 'telefono', 'email', 'es_principal', 'activo']
    list_filter = ['es_principal', 'activo', 'cliente']
    search_fields = ['nombre', 'cargo', 'email', 'cliente__razon_social']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(DireccionCliente)
class DireccionClienteAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_referencia', 'cliente', 'tipo', 'ciudad', 
        'es_principal', 'activo'
    ]
    list_filter = ['tipo', 'es_principal', 'activo', 'provincia']
    search_fields = [
        'nombre_referencia', 'direccion', 'ciudad', 'cliente__razon_social'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


# Personalización del admin site
admin.site.site_header = "UEB Acopio Bayamo - Gestión de Clientes"
admin.site.site_title = "Gestión de Clientes"
admin.site.index_title = "Panel de Administración de Clientes"
