from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal

from .models import (
    CategoriaMercancia, Proveedor, 
    Mercancia, LoteMercancia, MovimientoStock
)
from .forms import (
    CategoriaMercanciaForm, ProveedorForm,
    MercanciaForm, LoteMercanciaForm, MovimientoStockForm,
    BusquedaMercanciaForm
)


@login_required
def index(request):
    """Vista principal de mercancias con búsqueda y filtrado"""
    form = BusquedaMercanciaForm(request.GET)
    mercancias = Mercancia.objects.select_related('categoria').all()
    
    # Aplicar filtros
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        categoria = form.cleaned_data.get('categoria')
        estado_stock = form.cleaned_data.get('estado_stock')
        activo = form.cleaned_data.get('activo')
        
        if buscar:
            mercancias = mercancias.filter(
                Q(codigo__icontains=buscar) |
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar)
            )
        
        if categoria:
            mercancias = mercancias.filter(categoria=categoria)
        
        if estado_stock:
            if estado_stock == 'sin_stock':
                mercancias = mercancias.filter(stock_actual=0)
            elif estado_stock == 'normal':
                mercancias = mercancias.filter(stock_actual__gt=0)

        if activo:
            mercancias = mercancias.filter(activo=(activo == 'true'))

    # Estadísticas rápidas
    stats = {
        'total': mercancias.count(),
        'activas': mercancias.filter(activo=True).count(),
        'sin_stock': mercancias.filter(stock_actual=0).count(),
        'valor_total': mercancias.aggregate(
            total=Sum(F('stock_actual') * F('precio_compra'))
        )['total'] or 0
    }
    
    # Obtener categorías para el filtro
    categorias = CategoriaMercancia.objects.filter(activa=True).order_by('nombre')
    
    # Paginación
    paginator = Paginator(mercancias, 20)
    page_number = request.GET.get('page')
    mercancias_page = paginator.get_page(page_number)

    context = {
        'mercancias': mercancias_page,
        'form': form,
        'stats': stats,
        'categorias': categorias,
        'title': 'Gestión de Mercancias'
    }
    
    return render(request, 'mercancia/index.html', context)


@login_required
def crear(request):
    """Crear una nueva mercancia"""
    if request.method == 'POST':
        form = MercanciaForm(request.POST)
        if form.is_valid():
            try:
                mercancia = form.save(commit=False)
                mercancia.creado_por = request.user
                mercancia.save()
                
                messages.success(request, f'Mercancia "{mercancia.nombre}" creada exitosamente.')
                return redirect('mercancia:detalle', pk=mercancia.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar la mercancia: {str(e)}')
        else:
            # Agregar mensajes de error específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f'Error: {error}')
    else:
        form = MercanciaForm()

    context = {
        'form': form,
        'title': 'Crear Mercancia',
        'action': 'Crear'
    }

    return render(request, 'mercancia/crear_editar.html', context)


@login_required
def detalle(request, pk):
    """Ver detalles de una mercancia"""
    mercancia = get_object_or_404(Mercancia, pk=pk)

    # Lotes de la mercancia
    lotes = LoteMercancia.objects.filter(mercancia=mercancia, activo=True).order_by('-fecha_produccion')[:10]

    # Últimos movimientos
    movimientos = MovimientoStock.objects.filter(mercancia=mercancia).order_by('-fecha_movimiento')[:15]

    # Estadísticas de la mercancia
    estadisticas = {
        'total_lotes': LoteMercancia.objects.filter(mercancia=mercancia, activo=True).count(),
        'lotes_vencidos': LoteMercancia.objects.filter(
            mercancia=mercancia,
            fecha_vencimiento__lt=timezone.now().date(),
            activo=True
        ).count(),
        'lotes_por_vencer': LoteMercancia.objects.filter(
            mercancia=mercancia,
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=30),
            fecha_vencimiento__gte=timezone.now().date(),
            activo=True
        ).count(),
        'movimientos_mes': MovimientoStock.objects.filter(
            mercancia=mercancia,
            fecha_movimiento__month=timezone.now().month,
            fecha_movimiento__year=timezone.now().year
        ).count()
    }
    
    context = {
        'mercancia': mercancia,
        'lotes': lotes,
        'movimientos': movimientos,
        'estadisticas': estadisticas,
        'title': f'Mercancia: {mercancia.nombre}'
    }

    return render(request, 'mercancia/detalle.html', context)


@login_required
def editar(request, pk):
    """Editar una mercancia existente"""
    mercancia = get_object_or_404(Mercancia, pk=pk)

    if request.method == 'POST':
        form = MercanciaForm(request.POST, instance=mercancia)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mercancia "{mercancia.nombre}" actualizada exitosamente.')
            return redirect('mercancia:detalle', pk=mercancia.pk)
    else:
        form = MercanciaForm(instance=mercancia)
    
    context = {
        'form': form,
        'mercancia': mercancia,
        'title': f'Editar Mercancia: {mercancia.nombre}',
        'action': 'Editar'
    }

    return render(request, 'mercancia/crear_editar.html', context)


@login_required
def eliminar(request, pk):
    """Eliminar (desactivar) una mercancia"""
    mercancia = get_object_or_404(Mercancia, pk=pk)
    
    if request.method == 'POST':
        # No eliminar físicamente, solo desactivar
        mercancia.activo = False
        mercancia.save()

        messages.success(request, f'Mercancia "{mercancia.nombre}" desactivada exitosamente.')
        return redirect('mercancia:index')

    context = {
        'mercancia': mercancia,
        'title': f'Eliminar Mercancia: {mercancia.nombre}'
    }

    return render(request, 'mercancia/eliminar.html', context)


@login_required
def lotes_index(request):
    """Vista de lotes de mercancias"""
    lotes = LoteMercancia.objects.select_related('mercancia', 'proveedor').filter(activo=True)
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    mercancia_id = request.GET.get('mercancia', '')
    estado = request.GET.get('estado', '')
    
    if buscar:
        lotes = lotes.filter(
            Q(numero_lote__icontains=buscar) |
            Q(mercancia__nombre__icontains=buscar) |
            Q(mercancia__codigo__icontains=buscar)
        )

    if mercancia_id:
        lotes = lotes.filter(mercancia_id=mercancia_id)

    if estado == 'vencidos':
        lotes = lotes.filter(fecha_vencimiento__lt=timezone.now().date())
    elif estado == 'por_vencer':
        lotes = lotes.filter(
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=30),
            fecha_vencimiento__gte=timezone.now().date()
        )
    elif estado == 'vigentes':
        lotes = lotes.filter(fecha_vencimiento__gt=timezone.now().date() + timezone.timedelta(days=30))
    
    # Paginación
    paginator = Paginator(lotes, 20)
    page_number = request.GET.get('page')
    lotes_page = paginator.get_page(page_number)
    
    # Mercancias para el filtro
    mercancias = Mercancia.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'lotes': lotes_page,
        'mercancias': mercancias,
        'buscar': buscar,
        'mercancia_seleccionada': mercancia_id,
        'estado_seleccionado': estado,
        'title': 'Gestión de Lotes'
    }

    return render(request, 'mercancia/lotes_index.html', context)


@login_required
def lote_crear(request):
    """Crear un nuevo lote"""
    if request.method == 'POST':
        form = LoteMercanciaForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.creado_por = request.user
            lote.cantidad_actual = lote.cantidad_inicial
            lote.save()

            # Actualizar stock de la mercancia
            mercancia = lote.mercancia
            mercancia.stock_actual += lote.cantidad_inicial
            mercancia.save()

            # Crear movimiento de stock
            MovimientoStock.objects.create(
                mercancia=mercancia,
                lote=lote,
                tipo_movimiento='ENTRADA',
                cantidad=lote.cantidad_inicial,
                stock_anterior=mercancia.stock_actual - lote.cantidad_inicial,
                stock_posterior=mercancia.stock_actual,
                fecha_movimiento=timezone.now(),
                razon=f'Entrada por creación de lote {lote.numero_lote}',
                usuario_responsable=request.user,
                creado_por=request.user
            )
            
            messages.success(request, f'Lote "{lote.numero_lote}" creado exitosamente.')
            return redirect('mercancia:lotes')
    else:
        form = LoteMercanciaForm()

    context = {
        'form': form,
        'title': 'Crear Lote',
        'action': 'Crear'
    }
    
    return render(request, 'mercancia/lote_crear_editar.html', context)


@login_required
def movimientos_index(request):
    """Vista de movimientos de stock"""
    movimientos = MovimientoStock.objects.select_related(
        'mercancia', 'lote', 'usuario_responsable', 'creado_por'
    ).all()
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    mercancia_id = request.GET.get('mercancia', '')
    tipo = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    if buscar:
        movimientos = movimientos.filter(
            Q(mercancia__nombre__icontains=buscar) |
            Q(mercancia__codigo__icontains=buscar) |
            Q(razon__icontains=buscar) |
            Q(documento_referencia__icontains=buscar)
        )

    if mercancia_id:
        movimientos = movimientos.filter(mercancia_id=mercancia_id)

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)
    
    if fecha_desde:
        movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_desde)
    
    if fecha_hasta:
        movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(movimientos, 30)
    page_number = request.GET.get('page')
    movimientos_page = paginator.get_page(page_number)
    
    # Datos para filtros
    mercancias = Mercancia.objects.filter(activo=True).order_by('nombre')
    tipos_movimiento = MovimientoStock.TIPOS_MOVIMIENTO
    
    context = {
        'movimientos': movimientos_page,
        'mercancias': mercancias,
        'tipos_movimiento': tipos_movimiento,
        'filtros': {
            'buscar': buscar,
            'mercancia': mercancia_id,
            'tipo': tipo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        },
        'title': 'Movimientos de Stock'
    }
    
    return render(request, 'mercancia/movimientos_index.html', context)


@login_required
def movimiento_crear(request):
    """Crear un nuevo movimiento de stock"""
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.creado_por = request.user
            
            # Calcular stock anterior y posterior
            mercancias = movimiento.mercancia
            movimiento.stock_anterior = mercancias.stock_actual

            # Determinar si es entrada o salida
            if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE_POSITIVO', 'TRANSFERENCIA_ENTRADA']:
                nuevo_stock = mercancias.stock_actual + movimiento.cantidad
            else:  # SALIDA, AJUSTE_NEGATIVO, TRANSFERENCIA_SALIDA, MERMA, VENCIMIENTO
                nuevo_stock = mercancias.stock_actual - movimiento.cantidad
            
            movimiento.stock_posterior = nuevo_stock
            movimiento.save()
            
            # Actualizar stock de la mercancia
            mercancias.stock_actual = nuevo_stock
            mercancias.save()

            # Actualizar stock del lote si aplica
            if movimiento.lote:
                if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE_POSITIVO', 'TRANSFERENCIA_ENTRADA']:
                    movimiento.lote.cantidad_actual += movimiento.cantidad
                else:
                    movimiento.lote.cantidad_actual -= movimiento.cantidad
                movimiento.lote.save()
            
            messages.success(request, 'Movimiento de stock registrado exitosamente.')
            return redirect('mercancia:movimientos')
    else:
        form = MovimientoStockForm()
    
    context = {
        'form': form,
        'title': 'Registrar Movimiento',
        'action': 'Crear'
    }
    
    return render(request, 'mercancia/movimiento_crear.html', context)


@login_required
def get_lotes_mercancia(request):
    """API para obtener lotes de un mercancia específico"""
    mercancia_id = request.GET.get('mercancia_id')
    if not mercancia_id:
        return JsonResponse({'lotes': []})
    
    lotes = LoteMercancia.objects.filter(
        mercancia_id=mercancia_id,
        activo=True,
        cantidad_actual__gt=0
    ).values('id', 'numero_lote', 'cantidad_actual', 'fecha_vencimiento')
    
    return JsonResponse({'lotes': list(lotes)})


# Vistas para categorías
@login_required
def categorias_index(request):
    """Vista de categorías de mercancias"""
    categorias = CategoriaMercancia.objects.annotate(
        total_mercancias=Count('mercancias', filter=Q(mercancias__activo=True))
    ).all()
    
    # Estadísticas
    categorias_activas = categorias.filter(activa=True).count()
    total_mercancias = Mercancia.objects.filter(activo=True).count()
    
    context = {
        'categorias': categorias,
        'categorias_activas': categorias_activas,
        'total_mercancias': total_mercancias,
        'title': 'Categorías de Mercancias'
    }
    
    return render(request, 'mercancia/categorias.html', context)


@login_required
def categoria_crear(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        form = CategoriaMercanciaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.creado_por = request.user
            categoria.save()
            
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('mercancia:categorias')
    else:
        form = CategoriaMercanciaForm()

    # Redirigir a la página de categorías (se maneja con modal)
    return redirect('mercancia:categorias')


# Vistas para proveedores
@login_required
def proveedores_index(request):
    """Vista de proveedores"""
    proveedores = Proveedor.objects.all()
    
    # Filtros básicos
    buscar = request.GET.get('buscar', '')
    if buscar:
        proveedores = proveedores.filter(
            Q(codigo__icontains=buscar) |
            Q(nombre__icontains=buscar) |
            Q(nombre_comercial__icontains=buscar)
        )
    
    context = {
        'proveedores': proveedores,
        'buscar': buscar,
        'title': 'Proveedores'
    }
    
    return render(request, 'mercancia/proveedores.html', context)


@login_required
def proveedor_crear(request):
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        if proveedor_id:
            proveedor_obj = get_object_or_404(Proveedor, pk=proveedor_id)
            form = ProveedorForm(request.POST, instance=proveedor_obj)
        else:
            form = ProveedorForm(request.POST)

        if form.is_valid():
            proveedor = form.save(commit=False)
            if not proveedor_id:
                proveedor.creado_por = request.user
            proveedor.save()

            if proveedor_id:
                messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado exitosamente.')
            else:
                messages.success(request, f'Proveedor "{proveedor.nombre}" creado exitosamente.')

            return redirect('mercancia:proveedores')
    
    # Redirigir a la página de proveedores (se maneja con modal)
    return redirect('mercancia:proveedores')


@login_required
def proveedor_eliminar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if not request.user.is_superuser:
        messages.error(request, 'No tiene permisos para eliminar proveedores.')
        return redirect('mercancia:proveedores')

    if request.method == 'POST':
        nombre = proveedor.nombre
        proveedor.delete()
        messages.success(request, f'Proveedor "{nombre}" eliminado.')

    return redirect('mercancia:proveedores')
