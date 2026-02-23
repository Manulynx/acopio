from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import (
    TipoArrendatario,
    Arrendatario,
    DocumentoArrendatario,
    ContratoArriendo
)
from .forms import (
    TipoArrendatarioForm,
    ArrendatarioForm,
    DocumentoArrendatarioForm,
    ContratoArriendoForm,
    BusquedaArrendatarioForm,
    BusquedaContratoForm
)


# ========== VISTAS DE ARRENDATARIOS ==========

@login_required
def arrendatario_index(request):
    """Lista de arrendatarios con búsqueda y filtros"""
    form = BusquedaArrendatarioForm(request.GET)
    arrendatarios = Arrendatario.objects.all()
    
    # Aplicar filtros
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        if buscar:
            arrendatarios = arrendatarios.filter(
                Q(codigo__icontains=buscar) |
                Q(nombres__icontains=buscar) |
                Q(apellidos__icontains=buscar) |
                Q(razon_social__icontains=buscar) |
                Q(identificacion__icontains=buscar) |
                Q(email__icontains=buscar)
            )
        
        tipo_persona = form.cleaned_data.get('tipo_persona')
        if tipo_persona:
            arrendatarios = arrendatarios.filter(tipo_persona=tipo_persona)
        
        estado = form.cleaned_data.get('estado')
        if estado:
            arrendatarios = arrendatarios.filter(estado=estado)
        
        tipo_arrendatario = form.cleaned_data.get('tipo_arrendatario')
        if tipo_arrendatario:
            arrendatarios = arrendatarios.filter(tipo_arrendatario=tipo_arrendatario)
        
        solo_activos = form.cleaned_data.get('solo_activos')
        if solo_activos:
            arrendatarios = arrendatarios.filter(activo=True)
    
    # Ordenar
    arrendatarios = arrendatarios.order_by('-fecha_creacion')
    
    # Estadísticas
    estadisticas = {
        'total': arrendatarios.count(),
        'activos': arrendatarios.filter(estado='ACTIVO').count(),
        'morosos': arrendatarios.filter(estado='MOROSO').count(),
        'con_contratos': arrendatarios.filter(contratos__estado__in=['VIGENTE', 'RENOVADO']).distinct().count(),
    }
    
    context = {
        'arrendatarios': arrendatarios,
        'form': form,
        'estadisticas': estadisticas,
    }
    return render(request, 'arrendatarios/index.html', context)


@login_required
def arrendatario_crear(request):
    """Crear un nuevo arrendatario"""
    if request.method == 'POST':
        form = ArrendatarioForm(request.POST)
        if form.is_valid():
            arrendatario = form.save(commit=False)
            arrendatario.creado_por = request.user
            arrendatario.save()
            messages.success(request, f'Arrendatario {arrendatario.nombre_completo} creado exitosamente.')
            return redirect('arrendatarios:detalle', pk=arrendatario.pk)
    else:
        form = ArrendatarioForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Arrendatario',
        'boton': 'Crear',
    }
    return render(request, 'arrendatarios/crear_editar.html', context)


@login_required
def arrendatario_editar(request, pk):
    """Editar un arrendatario existente"""
    arrendatario = get_object_or_404(Arrendatario, pk=pk)
    
    if request.method == 'POST':
        form = ArrendatarioForm(request.POST, instance=arrendatario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Arrendatario {arrendatario.nombre_completo} actualizado exitosamente.')
            return redirect('arrendatarios:detalle', pk=arrendatario.pk)
    else:
        form = ArrendatarioForm(instance=arrendatario)
    
    context = {
        'form': form,
        'arrendatario': arrendatario,
        'titulo': 'Editar Arrendatario',
        'boton': 'Actualizar',
    }
    return render(request, 'arrendatarios/crear_editar.html', context)


@login_required
def arrendatario_detalle(request, pk):
    """Detalle de un arrendatario"""
    arrendatario = get_object_or_404(Arrendatario, pk=pk)
    
    # Obtener contratos relacionados
    contratos = arrendatario.contratos.all().order_by('-fecha_inicio')
    contratos_activos = contratos.filter(estado__in=['VIGENTE', 'RENOVADO'])
    
    # Obtener documentos
    documentos = arrendatario.documentos.all().order_by('-fecha_creacion')
    
    # Calcular estadísticas
    estadisticas = {
        'total_contratos': contratos.count(),
        'contratos_activos': contratos_activos.count(),
        'documentos': documentos.count(),
    }
    
    context = {
        'arrendatario': arrendatario,
        'contratos': contratos[:10],  # Últimos 10 contratos
        'contratos_activos': contratos_activos,
        'documentos': documentos,
        'estadisticas': estadisticas,
    }
    return render(request, 'arrendatarios/detalle.html', context)


@login_required
def arrendatario_eliminar(request, pk):
    """Eliminar un arrendatario"""
    arrendatario = get_object_or_404(Arrendatario, pk=pk)
    
    if request.method == 'POST':
        # Verificar si tiene contratos activos
        if arrendatario.tiene_arriendos_activos:
            messages.error(
                request,
                'No se puede eliminar un arrendatario con contratos activos. Primero finalice o rescinda los contratos.'
            )
            return redirect('arrendatarios:detalle', pk=arrendatario.pk)
        
        nombre = arrendatario.nombre_completo
        arrendatario.delete()
        messages.success(request, f'Arrendatario {nombre} eliminado exitosamente.')
        return redirect('arrendatarios:index')
    
    context = {
        'arrendatario': arrendatario,
    }
    return render(request, 'arrendatarios/eliminar.html', context)


# ========== VISTAS DE DOCUMENTOS ==========

@login_required
def documento_crear(request, arrendatario_pk):
    """Agregar un documento al arrendatario"""
    arrendatario = get_object_or_404(Arrendatario, pk=arrendatario_pk)
    
    if request.method == 'POST':
        form = DocumentoArrendatarioForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.arrendatario = arrendatario
            documento.subido_por = request.user
            documento.save()
            messages.success(request, f'Documento agregado exitosamente.')
            return redirect('arrendatarios:detalle', pk=arrendatario.pk)
    else:
        form = DocumentoArrendatarioForm()
    
    context = {
        'form': form,
        'arrendatario': arrendatario,
        'titulo': 'Agregar Documento',
        'boton': 'Agregar',
    }
    return render(request, 'arrendatarios/documento_crear.html', context)


@login_required
def documento_eliminar(request, pk):
    """Eliminar un documento"""
    documento = get_object_or_404(DocumentoArrendatario, pk=pk)
    arrendatario = documento.arrendatario
    
    if request.method == 'POST':
        # Eliminar archivo físico
        if documento.archivo:
            documento.archivo.delete()
        
        documento.delete()
        messages.success(request, 'Documento eliminado exitosamente.')
        return redirect('arrendatarios:detalle', pk=arrendatario.pk)
    
    context = {
        'documento': documento,
        'arrendatario': arrendatario,
    }
    return render(request, 'arrendatarios/documento_eliminar.html', context)


# ========== VISTAS DE CONTRATOS ==========

@login_required
def contrato_index(request):
    """Lista de contratos con búsqueda y filtros"""
    form = BusquedaContratoForm(request.GET)
    contratos = ContratoArriendo.objects.select_related('arrendatario', 'inmueble').all()
    
    # Aplicar filtros
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        if buscar:
            contratos = contratos.filter(
                Q(numero_contrato__icontains=buscar) |
                Q(arrendatario__nombres__icontains=buscar) |
                Q(arrendatario__apellidos__icontains=buscar) |
                Q(arrendatario__razon_social__icontains=buscar) |
                Q(inmueble__nombre__icontains=buscar)
            )
        
        estado = form.cleaned_data.get('estado')
        if estado:
            contratos = contratos.filter(estado=estado)
        
        arrendatario = form.cleaned_data.get('arrendatario')
        if arrendatario:
            contratos = contratos.filter(arrendatario=arrendatario)
        
        fecha_desde = form.cleaned_data.get('fecha_desde')
        if fecha_desde:
            contratos = contratos.filter(fecha_inicio__gte=fecha_desde)
        
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        if fecha_hasta:
            contratos = contratos.filter(fecha_inicio__lte=fecha_hasta)
    
    # Ordenar
    contratos = contratos.order_by('-fecha_inicio')
    
    # Estadísticas
    estadisticas = {
        'total': contratos.count(),
        'vigentes': contratos.filter(estado__in=['VIGENTE', 'RENOVADO']).count(),
        'finalizados': contratos.filter(estado='FINALIZADO').count(),
        'por_vencer': sum(1 for c in contratos if c.esta_por_vencer),
    }
    
    context = {
        'contratos': contratos,
        'form': form,
        'estadisticas': estadisticas,
    }
    return render(request, 'arrendatarios/contrato_index.html', context)


@login_required
def contrato_crear(request):
    """Crear un nuevo contrato"""
    if request.method == 'POST':
        form = ContratoArriendoForm(request.POST, request.FILES)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.creado_por = request.user
            contrato.save()
            
            # Actualizar estado del inmueble
            inmueble = contrato.inmueble
            inmueble.estado = 'ARRENDADO'
            inmueble.save()
            
            messages.success(request, f'Contrato {contrato.numero_contrato} creado exitosamente.')
            return redirect('arrendatarios:contrato_detalle', pk=contrato.pk)
    else:
        form = ContratoArriendoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Contrato de Arriendo',
        'boton': 'Crear',
    }
    return render(request, 'arrendatarios/contrato_crear_editar.html', context)


@login_required
def contrato_editar(request, pk):
    """Editar un contrato existente"""
    contrato = get_object_or_404(ContratoArriendo, pk=pk)
    inmueble_anterior = contrato.inmueble
    
    if request.method == 'POST':
        form = ContratoArriendoForm(request.POST, request.FILES, instance=contrato)
        if form.is_valid():
            contrato = form.save()
            
            # Si cambió el inmueble, actualizar estados
            if contrato.inmueble != inmueble_anterior:
                inmueble_anterior.estado = 'DISPONIBLE'
                inmueble_anterior.save()
                
                contrato.inmueble.estado = 'ARRENDADO'
                contrato.inmueble.save()
            
            messages.success(request, f'Contrato {contrato.numero_contrato} actualizado exitosamente.')
            return redirect('arrendatarios:contrato_detalle', pk=contrato.pk)
    else:
        form = ContratoArriendoForm(instance=contrato)
        # Permitir editar el inmueble actual
        from inmuebles.models import Inmueble
        form.fields['inmueble'].queryset = Inmueble.objects.filter(
            Q(pk=contrato.inmueble.pk) | Q(activo=True, estado='DISPONIBLE')
        )
    
    context = {
        'form': form,
        'contrato': contrato,
        'titulo': 'Editar Contrato de Arriendo',
        'boton': 'Actualizar',
    }
    return render(request, 'arrendatarios/contrato_crear_editar.html', context)


@login_required
def contrato_detalle(request, pk):
    """Detalle de un contrato"""
    contrato = get_object_or_404(
        ContratoArriendo.objects.select_related('arrendatario', 'inmueble'),
        pk=pk
    )
    
    context = {
        'contrato': contrato,
    }
    return render(request, 'arrendatarios/contrato_detalle.html', context)


@login_required
def contrato_eliminar(request, pk):
    """Eliminar un contrato"""
    contrato = get_object_or_404(ContratoArriendo, pk=pk)
    
    if request.method == 'POST':
        # Liberar el inmueble si el contrato está activo
        if contrato.estado in ['VIGENTE', 'RENOVADO']:
            inmueble = contrato.inmueble
            inmueble.estado = 'DISPONIBLE'
            inmueble.save()
        
        numero = contrato.numero_contrato
        contrato.delete()
        messages.success(request, f'Contrato {numero} eliminado exitosamente.')
        return redirect('arrendatarios:contrato_index')
    
    context = {
        'contrato': contrato,
    }
    return render(request, 'arrendatarios/contrato_eliminar.html', context)


@login_required
def contrato_finalizar(request, pk):
    """Finalizar un contrato"""
    contrato = get_object_or_404(ContratoArriendo, pk=pk)
    
    if request.method == 'POST':
        if contrato.estado in ['VIGENTE', 'RENOVADO']:
            contrato.estado = 'FINALIZADO'
            contrato.save()
            
            # Liberar el inmueble
            inmueble = contrato.inmueble
            inmueble.estado = 'DISPONIBLE'
            inmueble.save()
            
            messages.success(request, f'Contrato {contrato.numero_contrato} finalizado exitosamente.')
        else:
            messages.warning(request, 'El contrato ya no está vigente.')
        
        return redirect('arrendatarios:contrato_detalle', pk=contrato.pk)
    
    context = {
        'contrato': contrato,
    }
    return render(request, 'arrendatarios/contrato_finalizar.html', context)


@login_required
def contrato_rescindir(request, pk):
    """Rescindir un contrato"""
    contrato = get_object_or_404(ContratoArriendo, pk=pk)
    
    if request.method == 'POST':
        if contrato.estado in ['VIGENTE', 'RENOVADO']:
            contrato.estado = 'RESCINDIDO'
            contrato.save()
            
            # Liberar el inmueble
            inmueble = contrato.inmueble
            inmueble.estado = 'DISPONIBLE'
            inmueble.save()
            
            messages.success(request, f'Contrato {contrato.numero_contrato} rescindido exitosamente.')
        else:
            messages.warning(request, 'El contrato ya no está vigente.')
        
        return redirect('arrendatarios:contrato_detalle', pk=contrato.pk)
    
    context = {
        'contrato': contrato,
    }
    return render(request, 'arrendatarios/contrato_rescindir.html', context)


# ========== VISTAS DE TIPOS DE ARRENDATARIOS ==========

@login_required
def tipo_arrendatario_index(request):
    """Lista de tipos de arrendatarios"""
    tipos = TipoArrendatario.objects.annotate(
        num_arrendatarios=Count('arrendatarios')
    ).order_by('nombre')
    
    context = {
        'tipos': tipos,
    }
    return render(request, 'arrendatarios/tipo_index.html', context)


@login_required
def tipo_arrendatario_crear(request):
    """Crear un nuevo tipo de arrendatario"""
    if request.method == 'POST':
        form = TipoArrendatarioForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo de arrendatario {tipo.nombre} creado exitosamente.')
            return redirect('arrendatarios:tipo_index')
    else:
        form = TipoArrendatarioForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Tipo de Arrendatario',
        'boton': 'Crear',
    }
    return render(request, 'arrendatarios/tipo_crear_editar.html', context)


@login_required
def tipo_arrendatario_editar(request, pk):
    """Editar un tipo de arrendatario"""
    tipo = get_object_or_404(TipoArrendatario, pk=pk)
    
    if request.method == 'POST':
        form = TipoArrendatarioForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de arrendatario {tipo.nombre} actualizado exitosamente.')
            return redirect('arrendatarios:tipo_index')
    else:
        form = TipoArrendatarioForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'titulo': 'Editar Tipo de Arrendatario',
        'boton': 'Actualizar',
    }
    return render(request, 'arrendatarios/tipo_crear_editar.html', context)


@login_required
def tipo_arrendatario_eliminar(request, pk):
    """Eliminar un tipo de arrendatario"""
    tipo = get_object_or_404(TipoArrendatario, pk=pk)
    
    if request.method == 'POST':
        # Verificar si tiene arrendatarios asociados
        if tipo.arrendatarios.exists():
            messages.error(
                request,
                'No se puede eliminar este tipo porque tiene arrendatarios asociados.'
            )
            return redirect('arrendatarios:tipo_index')
        
        nombre = tipo.nombre
        tipo.delete()
        messages.success(request, f'Tipo de arrendatario {nombre} eliminado exitosamente.')
        return redirect('arrendatarios:tipo_index')
    
    context = {
        'tipo': tipo,
    }
    return render(request, 'arrendatarios/tipo_eliminar.html', context)
