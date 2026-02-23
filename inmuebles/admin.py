from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Inmueble, TipoInmueble, ImagenInmueble,
    CaracteristicaAdicional, InmuebleCaracteristica, MantenimientoInmueble
)


@admin.register(TipoInmueble)
class TipoInmuebleAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'total_inmuebles', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def total_inmuebles(self, obj):
        return obj.inmuebles.filter(activo=True).count()
    total_inmuebles.short_description = 'Total Inmuebles'


class ImagenInmuebleInline(admin.TabularInline):
    model = ImagenInmueble
    extra = 0
    fields = ['imagen', 'titulo', 'es_principal', 'orden']


class InmuebleCaracteristicaInline(admin.TabularInline):
    model = InmuebleCaracteristica
    extra = 0
    fields = ['caracteristica', 'valor']


class MantenimientoInmuebleInline(admin.TabularInline):
    model = MantenimientoInmueble
    extra = 0
    fields = ['tipo', 'fecha_programada', 'estado', 'costo']
    readonly_fields = ['fecha_creacion']


@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'tipo', 'ciudad', 'area_total',
        'precio_arriendo_mensual', 'estado_badge', 'destacado', 'activo'
    ]
    list_filter = ['tipo', 'estado', 'ciudad', 'tipo_uso', 'condicion', 'activo', 'destacado']
    search_fields = ['codigo', 'nombre', 'direccion', 'ciudad']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'costo_total_mensual']
    inlines = [ImagenInmuebleInline, InmuebleCaracteristicaInline, MantenimientoInmuebleInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'nombre', 'tipo')
        }),
        ('Características Físicas', {
            'fields': (
                'area_total', 'area_util', 'altura', 'capacidad_carga',
                'numero_ambientes', 'numero_banos', 'numero_estacionamientos'
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion', 'ciudad', 'provincia', 'codigo_postal',
                'coordenadas_lat', 'coordenadas_lng'
            )
        }),
        ('Características del Inmueble', {
            'fields': ('tipo_uso', 'condicion', 'ano_construccion')
        }),
        ('Servicios Básicos', {
            'fields': (
                'tiene_electricidad', 'tiene_agua', 'tiene_gas', 'tiene_internet'
            )
        }),
        ('Seguridad', {
            'fields': (
                'tiene_seguridad', 'tiene_vigilancia_24h', 'tiene_camaras',
                'tiene_alarma', 'tiene_extintor', 'tiene_rociadores'
            )
        }),
        ('Facilidades de Carga', {
            'fields': ('tiene_carga_descarga', 'tiene_montacargas', 'tiene_rampa')
        }),
        ('Información de Arriendo', {
            'fields': (
                'precio_arriendo_mensual', 'gastos_comunes', 'costo_total_mensual',
                'deposito_garantia', 'dias_preaviso'
            )
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_disponibilidad', 'activo', 'destacado')
        }),
        ('Descripción', {
            'fields': ('descripcion', 'observaciones'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'DISPONIBLE': 'green',
            'ARRENDADO': 'blue',
            'MANTENIMIENTO': 'orange',
            'RESERVADO': 'purple',
            'NO_DISPONIBLE': 'red',
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'


@admin.register(ImagenInmueble)
class ImagenInmuebleAdmin(admin.ModelAdmin):
    list_display = ['inmueble', 'titulo', 'es_principal', 'orden', 'fecha_creacion']
    list_filter = ['es_principal', 'fecha_creacion']
    search_fields = ['inmueble__nombre', 'titulo']
    readonly_fields = ['fecha_creacion']


@admin.register(CaracteristicaAdicional)
class CaracteristicaAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(MantenimientoInmueble)
class MantenimientoInmuebleAdmin(admin.ModelAdmin):
    list_display = [
        'inmueble', 'tipo', 'fecha_programada', 'fecha_realizacion',
        'estado', 'costo', 'proveedor'
    ]
    list_filter = ['tipo', 'estado', 'fecha_programada']
    search_fields = ['inmueble__nombre', 'descripcion', 'proveedor']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_programada'


# Personalización del admin site
admin.site.site_header = "UEB Acopio Bayamo - Gestión de Inmuebles"
admin.site.site_title = "Gestión de Inmuebles"
admin.site.index_title = "Panel de Administración de Inmuebles"
