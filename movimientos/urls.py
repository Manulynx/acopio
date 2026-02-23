from django.urls import path
from . import views

app_name = 'movimientos'

urlpatterns = [
    # URLs básicas para movimientos (placeholder)
    path('', views.index, name='index'),
    path('entrada/', views.entrada, name='entrada'),
    path('salida/', views.salida, name='salida'),
]