from django.urls import path
from . import views

app_name = 'mercancia'

urlpatterns = [
    # URLs de mercancías
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    
    # URLs de lotes
    path('lotes/', views.lotes_index, name='lotes'),
    path('lotes/crear/', views.lote_crear, name='lote_crear'),
    
    # URLs de movimientos
    path('movimientos/', views.movimientos_index, name='movimientos'),
    path('movimientos/crear/', views.movimiento_crear, name='movimiento_crear'),
    
    # APIs
    path('api/lotes-mercancia/', views.get_lotes_mercancia, name='api_lotes_mercancia'),
    
    # URLs de categorías
    path('categorias/', views.categorias_index, name='categorias'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    
    # URLs de proveedores
    path('proveedores/', views.proveedores_index, name='proveedores'),
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),
]