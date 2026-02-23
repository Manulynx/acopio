from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # URLs básicas para reportes (placeholder)
    path('', views.index, name='index'),
    path('mercancia/', views.reporte_mercancia, name='mercancia'),
    path('productos/', views.reporte_productos, name='productos')
    
]