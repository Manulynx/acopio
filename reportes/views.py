from django.shortcuts import render

def index(request):
    return render(request, 'reportes/index.html', {
        'title': 'Reportes'
    })

def reporte_mercancia(request):
    return render(request, 'reportes/mercancia.html', {
        'title': 'Reporte de Mercancía'
    })

def reporte_productos(request):
    return render(request, 'reportes/productos.html', {
        'title': 'Reporte de Productos'
    })


