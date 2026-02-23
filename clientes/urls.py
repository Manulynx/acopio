from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # URLs de clientes
    path('', views.clientes_index, name='index'),
    path('crear/', views.cliente_crear, name='crear'),
    path('<int:pk>/', views.cliente_detalle, name='detalle'),
    path('<int:pk>/editar/', views.cliente_editar, name='editar'),
    path('<int:pk>/eliminar/', views.cliente_eliminar, name='eliminar'),
    
    # URLs de tipos de clientes
    path('tipos/', views.tipos_index, name='tipos_index'),
    path('tipos/crear/', views.tipo_crear, name='tipo_crear'),
    path('tipos/<int:pk>/editar/', views.tipo_editar, name='tipo_editar'),
    
    # URLs de contactos
    path('<int:cliente_pk>/contactos/crear/', views.contacto_crear, name='contacto_crear'),
    path('contactos/<int:pk>/editar/', views.contacto_editar, name='contacto_editar'),
    
    # URLs de direcciones
    path('<int:cliente_pk>/direcciones/crear/', views.direccion_crear, name='direccion_crear'),
    path('direcciones/<int:pk>/editar/', views.direccion_editar, name='direccion_editar'),
]
