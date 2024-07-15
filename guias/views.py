from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import GuiaTuristico, Ruta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.paginator import Paginator


@login_required(login_url="userauths:sign-in")
def rutas_por_guia(request, guia_id):
    guia = get_object_or_404(GuiaTuristico, id=guia_id, estado__in=["Aprobado", "Disponible"])
    rutas = guia.rutas.all()
    context = {
        'guia': guia,
        'rutas': rutas
    }
    return render(request, 'guiasturistico/rutas.html', context)

def detalle_ruta(request, ruta_id):
    ruta = get_object_or_404(Ruta, id=ruta_id)
  
    return render(request, 'guiasturistico/detalle_ruta.html', {'ruta': ruta})

def detalle_ruta_con_guia(request, ruta_id, guia_id):
    ruta = get_object_or_404(Ruta, id=ruta_id)
    guia = get_object_or_404(GuiaTuristico, id=guia_id, rutas=ruta)
    return render(request, 'guiasturistico/detalle_ruta.html', {'ruta': ruta, 'guia': guia})

def ver_guias(request):
    base_queryset = GuiaTuristico.objects.filter(estado__in=["Aprobado", "Disponible"])
    applied_filters = False
    mostrar_cinta = False
    page  = request.GET.get('page',1)
    # Filtro por precio máximo de las rutas asociadas
    precio_max = request.GET.get('precio_max')
    if precio_max:
        base_queryset = base_queryset.filter(rutas__precio__lte=precio_max).distinct()
        applied_filters = True

    # Filtro por guía con más rutas asociadas
    guia_mas_rutas = request.GET.get('guia_mas_rutas')
    if guia_mas_rutas:
        guia_con_mas_rutas = base_queryset.annotate(num_rutas=Count('rutas')).order_by('-num_rutas').first()
        base_queryset = GuiaTuristico.objects.filter(pk=guia_con_mas_rutas.pk) if guia_con_mas_rutas else GuiaTuristico.objects.none()
        applied_filters = True

    # Filtro por ruta más reservada
    ruta_mas_reservada = request.GET.get('ruta_mas_reservada')
    if ruta_mas_reservada:
        ruta_mas_reservada = Ruta.objects.annotate(num_reservas=Count('reservacionguia')).order_by('-num_reservas').first()
        if ruta_mas_reservada:
            base_queryset = base_queryset.filter(rutas=ruta_mas_reservada)
        else:
            base_queryset = GuiaTuristico.objects.none()
        applied_filters = True

    # Filtro por guía más reservado
    guia_mas_reservado = request.GET.get('guia_mas_reservado')
    if guia_mas_reservado:
        guias_ordenados = base_queryset.annotate(num_reservas=Count('reservacionguia')).order_by('-num_reservas')
        if guias_ordenados:
            max_reservas = guias_ordenados.first().num_reservas
            guias_mas_reservados = guias_ordenados.filter(num_reservas=max_reservas)[:3]
            ids_mas_reservados = [guia.id for guia in guias_mas_reservados]
            base_queryset = base_queryset.filter(id__in=ids_mas_reservados)
            applied_filters = True
            mostrar_cinta = True

    if applied_filters and not base_queryset.exists():
        messages.warning(request, "No se encontraron resultados para los filtros seleccionados.")
        return redirect(reverse('guias:ver_guias'))

    # Marcar los guías más reservados solo si se aplicó el filtro correspondiente
    if mostrar_cinta:
        for guia in base_queryset:
            guia.es_mas_reservado = True
    else:
        for guia in base_queryset:
            guia.es_mas_reservado = False

    try:
         paginator = Paginator(base_queryset,5)
         base_queryset = paginator.page(page)
    except:
         raise Http404
    

    context = {
        "guiaturisticos": base_queryset,
        "mostrar_cinta": mostrar_cinta,
        "paginator":paginator,
    }

    return render(request, "guiasturistico/ver_guias.html", context)