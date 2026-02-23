from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    # URLs de autenticación (funcionan tanto en /login/ como en /usuarios/)
    path('', views.login_view, name='login'),  # Para /login/
    path('login/', views.login_view, name='login_alt'),  # Para /usuarios/login/
    path('logout/', views.logout_view_func, name='logout'),  # Usar vista de función
    
    # Gestión de usuarios (CRUD)
    path('index/', views.index, name='index'),
    path('crear/', views.crear_usuario, name='crear'),
    path('<int:pk>/', views.detalle_usuario, name='detalle'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar'),
    path('<int:pk>/alternar-estado/', views.alternar_estado_usuario, name='alternar_estado'),
    
    # Perfil y contraseña
    path('perfil/', views.perfil, name='perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # Autenticación - usando vistas basadas en clases (alternativas)
    path('login-class/', views.CustomLoginView.as_view(), name='login_class'),
    path('logout-class/', views.CustomLogoutView.as_view(), name='logout_class'),
    
    # Cambio de contraseña Django built-in
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='usuarios/password_change.html',
             success_url='/usuarios/password_change/done/'
         ), 
         name='password_change'),
    
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='usuarios/password_change_done.html'
         ), 
         name='password_change_done'),
]