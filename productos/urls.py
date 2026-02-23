from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # Productos
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    
    # Lotes
    path('lotes/', views.lotes_index, name='lotes'),
    path('lotes/crear/', views.lote_crear, name='lote_crear'),
    
    # Movimientos de stock
    path('movimientos/', views.movimientos_index, name='movimientos'),
    path('movimientos/crear/', views.movimiento_crear, name='movimiento_crear'),
    
    # APIs
    path('api/lotes-producto/', views.get_lotes_producto, name='api_lotes_producto'),
    path('api/info-producto/<int:producto_id>/', views.get_info_producto, name='api_info_producto'),
    
    # Categorías
    path('categorias/', views.categorias_index, name='categorias'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    
    # Proveedores
    path('proveedores/', views.proveedores_index, name='proveedores'),
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),
]