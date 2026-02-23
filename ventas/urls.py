from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Lista de ventas
    path('', views.VentaListView.as_view(), name='venta_list'),
    
    # Crear venta
    path('crear/', views.VentaCreateView.as_view(), name='venta_create'),
    
    # Detalle de venta
    path('<int:pk>/', views.VentaDetailView.as_view(), name='venta_detail'),
    
    # Editar venta
    path('<int:pk>/editar/', views.VentaUpdateView.as_view(), name='venta_update'),
    
    # Eliminar venta
    path('<int:pk>/eliminar/', views.VentaDeleteView.as_view(), name='venta_delete'),
]