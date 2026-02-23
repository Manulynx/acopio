from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from .models import (
    Inmueble, TipoInmueble, ImagenInmueble,
    CaracteristicaAdicional, MantenimientoInmueble
)
from .forms import (
    InmuebleForm, TipoInmuebleForm, ImagenInmuebleForm,
    CaracteristicaAdicionalForm, MantenimientoInmuebleForm, BusquedaInmuebleForm
)


# ===== VISTAS PARA INMUEBLES =====

@login_required
def inmuebles_index(request):
    """Lista todos los inmuebles con búsqueda y filtros"""
    form = BusquedaInmuebleForm(request.GET)
    
    inmuebles = Inmueble.objects.all()
    
    # Aplicar filtros
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        tipo = form.cleaned_data.get('tipo')
        estado = form.cleaned_data.get('estado')
        ciudad = form.cleaned_data.get('ciudad')
        precio_min = form.cleaned_data.get('precio_min')
        precio_max = form.cleaned_data.get('precio_max')
        area_min = form.cleaned_data.get('area_min')
        activo = form.cleaned_data.get('activo')
        
        if buscar:
            inmuebles = inmuebles.filter(
                Q(codigo__icontains=buscar) |
                Q(nombre__icontains=buscar) |
                Q(direccion__icontains=buscar)
            )
        
        if tipo:
            inmuebles = inmuebles.filter(tipo=tipo)
        
        if estado:
            inmuebles = inmuebles.filter(estado=estado)
        
        if ciudad:
            inmuebles = inmuebles.filter(ciudad__icontains=ciudad)
        
        if precio_min:
            inmuebles = inmuebles.filter(precio_arriendo_mensual__gte=precio_min)
        
        if precio_max:
            inmuebles = inmuebles.filter(precio_arriendo_mensual__lte=precio_max)
        
        if area_min:
            inmuebles = inmuebles.filter(area_total__gte=area_min)
        
        if activo == 'true':
            inmuebles = inmuebles.filter(activo=True)
        elif activo == 'false':
            inmuebles = inmuebles.filter(activo=False)
    
    # Ordenar
    inmuebles = inmuebles.order_by('-destacado', 'nombre')
    
    # Estadísticas
    total_inmuebles = Inmueble.objects.count()
    inmuebles_disponibles = Inmueble.objects.filter(estado='DISPONIBLE', activo=True).count()
    inmuebles_arrendados = Inmueble.objects.filter(estado='ARRENDADO').count()
    
    # Paginación
    paginator = Paginator(inmuebles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_inmuebles': total_inmuebles,
        'inmuebles_disponibles': inmuebles_disponibles,
        'inmuebles_arrendados': inmuebles_arrendados,
        'title': 'Gestión de Inmuebles'
    }
    
    return render(request, 'inmuebles/index.html', context)


@login_required
def inmueble_crear(request):
    """Crear un nuevo inmueble"""
    if request.method == 'POST':
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.creado_por = request.user
            inmueble.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" creado exitosamente.')
            return redirect('inmuebles:detalle', pk=inmueble.pk)
    else:
        form = InmuebleForm()
    
    context = {
        'form': form,
        'title': 'Registrar Inmueble',
        'action': 'Crear'
    }
    return render(request, 'inmuebles/crear_editar.html', context)


@login_required
def inmueble_editar(request, pk):
    """Editar un inmueble existente"""
    inmueble = get_object_or_404(Inmueble, pk=pk)
    
    if request.method == 'POST':
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" actualizado exitosamente.')
            return redirect('inmuebles:detalle', pk=inmueble.pk)
    else:
        form = InmuebleForm(instance=inmueble)
    
    context = {
        'form': form,
        'inmueble': inmueble,
        'title': f'Editar Inmueble: {inmueble.nombre}',
        'action': 'Actualizar'
    }
    return render(request, 'inmuebles/crear_editar.html', context)


@login_required
def inmueble_detalle(request, pk):
    """Ver detalles de un inmueble"""
    inmueble = get_object_or_404(Inmueble, pk=pk)
    
    # Obtener imágenes y mantenimientos
    imagenes = inmueble.imagenes.all()
    mantenimientos = inmueble.mantenimientos.order_by('-fecha_programada')[:5]
    caracteristicas = inmueble.caracteristicas_adicionales.all()
    
    context = {
        'inmueble': inmueble,
        'imagenes': imagenes,
        'mantenimientos': mantenimientos,
        'caracteristicas': caracteristicas,
        'title': f'Inmueble: {inmueble.nombre}'
    }
    return render(request, 'inmuebles/detalle.html', context)


@login_required
def inmueble_eliminar(request, pk):
    """Desactivar/eliminar un inmueble"""
    inmueble = get_object_or_404(Inmueble, pk=pk)
    
    if request.method == 'POST':
        # Solo desactivar, no eliminar
        inmueble.activo = False
        inmueble.estado = 'NO_DISPONIBLE'
        inmueble.save()
        messages.warning(request, f'Inmueble "{inmueble.nombre}" desactivado exitosamente.')
        return redirect('inmuebles:index')
    
    context = {
        'inmueble': inmueble,
        'title': f'Eliminar Inmueble: {inmueble.nombre}'
    }
    return render(request, 'inmuebles/eliminar.html', context)


# ===== VISTAS PARA TIPOS DE INMUEBLES =====

@login_required
def tipos_index(request):
    """Lista todos los tipos de inmuebles"""
    tipos = TipoInmueble.objects.annotate(
        total_inmuebles=Count('inmuebles')
    ).order_by('nombre')
    
    context = {
        'tipos': tipos,
        'title': 'Tipos de Inmuebles'
    }
    return render(request, 'inmuebles/tipos_index.html', context)


@login_required
def tipo_crear(request):
    """Crear un nuevo tipo de inmueble"""
    if request.method == 'POST':
        form = TipoInmuebleForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo de inmueble "{tipo.nombre}" creado exitosamente.')
            return redirect('inmuebles:tipos_index')
    else:
        form = TipoInmuebleForm()
    
    context = {
        'form': form,
        'title': 'Crear Tipo de Inmueble',
        'action': 'Crear'
    }
    return render(request, 'inmuebles/tipo_crear_editar.html', context)


@login_required
def tipo_editar(request, pk):
    """Editar un tipo de inmueble"""
    tipo = get_object_or_404(TipoInmueble, pk=pk)
    
    if request.method == 'POST':
        form = TipoInmuebleForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de inmueble "{tipo.nombre}" actualizado exitosamente.')
            return redirect('inmuebles:tipos_index')
    else:
        form = TipoInmuebleForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'title': f'Editar Tipo: {tipo.nombre}',
        'action': 'Actualizar'
    }
    return render(request, 'inmuebles/tipo_crear_editar.html', context)


# ===== VISTAS PARA MANTENIMIENTOS =====

@login_required
def mantenimiento_crear(request, inmueble_pk):
    """Crear un nuevo mantenimiento para un inmueble"""
    inmueble = get_object_or_404(Inmueble, pk=inmueble_pk)
    
    if request.method == 'POST':
        form = MantenimientoInmuebleForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.inmueble = inmueble
            mantenimiento.creado_por = request.user
            mantenimiento.save()
            messages.success(request, 'Mantenimiento registrado exitosamente.')
            return redirect('inmuebles:detalle', pk=inmueble.pk)
    else:
        form = MantenimientoInmuebleForm(initial={'inmueble': inmueble})
    
    context = {
        'form': form,
        'inmueble': inmueble,
        'title': f'Registrar Mantenimiento - {inmueble.nombre}',
        'action': 'Crear'
    }
    return render(request, 'inmuebles/mantenimiento_crear_editar.html', context)


@login_required
def mantenimiento_editar(request, pk):
    """Editar un mantenimiento"""
    mantenimiento = get_object_or_404(MantenimientoInmueble, pk=pk)
    
    if request.method == 'POST':
        form = MantenimientoInmuebleForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mantenimiento actualizado exitosamente.')
            return redirect('inmuebles:detalle', pk=mantenimiento.inmueble.pk)
    else:
        form = MantenimientoInmuebleForm(instance=mantenimiento)
    
    context = {
        'form': form,
        'mantenimiento': mantenimiento,
        'inmueble': mantenimiento.inmueble,
        'title': f'Editar Mantenimiento',
        'action': 'Actualizar'
    }
    return render(request, 'inmuebles/mantenimiento_crear_editar.html', context)


@login_required
def mantenimientos_lista(request):
    """Lista todos los mantenimientos"""
    mantenimientos = MantenimientoInmueble.objects.select_related(
        'inmueble'
    ).order_by('-fecha_programada')
    
    # Paginación
    paginator = Paginator(mantenimientos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Mantenimientos de Inmuebles'
    }
    return render(request, 'inmuebles/mantenimientos_lista.html', context)


# ===== VISTAS PARA IMÁGENES =====

@login_required
def imagen_crear(request, inmueble_pk):
    """Agregar imagen a un inmueble"""
    inmueble = get_object_or_404(Inmueble, pk=inmueble_pk)
    
    if request.method == 'POST':
        form = ImagenInmuebleForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save(commit=False)
            imagen.inmueble = inmueble
            imagen.save()
            messages.success(request, 'Imagen agregada exitosamente.')
            return redirect('inmuebles:detalle', pk=inmueble.pk)
    else:
        form = ImagenInmuebleForm(initial={'inmueble': inmueble})
    
    context = {
        'form': form,
        'inmueble': inmueble,
        'title': f'Agregar Imagen - {inmueble.nombre}',
        'action': 'Agregar'
    }
    return render(request, 'inmuebles/imagen_crear.html', context)


@login_required
def imagen_eliminar(request, pk):
    """Eliminar una imagen"""
    imagen = get_object_or_404(ImagenInmueble, pk=pk)
    inmueble = imagen.inmueble
    
    if request.method == 'POST':
        imagen.delete()
        messages.success(request, 'Imagen eliminada exitosamente.')
        return redirect('inmuebles:detalle', pk=inmueble.pk)
    
    context = {
        'imagen': imagen,
        'inmueble': inmueble,
        'title': 'Eliminar Imagen'
    }
    return render(request, 'inmuebles/imagen_eliminar.html', context)
