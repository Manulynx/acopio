from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from .models import Cliente, TipoCliente, ContactoCliente, DireccionCliente
from .forms import (
    ClienteForm, TipoClienteForm, ContactoClienteForm, 
    DireccionClienteForm, BusquedaClienteForm
)


# ===== VISTAS PARA CLIENTES =====

@login_required
def clientes_index(request):
    """Lista todos los clientes con búsqueda y filtros"""
    form = BusquedaClienteForm(request.GET)
    
    clientes = Cliente.objects.all()
    
    # Aplicar filtros
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        tipo_cliente = form.cleaned_data.get('tipo_cliente')
        estado = form.cleaned_data.get('estado')
        activo = form.cleaned_data.get('activo')
        
        if buscar:
            clientes = clientes.filter(
                Q(codigo__icontains=buscar) |
                Q(razon_social__icontains=buscar) |
                Q(nombre_comercial__icontains=buscar) |
                Q(identificacion__icontains=buscar) |
                Q(email__icontains=buscar)
            )
        
        if tipo_cliente:
            clientes = clientes.filter(tipo_cliente=tipo_cliente)
        
        if estado:
            clientes = clientes.filter(estado=estado)
        
        if activo == 'true':
            clientes = clientes.filter(activo=True)
        elif activo == 'false':
            clientes = clientes.filter(activo=False)
    
    # Ordenar
    clientes = clientes.order_by('-fecha_creacion')
    
    # Estadísticas
    total_clientes = Cliente.objects.count()
    clientes_activos = Cliente.objects.filter(activo=True, estado='ACTIVO').count()
    clientes_morosos = Cliente.objects.filter(estado='MOROSO').count()
    
    # Paginación
    paginator = Paginator(clientes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'clientes_morosos': clientes_morosos,
        'title': 'Gestión de Clientes'
    }
    
    return render(request, 'clientes/index.html', context)


@login_required
def cliente_crear(request):
    """Crear un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.creado_por = request.user
            cliente.save()
            messages.success(request, f'Cliente "{cliente.razon_social}" creado exitosamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'title': 'Crear Cliente',
        'action': 'Crear'
    }
    return render(request, 'clientes/crear_editar.html', context)


@login_required
def cliente_editar(request, pk):
    """Editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{cliente.razon_social}" actualizado exitosamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'title': f'Editar Cliente: {cliente.razon_social}',
        'action': 'Actualizar'
    }
    return render(request, 'clientes/crear_editar.html', context)


@login_required
def cliente_detalle(request, pk):
    """Ver detalles de un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Obtener contactos y direcciones
    contactos = cliente.contactos.filter(activo=True)
    direcciones = cliente.direcciones.filter(activo=True)
    
    # TODO: Obtener historial de ventas cuando se implemente el módulo
    
    context = {
        'cliente': cliente,
        'contactos': contactos,
        'direcciones': direcciones,
        'title': f'Cliente: {cliente.razon_social}'
    }
    return render(request, 'clientes/detalle.html', context)


@login_required
def cliente_eliminar(request, pk):
    """Desactivar/eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        # TODO: Verificar si tiene ventas asociadas
        # Por ahora solo desactivar
        cliente.activo = False
        cliente.estado = 'INACTIVO'
        cliente.save()
        messages.warning(request, f'Cliente "{cliente.razon_social}" desactivado exitosamente.')
        return redirect('clientes:index')
    
    context = {
        'cliente': cliente,
        'title': f'Eliminar Cliente: {cliente.razon_social}'
    }
    return render(request, 'clientes/eliminar.html', context)


# ===== VISTAS PARA TIPOS DE CLIENTES =====

@login_required
def tipos_index(request):
    """Lista todos los tipos de clientes"""
    tipos = TipoCliente.objects.annotate(
        total_clientes=Count('clientes')
    ).order_by('nombre')
    
    context = {
        'tipos': tipos,
        'title': 'Tipos de Clientes'
    }
    return render(request, 'clientes/tipos_index.html', context)


@login_required
def tipo_crear(request):
    """Crear un nuevo tipo de cliente"""
    if request.method == 'POST':
        form = TipoClienteForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo de cliente "{tipo.nombre}" creado exitosamente.')
            return redirect('clientes:tipos_index')
    else:
        form = TipoClienteForm()
    
    context = {
        'form': form,
        'title': 'Crear Tipo de Cliente',
        'action': 'Crear'
    }
    return render(request, 'clientes/tipo_crear_editar.html', context)


@login_required
def tipo_editar(request, pk):
    """Editar un tipo de cliente"""
    tipo = get_object_or_404(TipoCliente, pk=pk)
    
    if request.method == 'POST':
        form = TipoClienteForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de cliente "{tipo.nombre}" actualizado exitosamente.')
            return redirect('clientes:tipos_index')
    else:
        form = TipoClienteForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'title': f'Editar Tipo: {tipo.nombre}',
        'action': 'Actualizar'
    }
    return render(request, 'clientes/tipo_crear_editar.html', context)


# ===== VISTAS PARA CONTACTOS =====

@login_required
def contacto_crear(request, cliente_pk):
    """Crear un nuevo contacto para un cliente"""
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    
    if request.method == 'POST':
        form = ContactoClienteForm(request.POST)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.cliente = cliente
            contacto.save()
            messages.success(request, f'Contacto "{contacto.nombre}" agregado exitosamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ContactoClienteForm(initial={'cliente': cliente})
    
    context = {
        'form': form,
        'cliente': cliente,
        'title': f'Agregar Contacto a {cliente.razon_social}',
        'action': 'Crear'
    }
    return render(request, 'clientes/contacto_crear_editar.html', context)


@login_required
def contacto_editar(request, pk):
    """Editar un contacto"""
    contacto = get_object_or_404(ContactoCliente, pk=pk)
    
    if request.method == 'POST':
        form = ContactoClienteForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contacto "{contacto.nombre}" actualizado exitosamente.')
            return redirect('clientes:detalle', pk=contacto.cliente.pk)
    else:
        form = ContactoClienteForm(instance=contacto)
    
    context = {
        'form': form,
        'contacto': contacto,
        'cliente': contacto.cliente,
        'title': f'Editar Contacto: {contacto.nombre}',
        'action': 'Actualizar'
    }
    return render(request, 'clientes/contacto_crear_editar.html', context)


# ===== VISTAS PARA DIRECCIONES =====

@login_required
def direccion_crear(request, cliente_pk):
    """Crear una nueva dirección para un cliente"""
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    
    if request.method == 'POST':
        form = DireccionClienteForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = cliente
            direccion.save()
            messages.success(request, f'Dirección "{direccion.nombre_referencia}" agregada exitosamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = DireccionClienteForm(initial={'cliente': cliente})
    
    context = {
        'form': form,
        'cliente': cliente,
        'title': f'Agregar Dirección a {cliente.razon_social}',
        'action': 'Crear'
    }
    return render(request, 'clientes/direccion_crear_editar.html', context)


@login_required
def direccion_editar(request, pk):
    """Editar una dirección"""
    direccion = get_object_or_404(DireccionCliente, pk=pk)
    
    if request.method == 'POST':
        form = DireccionClienteForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dirección "{direccion.nombre_referencia}" actualizada exitosamente.')
            return redirect('clientes:detalle', pk=direccion.cliente.pk)
    else:
        form = DireccionClienteForm(instance=direccion)
    
    context = {
        'form': form,
        'direccion': direccion,
        'cliente': direccion.cliente,
        'title': f'Editar Dirección: {direccion.nombre_referencia}',
        'action': 'Actualizar'
    }
    return render(request, 'clientes/direccion_crear_editar.html', context)
