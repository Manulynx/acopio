from django.urls import path
from . import views

app_name = 'inmuebles'

urlpatterns = [
    # URLs de inmuebles
    path('', views.inmuebles_index, name='index'),
    path('crear/', views.inmueble_crear, name='crear'),
    path('<int:pk>/', views.inmueble_detalle, name='detalle'),
    path('<int:pk>/editar/', views.inmueble_editar, name='editar'),
    path('<int:pk>/eliminar/', views.inmueble_eliminar, name='eliminar'),
    
    # URLs de tipos de inmuebles
    path('tipos/', views.tipos_index, name='tipos_index'),
    path('tipos/crear/', views.tipo_crear, name='tipo_crear'),
    path('tipos/<int:pk>/editar/', views.tipo_editar, name='tipo_editar'),
    
    # URLs de mantenimientos
    path('mantenimientos/', views.mantenimientos_lista, name='mantenimientos_lista'),
    path('<int:inmueble_pk>/mantenimientos/crear/', views.mantenimiento_crear, name='mantenimiento_crear'),
    path('mantenimientos/<int:pk>/editar/', views.mantenimiento_editar, name='mantenimiento_editar'),
    
    # URLs de imágenes
    path('<int:inmueble_pk>/imagenes/crear/', views.imagen_crear, name='imagen_crear'),
    path('imagenes/<int:pk>/eliminar/', views.imagen_eliminar, name='imagen_eliminar'),
]
