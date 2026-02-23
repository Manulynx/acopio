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
    CategoriaProducto, Proveedor, 
    Producto, LoteProducto, MovimientoStock
)
from .forms import (
    CategoriaProductoForm, ProveedorForm,
    ProductoForm, LoteProductoForm, MovimientoStockForm,
    BusquedaProductoForm
)


@login_required
def index(request):
    """Vista principal de productos con búsqueda y filtrado"""
    form = BusquedaProductoForm(request.GET)
    productos = Producto.objects.select_related('categoria').all()
    
    # Aplicar filtros
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        categoria = form.cleaned_data.get('categoria')
        estado_stock = form.cleaned_data.get('estado_stock')
        activo = form.cleaned_data.get('activo')
        
        if buscar:
            productos = productos.filter(
                Q(codigo__icontains=buscar) |
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar)
            )
        
        if categoria:
            productos = productos.filter(categoria=categoria)
        
        if estado_stock:
            if estado_stock == 'sin_stock':
                productos = productos.filter(stock_actual=0)
            elif estado_stock == 'normal':
                productos = productos.filter(stock_actual__gt=0)
        
        if activo:
            productos = productos.filter(activo=(activo == 'true'))
    
    # Estadísticas rápidas
    estadisticas = {
        'total_productos': productos.count(),
        'productos_activos': productos.filter(activo=True).count(),
        'sin_stock': productos.filter(stock_actual=0).count(),
        'valor_total_inventario': productos.aggregate(
            total=Sum(F('stock_actual') * F('precio_compra'))
        )['total'] or 0
    }
    
    # Paginación
    paginator = Paginator(productos, 20)
    page_number = request.GET.get('page')
    productos_page = paginator.get_page(page_number)
    
    context = {
        'productos': productos_page,
        'form': form,
        'estadisticas': estadisticas,
        'title': 'Gestión de Productos'
    }
    
    return render(request, 'productos/index.html', context)


@login_required
def crear(request):
    """Crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.creado_por = request.user
            producto.save()
            
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('productos:detalle', pk=producto.pk)
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'title': 'Crear Producto',
        'action': 'Crear'
    }
    
    return render(request, 'productos/crear_editar.html', context)


@login_required
def detalle(request, pk):
    """Ver detalles de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    # Lotes del producto
    lotes = LoteProducto.objects.filter(producto=producto, activo=True).order_by('-fecha_produccion')[:10]
    
    # Últimos movimientos
    movimientos = MovimientoStock.objects.filter(producto=producto).order_by('-fecha_movimiento')[:15]
    
    # Estadísticas del producto
    estadisticas = {
        'total_lotes': LoteProducto.objects.filter(producto=producto, activo=True).count(),
        'lotes_vencidos': LoteProducto.objects.filter(
            producto=producto, 
            fecha_vencimiento__lt=timezone.now().date(),
            activo=True
        ).count(),
        'lotes_por_vencer': LoteProducto.objects.filter(
            producto=producto,
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=30),
            fecha_vencimiento__gte=timezone.now().date(),
            activo=True
        ).count(),
        'movimientos_mes': MovimientoStock.objects.filter(
            producto=producto,
            fecha_movimiento__month=timezone.now().month,
            fecha_movimiento__year=timezone.now().year
        ).count()
    }
    
    context = {
        'producto': producto,
        'lotes': lotes,
        'movimientos': movimientos,
        'estadisticas': estadisticas,
        'title': f'Producto: {producto.nombre}'
    }
    
    return render(request, 'productos/detalle.html', context)


@login_required
def editar(request, pk):
    """Editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('productos:detalle', pk=producto.pk)
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'title': f'Editar Producto: {producto.nombre}',
        'action': 'Editar'
    }
    
    return render(request, 'productos/crear_editar.html', context)


@login_required
def eliminar(request, pk):
    """Eliminar (desactivar) un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        # No eliminar físicamente, solo desactivar
        producto.activo = False
        producto.save()
        
        messages.success(request, f'Producto "{producto.nombre}" desactivado exitosamente.')
        return redirect('productos:index')
    
    context = {
        'producto': producto,
        'title': f'Eliminar Producto: {producto.nombre}'
    }
    
    return render(request, 'productos/eliminar.html', context)


@login_required
def lotes_index(request):
    """Vista de lotes de productos"""
    lotes = LoteProducto.objects.select_related('producto', 'proveedor').filter(activo=True)
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    producto_id = request.GET.get('producto', '')
    estado = request.GET.get('estado', '')
    calidad = request.GET.get('calidad', '')
    
    if buscar:
        lotes = lotes.filter(
            Q(numero_lote__icontains=buscar) |
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar)
        )
    
    if producto_id:
        lotes = lotes.filter(producto_id=producto_id)
    
    if estado == 'vencido':
        lotes = lotes.filter(fecha_vencimiento__lt=timezone.now().date())
    elif estado == 'proximo':
        lotes = lotes.filter(
            fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=30),
            fecha_vencimiento__gte=timezone.now().date()
        )
    elif estado == 'vigente':
        lotes = lotes.filter(fecha_vencimiento__gt=timezone.now().date() + timezone.timedelta(days=30))
    
    if calidad:
        lotes = lotes.filter(estado_calidad=calidad)
    
    # Estadísticas
    total_lotes = LoteProducto.objects.filter(activo=True).count()
    lotes_vencidos = LoteProducto.objects.filter(
        activo=True,
        fecha_vencimiento__lt=timezone.now().date()
    ).count()
    lotes_proximos = LoteProducto.objects.filter(
        activo=True,
        fecha_vencimiento__lte=timezone.now().date() + timezone.timedelta(days=30),
        fecha_vencimiento__gte=timezone.now().date()
    ).count()
    lotes_vigentes = LoteProducto.objects.filter(
        activo=True,
        fecha_vencimiento__gt=timezone.now().date() + timezone.timedelta(days=30)
    ).count()
    
    # Paginación
    paginator = Paginator(lotes, 20)
    page_number = request.GET.get('page')
    lotes_page = paginator.get_page(page_number)
    
    # Productos para el filtro
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'lotes': lotes_page,
        'productos': productos,
        'buscar': buscar,
        'producto_seleccionado': producto_id,
        'estado_seleccionado': estado,
        'stats': {
            'total': total_lotes,
            'vencidos': lotes_vencidos,
            'proximos': lotes_proximos,
            'vigentes': lotes_vigentes,
        },
        'title': 'Gestión de Lotes'
    }
    
    return render(request, 'productos/lotes_index.html', context)


@login_required
def lote_crear(request):
    """Crear un nuevo lote"""
    if request.method == 'POST':
        form = LoteProductoForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.creado_por = request.user
            lote.cantidad_actual = lote.cantidad_inicial
            lote.save()
            
            # Actualizar stock del producto
            producto = lote.producto
            producto.stock_actual += lote.cantidad_inicial
            producto.save()
            
            # Crear movimiento de stock
            MovimientoStock.objects.create(
                producto=producto,
                lote=lote,
                tipo_movimiento='ENTRADA',
                cantidad=lote.cantidad_inicial,
                stock_anterior=producto.stock_actual - lote.cantidad_inicial,
                stock_posterior=producto.stock_actual,
                fecha_movimiento=timezone.now(),
                razon=f'Entrada por creación de lote {lote.numero_lote}',
                usuario_responsable=request.user,
                creado_por=request.user
            )
            
            messages.success(request, f'Lote "{lote.numero_lote}" creado exitosamente.')
            return redirect('productos:lotes')
    else:
        form = LoteProductoForm()
    
    context = {
        'form': form,
        'title': 'Crear Lote',
        'action': 'Crear'
    }
    
    return render(request, 'productos/lote_crear_editar.html', context)


@login_required
def movimientos_index(request):
    """Vista de movimientos de stock"""
    movimientos = MovimientoStock.objects.select_related(
        'producto', 'lote', 'usuario_responsable', 'creado_por'
    ).all()
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    producto_id = request.GET.get('producto', '')
    tipo = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    if buscar:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar) |
            Q(razon__icontains=buscar) |
            Q(documento_referencia__icontains=buscar)
        )
    
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    
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
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    tipos_movimiento = MovimientoStock.TIPOS_MOVIMIENTO
    
    context = {
        'movimientos': movimientos_page,
        'productos': productos,
        'tipos_movimiento': tipos_movimiento,
        'filtros': {
            'buscar': buscar,
            'producto': producto_id,
            'tipo': tipo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        },
        'title': 'Movimientos de Stock'
    }
    
    return render(request, 'productos/movimientos_index.html', context)


@login_required
def movimiento_crear(request):
    """Crear un nuevo movimiento de stock"""
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.creado_por = request.user
            
            # Calcular stock anterior y posterior
            producto = movimiento.producto
            movimiento.stock_anterior = producto.stock_actual
            
            # Determinar si es entrada o salida
            if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE_POSITIVO', 'TRANSFERENCIA_ENTRADA']:
                nuevo_stock = producto.stock_actual + movimiento.cantidad
            else:  # SALIDA, AJUSTE_NEGATIVO, TRANSFERENCIA_SALIDA, MERMA, VENCIMIENTO
                nuevo_stock = producto.stock_actual - movimiento.cantidad
            
            movimiento.stock_posterior = nuevo_stock
            movimiento.save()
            
            # Actualizar stock del producto
            producto.stock_actual = nuevo_stock
            producto.refresh_from_db()
            producto.save()
            
            # Actualizar stock del lote si aplica
            if movimiento.lote:
                if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE_POSITIVO', 'TRANSFERENCIA_ENTRADA']:
                    movimiento.lote.cantidad_actual += movimiento.cantidad
                else:
                    movimiento.lote.cantidad_actual -= movimiento.cantidad
                movimiento.lote.save()
            
            messages.success(request, 'Movimiento de stock registrado exitosamente.')
            return redirect('productos:movimientos')
    else:
        form = MovimientoStockForm()
    
    context = {
        'form': form,
        'title': 'Registrar Movimiento',
        'action': 'Crear'
    }
    
    return render(request, 'productos/movimiento_crear.html', context)


@login_required
def get_lotes_producto(request):
    """API para obtener lotes de un producto específico"""
    producto_id = request.GET.get('producto_id')
    if not producto_id:
        return JsonResponse({'lotes': []})
    
    lotes = LoteProducto.objects.filter(
        producto_id=producto_id,
        activo=True,
        cantidad_actual__gt=0
    ).values('id', 'numero_lote', 'cantidad_actual', 'fecha_vencimiento')
    
    return JsonResponse({'lotes': list(lotes)})


@login_required
def get_info_producto(request, producto_id):
    """API para obtener información básica de un producto"""
    try:
        producto = Producto.objects.get(id=producto_id)
        data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'stock_actual': float(producto.stock_actual),
            'precio_compra': float(producto.precio_compra) if producto.precio_compra else 0,
            'precio_venta': float(producto.precio_venta) if producto.precio_venta else 0,
            'requiere_lote': producto.requiere_lote,
            'requiere_vencimiento': producto.requiere_vencimiento,
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


# Vistas para categorías
@login_required
def categorias_index(request):
    """Vista de categorías de productos"""
    categorias = CategoriaProducto.objects.annotate(
        total_productos=Count('productos', filter=Q(productos__activo=True))
    ).all()
    
    context = {
        'categorias': categorias,
        'title': 'Categorías de Productos'
    }
    
    return render(request, 'productos/categorias_index.html', context)


@login_required
def categoria_crear(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.creado_por = request.user
            categoria.save()
            
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('productos:categorias')
    else:
        form = CategoriaProductoForm()
    
    context = {
        'form': form,
        'title': 'Crear Categoría',
        'action': 'Crear'
    }
    
    return render(request, 'productos/categoria_crear_editar.html', context)


# Vistas para proveedores
@login_required
def proveedores_index(request):
    """Vista de proveedores"""
    proveedores = Proveedor.objects.all()
    
    # Filtros básicos
    buscar = request.GET.get('buscar', '')
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    
    if buscar:
        proveedores = proveedores.filter(
            Q(codigo__icontains=buscar) |
            Q(nombre__icontains=buscar) |
            Q(nombre_comercial__icontains=buscar) |
            Q(identificacion__icontains=buscar)
        )
    
    if tipo:
        proveedores = proveedores.filter(tipo=tipo)
    
    if estado == 'activo':
        proveedores = proveedores.filter(activo=True)
    elif estado == 'inactivo':
        proveedores = proveedores.filter(activo=False)
    
    # Estadísticas
    proveedores_activos = Proveedor.objects.filter(activo=True).count()
    
    # Licencias por vencer (próximos 30 días)
    fecha_limite = timezone.now().date() + timezone.timedelta(days=30)
    licencias_vencidas = Proveedor.objects.filter(
        fecha_vencimiento_licencia__lte=fecha_limite,
        fecha_vencimiento_licencia__gte=timezone.now().date()
    ).count()
    
    context = {
        'proveedores': proveedores,
        'buscar': buscar,
        'proveedores_activos': proveedores_activos,
        'licencias_vencidas': licencias_vencidas,
        'title': 'Proveedores'
    }
    
    return render(request, 'productos/proveedores_index.html', context)


@login_required
def proveedor_crear(request):
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.creado_por = request.user
            proveedor.save()
            
            messages.success(request, f'Proveedor "{proveedor.nombre}" creado exitosamente.')
            return redirect('productos:proveedores')
    else:
        form = ProveedorForm()
    
    context = {
        'form': form,
        'title': 'Crear Proveedor',
        'action': 'Crear'
    }
    
    return render(request, 'productos/proveedor_crear_editar.html', context)
