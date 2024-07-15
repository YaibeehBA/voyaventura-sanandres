# import json
# from django.shortcuts import render
# from django.db.models import Count, F
# from django.utils.timezone import datetime
# from django.contrib.admin.views.decorators import staff_member_required
# from django.db.models.functions import TruncMonth
# from alojamiento.models import  Alojamiento, Reservacion, TipoAlojamiento
# from userauths.models import Usuario  # Asegúrate de importar tu modelo de Usuario
# from guias.models import GuiaTuristico
# from datetime import datetime
# from django.utils.timezone import make_aware
# from datetime import datetime
# from django.utils import timezone

# def admin_dashboard(request):
#     # Obtener el usuario administrador actual
#     admin_user = request.user

#     # Conteo de usuarios, alojamientos y guías
#     usuarios_count = Usuario.objects.count()
#     guias_count = GuiaTuristico.objects.count()
#     alojamientos_count = Alojamiento.objects.count()

#     # Reservas por mes
#     now = timezone.now()
#     reservaciones_por_mes = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).annotate(
#         month=TruncMonth('fecha_ingreso')
#     ).values('month').annotate(count=Count('id')).order_by('month')

#     # Tipos de alojamiento más reservados
#     tipos_alojamiento_reservados = TipoAlojamiento.objects.filter(reservacion__fecha_ingreso__year=now.year, reservacion__fecha_ingreso__month=now.month).annotate(
#         reservas=Count('reservacion')
#     ).order_by('-reservas')[:3]  # Cambiado a [:3] para mostrar los top 3

#     # Guías más reservados
#     guias_mas_reservados = GuiaTuristico.objects.filter(reservacionguia__fecha_reserva__year=now.year, reservacionguia__fecha_reserva__month=now.month).annotate(
#         reservas=Count('reservacionguia')
#     ).order_by('-reservas')[:3]  # Cambiado a [:3] para mostrar los top 3

    

#     # Obtener los porcentajes de alojamientos y guías
#     total_reservas = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).count()
#     if total_reservas > 0:
#         porcentaje_alojamientos = (Alojamiento.objects.filter(reservacion__fecha_ingreso__year=now.year, reservacion__fecha_ingreso__month=now.month).count() / total_reservas) * 100
#         porcentaje_guias = (GuiaTuristico.objects.filter(reservacionguia__fecha_reserva__year=now.year, reservacionguia__fecha_reserva__month=now.month).count() / total_reservas) * 100
#     else:
#         porcentaje_alojamientos = 0
#         porcentaje_guias = 0

#     # Convertir a formato JSON seguro para JavaScript
#     porcentaje_alojamientos_json = json.dumps(porcentaje_alojamientos, cls=DjangoJSONEncoder)
#     porcentaje_guias_json = json.dumps(porcentaje_guias, cls=DjangoJSONEncoder)

#     # Historial de reservaciones
#     historial_reservaciones = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).order_by('-fecha_ingreso')

#     # Nombre del mes actual en español
#     meses = {
#         1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
#         5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
#         9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
#     }
#     historial_mes_actual = meses[now.month]

#     context = {
#         'admin_user': admin_user,
#         'usuarios_count': usuarios_count,
#         'guias_count': guias_count,
#         'alojamientos_count': alojamientos_count,
#         'reservaciones_por_mes': reservaciones_por_mes,
#         'tipos_alojamiento_reservados': tipos_alojamiento_reservados,
#         'guias_mas_reservados': guias_mas_reservados,
        
#         'historial_reservaciones': historial_reservaciones,
#         'historial_mes_actual': historial_mes_actual,
#         'porcentaje_alojamientos_json': porcentaje_alojamientos_json,
#         'porcentaje_guias_json': porcentaje_guias_json,
#     }

#     return render(request, 'admin/dashboard.html', context)

import json
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from alojamiento.models import Alojamiento, Reservacion, TipoAlojamiento
from userauths.models import Usuario
from guias.models import GuiaTuristico, ReservacionGuia
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Value as V
from itertools import chain
from operator import attrgetter
from django.db.models.functions import TruncDay
from datetime import datetime, date, time
from django.utils.timezone import make_aware, is_naive

# @staff_member_required
# def admin_dashboard(request):
#     # Obtener el usuario administrador actual
#     admin_user = request.user

#     # Conteo de usuarios, alojamientos y guías
#     usuarios_count = Usuario.objects.count()
#     guias_count = GuiaTuristico.objects.count()
#     alojamientos_count = Alojamiento.objects.count()

#     # Reservas por mes
#     now = timezone.now()
#     reservaciones_por_mes = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).annotate(
#         month=TruncMonth('fecha_ingreso')
#     ).values('month').annotate(count=Count('id')).order_by('month')

#     # Tipos de alojamiento más reservados
#     tipos_alojamiento_reservados = TipoAlojamiento.objects.filter(reservacion__fecha_ingreso__year=now.year, reservacion__fecha_ingreso__month=now.month).annotate(
#         reservas=Count('reservacion')
#     ).order_by('-reservas')[:3]

#     # Guías más reservados
#     guias_mas_reservados = GuiaTuristico.objects.filter(reservacionguia__fecha_reserva__year=now.year, reservacionguia__fecha_reserva__month=now.month).annotate(
#         reservas=Count('reservacionguia')
#     ).order_by('-reservas')[:3]

#     # Porcentaje de reservas de alojamientos y guías
#     total_reservas = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).count()
#     if total_reservas > 0:
#         porcentaje_alojamientos = (Alojamiento.objects.filter(reservacion__fecha_ingreso__year=now.year, reservacion__fecha_ingreso__month=now.month).count() / total_reservas) * 100
#         porcentaje_guias = (GuiaTuristico.objects.filter(reservacionguia__fecha_reserva__year=now.year, reservacionguia__fecha_reserva__month=now.month).count() / total_reservas) * 100
#     else:
#         porcentaje_alojamientos = 0
#         porcentaje_guias = 0

#     # Convertir porcentajes a formato JSON seguro para JavaScript
#     porcentaje_alojamientos_json = json.dumps(porcentaje_alojamientos, cls=DjangoJSONEncoder)
#     porcentaje_guias_json = json.dumps(porcentaje_guias, cls=DjangoJSONEncoder)

#     # Historial de reservaciones del mes actual
#     historial_reservaciones = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).order_by('-fecha_ingreso')

#     # Nombre del mes actual en español
#     meses = {
#         1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
#         5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
#         9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
#     }
#     historial_mes_actual = meses[now.month]
    
#     seis_meses_atras = now - timezone.timedelta(days=180)
    
#     reservaciones_alojamientos = Reservacion.objects.filter(
#         fecha_ingreso__gte=seis_meses_atras
#     ).annotate(
#         month=TruncMonth('fecha_ingreso')
#     ).values('month').annotate(
#         count=Count('id')
#     ).order_by('month')

#     reservaciones_guias = ReservacionGuia.objects.filter(
#         fecha_reserva__gte=seis_meses_atras
#     ).annotate(
#         month=TruncMonth('fecha_reserva')
#     ).values('month').annotate(
#         count=Count('id')
#     ).order_by('month')

#     # Preparar datos para la gráfica
#     meses = []
#     datos_alojamientos = []
#     datos_guias = []

#     for i in range(6):
#         mes = now - timezone.timedelta(days=30*i)
#         meses.insert(0, mes.strftime('%Y-%m'))
#         datos_alojamientos.insert(0, 0)
#         datos_guias.insert(0, 0)

#     for reserva in reservaciones_alojamientos:
#         mes = reserva['month'].strftime('%Y-%m')
#         if mes in meses:
#             index = meses.index(mes)
#             datos_alojamientos[index] = reserva['count']

#     for reserva in reservaciones_guias:
#         mes = reserva['month'].strftime('%Y-%m')
#         if mes in meses:
#             index = meses.index(mes)
#             datos_guias[index] = reserva['count']




#     context = {
#         'admin_user': admin_user,
#         'usuarios_count': usuarios_count,
#         'guias_count': guias_count,
#         'alojamientos_count': alojamientos_count,
#         'reservaciones_por_mes': reservaciones_por_mes,
#         'tipos_alojamiento_reservados': tipos_alojamiento_reservados,
#         'guias_mas_reservados': guias_mas_reservados,
#         'historial_reservaciones': historial_reservaciones,
#         'historial_mes_actual': historial_mes_actual,
#         'meses': json.dumps(meses),
#         'datos_alojamientos': json.dumps(datos_alojamientos),
#         'datos_guias': json.dumps(datos_guias),
#     }

#     return render(request, 'admin/dashboard.html', context)



@staff_member_required
def admin_dashboard(request):
    # Obtener el usuario administrador actual
    admin_user = request.user

    # Conteo de usuarios, alojamientos y guías
    usuarios_count = Usuario.objects.count()
    guias_count = GuiaTuristico.objects.count()
    alojamientos_count = Alojamiento.objects.count()

    # Reservas por mes
    now = timezone.now()
    reservaciones_por_mes = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).annotate(
        month=TruncMonth('fecha_ingreso')
    ).values('month').annotate(count=Count('id')).order_by('month')

    # Tipos de alojamiento más reservados
    tipos_alojamiento_reservados = TipoAlojamiento.objects.filter(reservacion__fecha_ingreso__year=now.year, reservacion__fecha_ingreso__month=now.month).annotate(
        reservas=Count('reservacion')
    ).order_by('-reservas')[:3]

    # Guías más reservados
    guias_mas_reservados = GuiaTuristico.objects.filter(reservacionguia__fecha_reserva__year=now.year, reservacionguia__fecha_reserva__month=now.month).annotate(
        reservas=Count('reservacionguia')
    ).order_by('-reservas')[:3]

    # Porcentaje de reservas de alojamientos y guías
    total_reservas = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).count()
    if total_reservas > 0:
        porcentaje_alojamientos = (Alojamiento.objects.filter(reservacion__fecha_ingreso__year=now.year, reservacion__fecha_ingreso__month=now.month).count() / total_reservas) * 100
        porcentaje_guias = (GuiaTuristico.objects.filter(reservacionguia__fecha_reserva__year=now.year, reservacionguia__fecha_reserva__month=now.month).count() / total_reservas) * 100
    else:
        porcentaje_alojamientos = 0
        porcentaje_guias = 0

    # Convertir porcentajes a formato JSON seguro para JavaScript
    porcentaje_alojamientos_json = json.dumps(porcentaje_alojamientos, cls=DjangoJSONEncoder)
    porcentaje_guias_json = json.dumps(porcentaje_guias, cls=DjangoJSONEncoder)

    # Historial de reservaciones del mes actual
    historial_reservaciones = Reservacion.objects.filter(fecha_ingreso__year=now.year, fecha_ingreso__month=now.month).order_by('-fecha_ingreso')

    # Nombre del mes actual en español
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    historial_mes_actual = meses[now.month]
    
    now = timezone.now()
    seis_meses_atras = now - timezone.timedelta(days=180)
    
    # Reservaciones de alojamientos pagadas
    reservaciones_alojamientos = Reservacion.objects.filter(
        fecha_ingreso__gte=seis_meses_atras,
        estado_pago='Pagado'  # Usando 'Pagado' según tus ESTADO_PAGO choices
    ).annotate(
        month=TruncMonth('fecha_ingreso')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Reservaciones de guías pagadas
    reservaciones_guias = ReservacionGuia.objects.filter(
        fecha_reserva__gte=seis_meses_atras,
        estado_pago='Pagado'  # Usando 'Pagado' según tus ESTADO_PAGO choices
    ).annotate(
        month=TruncMonth('fecha_reserva')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Total de reservas pagadas
    total_reservas_pagadas = Reservacion.objects.filter(
        fecha_ingreso__gte=seis_meses_atras,
        estado_pago='Pagado'
    ).count() + ReservacionGuia.objects.filter(
        fecha_reserva__gte=seis_meses_atras,
        estado_pago='Pagado'
    ).count()

    # Preparar datos para la gráfica
    meses = []
    datos_alojamientos = []
    datos_guias = []
    datos_total = []

    for i in range(6):
        mes = now - timezone.timedelta(days=30*i)
        meses.insert(0, mes.strftime('%Y-%m'))
        datos_alojamientos.insert(0, 0)
        datos_guias.insert(0, 0)
        datos_total.insert(0, 0)

    for reserva in reservaciones_alojamientos:
        mes = reserva['month'].strftime('%Y-%m')
        if mes in meses:
            index = meses.index(mes)
            datos_alojamientos[index] = reserva['count']
            datos_total[index] += reserva['count']

    for reserva in reservaciones_guias:
        mes = reserva['month'].strftime('%Y-%m')
        if mes in meses:
            index = meses.index(mes)
            datos_guias[index] = reserva['count']
            datos_total[index] += reserva['count']

    total_alojamientos_pagados = sum(datos_alojamientos)
    total_guias_pagados = sum(datos_guias)
    total_general_pagado = total_alojamientos_pagados + total_guias_pagados

    datos_barras_horizontal = {
        'Alojamientos': total_alojamientos_pagados,
        'Guías': total_guias_pagados
    }

    dashboard_data = {
        'datos_alojamientos': datos_alojamientos,
        'datos_guias': datos_guias,
        'datos_total': datos_total,
        'meses': meses,
        'total_alojamientos_pagados': total_alojamientos_pagados,
        'total_guias_pagados': total_guias_pagados,
    }
    
    # reservaciones_alojamientos = Reservacion.objects.filter(
    #     fecha_ingreso__year=now.year,
    #     fecha_ingreso__month=now.month,
    #     estado_pago='Pagado'  # Usando 'Pagado' según tus ESTADO_PAGO choices
    # ).annotate(
    #     tipo=V('Alojamiento'),
    #     nombre_usuario=F('user__username'),
    #     monto=F('total'),
    #     fecha_creacion_reserva=F('fecha')  # Cambia 'fecha_creacion' a 'fecha_creacion_reserva' o un nombre único
    # ).values('id', 'fecha_creacion_reserva', 'nombre_usuario', 'monto', 'tipo')

    # # Reservaciones de guías pagadas del mes actual
    # reservaciones_guias = ReservacionGuia.objects.filter(
    #     fecha_reserva__year=now.year,
    #     fecha_reserva__month=now.month,
    #     estado_pago='Pagado'  # Usando 'Pagado' según tus ESTADO_PAGO choices
    # ).annotate(
    #     tipo=V('Guía'),
    #     nombre_usuario=F('user__username'),
    #     monto=F('total'),
    #     fecha_creacion_reserva=F('fecha_creacion')  # Cambia 'fecha_creacion' a 'fecha_creacion_reserva' o un nombre único
    # ).values('id', 'fecha_creacion_reserva', 'nombre_usuario', 'monto', 'tipo')

    # # Combinar las reservaciones de alojamientos y guías del mes actual
    # todas_reservaciones = list(chain(reservaciones_alojamientos, reservaciones_guias))

    # # Convertir todas las fechas a datetime y asegurar que sean aware
    # for reserva in todas_reservaciones:
    #     if isinstance(reserva['fecha_creacion_reserva'], date) and not isinstance(reserva['fecha_creacion_reserva'], datetime):
    #         reserva['fecha_creacion_reserva'] = timezone.make_aware(datetime.combine(reserva['fecha_creacion_reserva'], time.min), timezone.get_current_timezone())
    #     elif isinstance(reserva['fecha_creacion_reserva'], datetime) and reserva['fecha_creacion_reserva'].tzinfo is None:
    #         reserva['fecha_creacion_reserva'] = timezone.make_aware(reserva['fecha_creacion_reserva'], timezone.get_current_timezone())

    # # Ordenar las reservaciones por fecha de creación descendente
    # todas_reservaciones = sorted(todas_reservaciones, key=lambda x: x['fecha_creacion_reserva'], reverse=True)

    todas_reservaciones = obtener_reservaciones_mes_actual()

    context = {
        'admin_user': admin_user,
        'usuarios_count': usuarios_count,
        'guias_count': guias_count,
        'alojamientos_count': alojamientos_count,
        'reservaciones_por_mes': reservaciones_por_mes,
        'tipos_alojamiento_reservados': tipos_alojamiento_reservados,
        'guias_mas_reservados': guias_mas_reservados,
        'historial_reservaciones': historial_reservaciones,
        'historial_mes_actual': historial_mes_actual,
        'meses': json.dumps(meses),
        'datos_alojamientos': json.dumps(datos_alojamientos),
        'datos_guias': json.dumps(datos_guias),
        'datos_total': json.dumps(datos_total),
        'total_reservas_pagadas': total_reservas_pagadas,
        'total_alojamientos_pagados': total_alojamientos_pagados,
        'total_guias_pagados': total_guias_pagados,
        'total_general_pagado': total_general_pagado,
        'dashboard_data_json': json.dumps(dashboard_data),
        'datos_barras_horizontal': json.dumps(datos_barras_horizontal),
        'todas_reservaciones': todas_reservaciones, 
        

    }

    return render(request, 'admin/dashboard.html', context)





def obtener_reservaciones_mes_actual():
    now = timezone.now()
    mes_actual = now.month
    anio_actual = now.year

    # Obtener reservaciones de alojamientos del mes actual
    reservaciones_alojamientos = Reservacion.objects.filter(
        fecha__year=anio_actual, 
        fecha__month=mes_actual
    ).annotate(
        tipo=V('Alojamiento'),
        nombre_usuario=F('user__username'),
        monto=F('total'),
        fecha_creacion_reserva=F('fecha')  # Usar el campo 'fecha' como 'fecha_creacion_reserva'
    ).values('id', 'fecha_creacion_reserva', 'nombre_usuario', 'monto', 'tipo')

    # Obtener reservaciones de guías del mes actual
    reservaciones_guias = ReservacionGuia.objects.filter(
        fecha_creacion__year=anio_actual,
        fecha_creacion__month=mes_actual
    ).annotate(
        tipo=V('Guía'),
        nombre_usuario=F('user__username'),
        monto=F('total'),
        fecha_creacion_reserva=F('fecha_creacion')  # Usar el campo 'fecha_creacion' como 'fecha_creacion_reserva'
    ).values('id', 'fecha_creacion_reserva', 'nombre_usuario', 'monto', 'tipo')

    # Combinar las reservaciones
    todas_reservaciones = list(chain(reservaciones_alojamientos, reservaciones_guias))

    # Convertir todas las fechas a datetime con zona horaria para asegurar una comparación consistente
    for reserva in todas_reservaciones:
        if isinstance(reserva['fecha_creacion_reserva'], datetime) and is_naive(reserva['fecha_creacion_reserva']):
            reserva['fecha_creacion_reserva'] = make_aware(reserva['fecha_creacion_reserva'])
        elif isinstance(reserva['fecha_creacion_reserva'], date):
            reserva['fecha_creacion_reserva'] = make_aware(datetime.combine(reserva['fecha_creacion_reserva'], time.min))

    # Ordenar las reservaciones por fecha de creación descendente
    todas_reservaciones = sorted(todas_reservaciones, key=lambda x: x['fecha_creacion_reserva'], reverse=True)

    return todas_reservaciones
