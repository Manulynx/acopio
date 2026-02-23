from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import json

@login_required
def dashboard(request):
    """Vista del dashboard - Gráfico de cantidad de mercancías y productos por proveedor"""
    
    # Importar modelos necesarios
    from productos.models import Producto, Proveedor as ProveedorProducto, LoteProducto
    from mercancia.models import Mercancia, Proveedor as ProveedorMercancia, LoteMercancia
    
    # Obtener datos de productos y mercancías por proveedor
    datos_por_proveedor = []
    total_productos_global = 0
    total_mercancias_global = 0
    
    # Crear un diccionario para combinar proveedores de ambos modelos
    proveedores_dict = {}
    
    # Obtener proveedores únicos de productos (a través de lotes)
    lotes_productos = LoteProducto.objects.filter(
        activo=True,
        proveedor__activo=True,
        producto__activo=True
    ).select_related('proveedor', 'producto')
    
    for lote in lotes_productos:
        proveedor_nombre = lote.proveedor.nombre
        if proveedor_nombre not in proveedores_dict:
            proveedores_dict[proveedor_nombre] = {
                'productos': set(),
                'mercancias': set(),
                'stock_productos': 0,
                'stock_mercancias': 0
            }
        proveedores_dict[proveedor_nombre]['productos'].add(lote.producto.id)
        # Sumar la cantidad actual del lote para el stock de productos
        proveedores_dict[proveedor_nombre]['stock_productos'] += float(lote.cantidad_actual)
    
    # Obtener proveedores únicos de mercancías (a través de lotes)
    lotes_mercancias = LoteMercancia.objects.filter(
        activo=True,
        proveedor__activo=True,
        mercancia__activo=True
    ).select_related('proveedor', 'mercancia')
    
    for lote in lotes_mercancias:
        proveedor_nombre = lote.proveedor.nombre
        if proveedor_nombre not in proveedores_dict:
            proveedores_dict[proveedor_nombre] = {
                'productos': set(),
                'mercancias': set(),
                'stock_productos': 0,
                'stock_mercancias': 0
            }
        proveedores_dict[proveedor_nombre]['mercancias'].add(lote.mercancia.id)
        # Sumar la cantidad actual del lote para el stock de mercancías
        proveedores_dict[proveedor_nombre]['stock_mercancias'] += float(lote.cantidad_actual)
    
    # Convertir a la estructura final
    datos_por_stock = []  # Nueva lista para datos por stock
    
    for proveedor_nombre, datos in proveedores_dict.items():
        total_productos = len(datos['productos'])
        total_mercancias = len(datos['mercancias'])
        stock_productos = round(datos['stock_productos'], 2)
        stock_mercancias = round(datos['stock_mercancias'], 2)
        
        if total_productos > 0 or total_mercancias > 0:
            datos_por_proveedor.append({
                'proveedor': proveedor_nombre,
                'productos': total_productos,
                'mercancias': total_mercancias,
                'total': total_productos + total_mercancias
            })
            
            # Datos para el gráfico de stock
            datos_por_stock.append({
                'proveedor': proveedor_nombre,
                'stock_productos': stock_productos,
                'stock_mercancias': stock_mercancias,
                'stock_total': stock_productos + stock_mercancias
            })
            
            # Sumar a los totales globales
            total_productos_global += total_productos
            total_mercancias_global += total_mercancias
    
    # Ordenar por total (descendente)
    datos_por_proveedor.sort(key=lambda x: x['total'], reverse=True)
    datos_por_stock.sort(key=lambda x: x['stock_total'], reverse=True)
    
    # Tomar solo los top 10 para mejor visualización
    top_proveedores_stock = datos_por_stock[:10]
    
    # Preparar datos para el gráfico de cantidades
    proveedores_nombres = [item['proveedor'] for item in datos_por_proveedor]
    productos_cantidades = [item['productos'] for item in datos_por_proveedor]
    mercancias_cantidades = [item['mercancias'] for item in datos_por_proveedor]
    
    # Preparar datos para el gráfico de stock (solo top 10)
    proveedores_stock_nombres = [item['proveedor'] for item in top_proveedores_stock]
    stock_productos_cantidades = [item['stock_productos'] for item in top_proveedores_stock]
    stock_mercancias_cantidades = [item['stock_mercancias'] for item in top_proveedores_stock]
    
    # Si no hay datos, mostrar mensaje informativo
    if not datos_por_proveedor:
        proveedores_nombres = ['Sin datos']
        productos_cantidades = [0]
        mercancias_cantidades = [0]
        proveedores_stock_nombres = ['Sin datos']
        stock_productos_cantidades = [0]
        stock_mercancias_cantidades = [0]
    elif not top_proveedores_stock:
        proveedores_stock_nombres = ['Sin datos']
        stock_productos_cantidades = [0]
        stock_mercancias_cantidades = [0]
    
    context = {
        'datos_por_proveedor': datos_por_proveedor,
        'top_proveedores_stock': top_proveedores_stock,
        'proveedores_nombres': json.dumps(proveedores_nombres),
        'productos_cantidades': json.dumps(productos_cantidades),
        'mercancias_cantidades': json.dumps(mercancias_cantidades),
        'proveedores_stock_nombres': json.dumps(proveedores_stock_nombres),
        'stock_productos_cantidades': json.dumps(stock_productos_cantidades),
        'stock_mercancias_cantidades': json.dumps(stock_mercancias_cantidades),
        'total_productos_global': total_productos_global,
        'total_mercancias_global': total_mercancias_global,
        'gran_total': total_productos_global + total_mercancias_global,
        'total_proveedores': len(datos_por_proveedor),
    }
    
    return render(request, 'dashboard.html', context)