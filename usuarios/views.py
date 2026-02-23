from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.decorators import method_decorator
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import json

from .models import CustomUser, Perfil, SesionUsuario, LogAuditoria
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, LoginForm, 
    PerfilForm, CambiarPasswordForm
)


# Utilidades para auditoría
def crear_log_auditoria(usuario, accion, descripcion, modelo_afectado=None, objeto_id=None, 
                       datos_anteriores=None, datos_nuevos=None, request=None):
    """Crear log de auditoría"""
    try:
        LogAuditoria.objects.create(
            usuario=usuario,
            accion=accion,
            modelo_afectado=modelo_afectado,
            objeto_id=str(objeto_id) if objeto_id else None,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=get_client_ip(request) if request else '127.0.0.1',
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            url_solicitada=request.path if request else '',
            metodo_http=request.method if request else '',
        )
    except Exception as e:
        # En caso de error creando log, no afectar la funcionalidad principal
        print(f"Error creando log de auditoría: {e}")


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_staff_or_superuser(user):
    """Verificar si el usuario es staff o superusuario"""
    return user.is_staff or user.is_superuser


# Vistas de autenticación
class CustomLoginView(LoginView):
    """Vista personalizada para el login"""
    form_class = LoginForm
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """Redirigir después del login exitoso"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """Manejar login exitoso"""
        user = form.get_user()
        
        # Actualizar información de conexión
        user.ip_ultima_conexion = get_client_ip(self.request)
        user.navegador_ultima_conexion = self.request.META.get('HTTP_USER_AGENT', '')[:200]
        user.save(update_fields=['ip_ultima_conexion', 'navegador_ultima_conexion'])
        
        # Crear sesión de usuario
        try:
            # Verificar si ya existe una sesión con esta session_key
            session_key = self.request.session.session_key or ''
            if session_key:
                # Finalizar sesión existente si existe
                SesionUsuario.objects.filter(session_key=session_key, activa=True).update(
                    fecha_fin=timezone.now(), 
                    activa=False
                )
            
            # Crear nueva sesión
            SesionUsuario.objects.create(
                usuario=user,
                ip_address=get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                session_key=session_key,
            )
        except Exception as e:
            # Si hay error creando sesión, no afectar el login
            print(f"Error creando sesión de usuario: {e}")
        
        # Log de auditoría
        crear_log_auditoria(
            usuario=user,
            accion='LOGIN',
            descripcion=f'Usuario {user.username} inició sesión',
            request=self.request
        )
        
        messages.success(self.request, f'¡Bienvenido, {user.get_full_name()}!')
        
        # Configurar duración de sesión según "recordarme"
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)  # Expira al cerrar navegador
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Manejar errores de login"""
        messages.error(self.request, 'Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Vista personalizada para logout"""
    next_page = reverse_lazy('usuarios:login')
    http_method_names = ['get', 'post', 'options']  # Permitir GET y POST
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Finalizar sesión activa
            try:
                sesion = SesionUsuario.objects.filter(
                    usuario=request.user,
                    session_key=request.session.session_key,
                    activa=True
                ).first()
                
                if sesion:
                    sesion.fecha_fin = timezone.now()
                    sesion.activa = False
                    sesion.save()
            except Exception:
                pass  # No fallar si hay error cerrando sesión
            
            # Log de auditoría
            crear_log_auditoria(
                usuario=request.user,
                accion='LOGOUT',
                descripcion=f'Usuario {request.user.username} cerró sesión',
                request=request
            )
            
            messages.info(request, 'Sesión cerrada correctamente.')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Permitir logout con GET (para enlaces directos)"""
        return self.post(request, *args, **kwargs)


# Vistas de gestión de usuarios
@login_required
@user_passes_test(is_staff_or_superuser, login_url='usuarios:login')
def index(request):
    """Lista de usuarios"""
    # Busqueda
    search_query = request.GET.get('search', '')
    usuarios_list = CustomUser.objects.all()
    
    if search_query:
        usuarios_list = usuarios_list.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(cedula__icontains=search_query)
        )
    
    usuarios_list = usuarios_list.order_by('username')
    
    # Paginación
    paginator = Paginator(usuarios_list, 10)
    page = request.GET.get('page')
    
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)
    
    context = {
        'title': 'Gestión de Usuarios',
        'usuarios': usuarios,
        'search_query': search_query,
        'total_usuarios': usuarios_list.count(),
        'can_manage': request.user.is_staff or request.user.is_superuser,
    }
    
    return render(request, 'usuarios/index.html', context)


@login_required
@user_passes_test(is_staff_or_superuser, login_url='usuarios:login')
def crear_usuario(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.creado_por = request.user
            user.save()
            
            # Log de auditoría
            crear_log_auditoria(
                usuario=request.user,
                accion='CREATE',
                descripcion=f'Creado usuario {user.username}',
                modelo_afectado='CustomUser',
                objeto_id=user.pk,
                datos_nuevos={
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                request=request
            )
            
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('usuarios:detalle', pk=user.pk)
    else:
        form = CustomUserCreationForm()
    
    context = {
        'title': 'Crear Usuario',
        'form': form,
    }
    
    return render(request, 'usuarios/crear.html', context)


@login_required
def detalle_usuario(request, pk):
    """Detalle de usuario"""
    usuario = get_object_or_404(CustomUser, pk=pk)
    
    # Verificar permisos
    if not request.user.puede_ver_usuario(usuario):
        messages.error(request, 'No tienes permisos para ver este usuario.')
        return redirect('usuarios:index')
    
    context = {
        'title': f'Usuario: {usuario.username}',
        'usuario': usuario,
        'can_edit': request.user.puede_editar_usuario(usuario),
        'can_delete': request.user.puede_eliminar_usuario(usuario),
    }
    
    return render(request, 'usuarios/detalle.html', context)


@login_required
def editar_usuario(request, pk):
    """Editar usuario"""
    usuario = get_object_or_404(CustomUser, pk=pk)
    
    # Verificar permisos
    if not request.user.puede_editar_usuario(usuario):
        messages.error(request, 'No tienes permisos para editar este usuario.')
        return redirect('usuarios:detalle', pk=pk)
    
    if request.method == 'POST':
        # Guardar datos anteriores para auditoría
        datos_anteriores = {
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'is_active': usuario.is_active,
        }
        
        form = CustomUserChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            user = form.save()
            
            # Datos nuevos para auditoría
            datos_nuevos = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
            }
            
            # Log de auditoría
            crear_log_auditoria(
                usuario=request.user,
                accion='UPDATE',
                descripcion=f'Actualizado usuario {user.username}',
                modelo_afectado='CustomUser',
                objeto_id=user.pk,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                request=request
            )
            
            messages.success(request, f'Usuario {user.username} actualizado exitosamente.')
            return redirect('usuarios:detalle', pk=pk)
    else:
        form = CustomUserChangeForm(instance=usuario)
    
    context = {
        'title': f'Editar Usuario: {usuario.username}',
        'form': form,
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/editar.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='usuarios:login')
def eliminar_usuario(request, pk):
    """Eliminar usuario"""
    usuario = get_object_or_404(CustomUser, pk=pk)
    
    # No puede eliminarse a sí mismo
    if request.user == usuario:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('usuarios:detalle', pk=pk)
    
    if request.method == 'POST':
        confirm_username = request.POST.get('confirm_username')
        
        if confirm_username == usuario.username:
            # Guardar datos para auditoría antes de eliminar
            datos_usuario = {
                'username': usuario.username,
                'email': usuario.email,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
            }
            
            username = usuario.username
            usuario.delete()
            
            # Log de auditoría
            crear_log_auditoria(
                usuario=request.user,
                accion='DELETE',
                descripcion=f'Eliminado usuario {username}',
                modelo_afectado='CustomUser',
                objeto_id=pk,
                datos_anteriores=datos_usuario,
                request=request
            )
            
            messages.success(request, f'Usuario {username} eliminado exitosamente.')
            return redirect('usuarios:index')
        else:
            messages.error(request, 'El nombre de usuario no coincide.')
    
    context = {
        'title': f'Eliminar Usuario: {usuario.username}',
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/eliminar.html', context)


@login_required
@require_POST
def alternar_estado_usuario(request, pk):
    """Alternar estado activo/inactivo de usuario via AJAX"""
    usuario = get_object_or_404(CustomUser, pk=pk)
    
    # Verificar permisos
    if not request.user.puede_editar_usuario(usuario):
        return JsonResponse({
            'success': False,
            'message': 'No tienes permisos para cambiar el estado de este usuario.'
        })
    
    # No puede desactivarse a sí mismo
    if request.user == usuario:
        return JsonResponse({
            'success': False,
            'message': 'No puedes cambiar tu propio estado.'
        })
    
    # Cambiar estado
    estado_anterior = usuario.is_active
    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])
    
    accion_text = 'activado' if usuario.is_active else 'desactivado'
    
    # Log de auditoría
    crear_log_auditoria(
        usuario=request.user,
        accion='UPDATE',
        descripcion=f'Usuario {usuario.username} {accion_text}',
        modelo_afectado='CustomUser',
        objeto_id=usuario.pk,
        datos_anteriores={'is_active': estado_anterior},
        datos_nuevos={'is_active': usuario.is_active},
        request=request
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Usuario {usuario.username} {accion_text} exitosamente.',
        'nuevo_estado': usuario.is_active
    })


@login_required
def perfil(request):
    """Ver perfil propio"""
    usuario = request.user
    perfil_obj, created = Perfil.objects.get_or_create(usuario=usuario)
    
    context = {
        'title': 'Mi Perfil',
        'usuario': usuario,
        'perfil': perfil_obj,
    }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def editar_perfil(request):
    """Editar perfil propio"""
    usuario = request.user
    perfil_obj, created = Perfil.objects.get_or_create(usuario=usuario)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=usuario)
        perfil_form = PerfilForm(request.POST, instance=perfil_obj)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            
            # Log de auditoría
            crear_log_auditoria(
                usuario=request.user,
                accion='UPDATE',
                descripcion='Actualizado perfil propio',
                modelo_afectado='CustomUser',
                objeto_id=usuario.pk,
                request=request
            )
            
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
    else:
        user_form = CustomUserChangeForm(instance=usuario)
        perfil_form = PerfilForm(instance=perfil_obj)
    
    context = {
        'title': 'Editar Mi Perfil',
        'user_form': user_form,
        'perfil_form': perfil_form,
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/editar_perfil.html', context)


@login_required
def cambiar_password(request):
    """Cambiar contraseña propia"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            
            # Actualizar sesión para no cerrar después del cambio
            update_session_auth_hash(request, user)
            
            # Log de auditoría
            crear_log_auditoria(
                usuario=request.user,
                accion='PASSWORD_CHANGE',
                descripcion='Cambio de contraseña propio',
                modelo_afectado='CustomUser',
                objeto_id=user.pk,
                request=request
            )
            
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('usuarios:perfil')
    else:
        form = CambiarPasswordForm(request.user)
    
    context = {
        'title': 'Cambiar Contraseña',
        'form': form,
    }
    
    return render(request, 'usuarios/cambiar_password.html', context)


# Vistas de login y logout usando las clases personalizadas
login_view = CustomLoginView.as_view()
logout_view = CustomLogoutView.as_view()

# Vista de logout alternativa como función
@require_http_methods(["GET", "POST"])
def logout_view_func(request):
    """Vista de logout como función que acepta GET y POST"""
    if request.user.is_authenticated:
        # Finalizar sesión activa
        try:
            sesion = SesionUsuario.objects.filter(
                usuario=request.user,
                session_key=request.session.session_key,
                activa=True
            ).first()
            
            if sesion:
                sesion.fecha_fin = timezone.now()
                sesion.activa = False
                sesion.save()
        except Exception:
            pass  # No fallar si hay error cerrando sesión
        
        # Log de auditoría
        crear_log_auditoria(
            usuario=request.user,
            accion='LOGOUT',
            descripcion=f'Usuario {request.user.username} cerró sesión',
            request=request
        )
        
        messages.info(request, 'Sesión cerrada correctamente.')
        
        # Cerrar sesión
        logout(request)
    
    return redirect('usuarios:login')