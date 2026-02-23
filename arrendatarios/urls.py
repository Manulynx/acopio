from django.urls import path
from . import views

app_name = 'arrendatarios'

urlpatterns = [
    # Arrendatarios
    path('', views.arrendatario_index, name='index'),
    path('crear/', views.arrendatario_crear, name='crear'),
    path('<int:pk>/', views.arrendatario_detalle, name='detalle'),
    path('<int:pk>/editar/', views.arrendatario_editar, name='editar'),
    path('<int:pk>/eliminar/', views.arrendatario_eliminar, name='eliminar'),
    
    # Documentos
    path('<int:arrendatario_pk>/documento/crear/', views.documento_crear, name='documento_crear'),
    path('documento/<int:pk>/eliminar/', views.documento_eliminar, name='documento_eliminar'),
    
    # Contratos
    path('contratos/', views.contrato_index, name='contrato_index'),
    path('contratos/crear/', views.contrato_crear, name='contrato_crear'),
    path('contratos/<int:pk>/', views.contrato_detalle, name='contrato_detalle'),
    path('contratos/<int:pk>/editar/', views.contrato_editar, name='contrato_editar'),
    path('contratos/<int:pk>/eliminar/', views.contrato_eliminar, name='contrato_eliminar'),
    path('contratos/<int:pk>/finalizar/', views.contrato_finalizar, name='contrato_finalizar'),
    path('contratos/<int:pk>/rescindir/', views.contrato_rescindir, name='contrato_rescindir'),
    
    # Tipos de Arrendatarios
    path('tipos/', views.tipo_arrendatario_index, name='tipo_index'),
    path('tipos/crear/', views.tipo_arrendatario_crear, name='tipo_crear'),
    path('tipos/<int:pk>/editar/', views.tipo_arrendatario_editar, name='tipo_editar'),
    path('tipos/<int:pk>/eliminar/', views.tipo_arrendatario_eliminar, name='tipo_eliminar'),
]
