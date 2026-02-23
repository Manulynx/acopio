from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone

from .models import Venta, DetalleVentaProducto, DetalleVentaMercancia
from .forms import VentaForm, DetalleVentaProductoFormSet, DetalleVentaMercanciaFormSet

class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    ordering = ['-fecha_venta']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Búsqueda por cliente o código
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(codigo__icontains=query) |
                Q(cliente__nombre__icontains=query)
            )
        return queryset

class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

class VentaCreateView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['productos_formset'] = DetalleVentaProductoFormSet(self.request.POST)
            data['mercancias_formset'] = DetalleVentaMercanciaFormSet(self.request.POST)
        else:
            data['productos_formset'] = DetalleVentaProductoFormSet()
            data['mercancias_formset'] = DetalleVentaMercanciaFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        productos_formset = context['productos_formset']
        mercancias_formset = context['mercancias_formset']

        with transaction.atomic():
            form.instance.creado_por = self.request.user
            self.object = form.save()
            
            if productos_formset.is_valid():
                productos_formset.instance = self.object
                productos_formset.save()
                
            if mercancias_formset.is_valid():
                mercancias_formset.instance = self.object
                mercancias_formset.save()
                
            # Actualizar stock después de guardar todos los detalles
            self.object.actualizar_stock()

        messages.success(self.request, 'Venta creada exitosamente.')
        return super().form_valid(form)

class VentaUpdateView(LoginRequiredMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['productos_formset'] = DetalleVentaProductoFormSet(
                self.request.POST, instance=self.object
            )
            data['mercancias_formset'] = DetalleVentaMercanciaFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data['productos_formset'] = DetalleVentaProductoFormSet(instance=self.object)
            data['mercancias_formset'] = DetalleVentaMercanciaFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        productos_formset = context['productos_formset']
        mercancias_formset = context['mercancias_formset']

        with transaction.atomic():
            # Guardar estado anterior
            estado_anterior = self.object.estado
            
            self.object = form.save()
            
            if productos_formset.is_valid():
                productos_formset.save()
                
            if mercancias_formset.is_valid():
                mercancias_formset.save()
            
            # Si el estado cambió, actualizar el stock según corresponda
            if estado_anterior != self.object.estado:
                if self.object.estado == 'CANCELADA':
                    self.object.restaurar_stock()
                else:
                    self.object.actualizar_stock()

        messages.success(self.request, 'Venta actualizada exitosamente.')
        return super().form_valid(form)

class VentaDeleteView(LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/venta_confirm_delete.html'
    success_url = reverse_lazy('ventas:venta_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Venta eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

