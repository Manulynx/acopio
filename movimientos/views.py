from django.shortcuts import render

def index(request):
    return render(request, 'movimientos/index.html', {
        'title': 'Movimientos de Inventario'
    })

def entrada(request):
    return render(request, 'movimientos/entrada.html', {
        'title': 'Entrada de Mercancía'
    })

def salida(request):
    return render(request, 'movimientos/salida.html', {
        'title': 'Salida de Mercancía'
    })
