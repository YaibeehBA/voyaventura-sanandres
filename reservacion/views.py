import io
from django.conf import settings
import json
import stripe
from django.http import JsonResponse
from decimal import Decimal
from django.shortcuts import render, redirect
from django.urls import reverse
from alojamiento.models import Alojamiento, TipoAlojamiento, Habitacion
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from alojamiento.models import Reservacion
from guias.models import ReservacionGuia, Ruta
from userauths.models import Usuario
from .utils import enviar_correo_reservacion, medir_tiempo

from django.http import HttpResponse



stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def habitacion_disponible(request):

    if request.method == "POST":
        id = request.POST.get("alojamiento-id")
        fecha_ingreso = request.POST.get("fecha_ingreso")
        fecha_salida = request.POST.get("fecha_salida")
        num_adultos = request.POST.get("num_adultos")
        num_ninos = request.POST.get("num_ninos")
        alojamiento_tipo = request.POST.get("alojamiento-tipo")

        alojamiento = Alojamiento.objects.get(id=id)
        alojamiento_tipo_obj = TipoAlojamiento.objects.get(
            alojamiento=alojamiento, pk=alojamiento_tipo)

        # Debugging output
        print("id ====== ", id)
        print("fecha_ingreso =========", fecha_ingreso)
        print("fecha_salida =========", fecha_salida)
        print("num adultos =========", num_adultos)
        print("num niños =========", num_ninos)
        print("alojamiento_tipo =========", alojamiento_tipo_obj)

        try:
            # Construir la URL con reverse
            url = reverse("alojamiento:tipos_alojamiento_detalle", args=[
                          alojamiento.pk, alojamiento_tipo_obj.pk])

            # Redirigir a la URL con los parámetros necesarios
            url_params = f"{url}?alojamiento-id={id}&fecha_ingreso={fecha_ingreso}&fecha_salida={fecha_salida}&num_adultos={num_adultos}&num_ninos={num_ninos}&alojamiento_tipo={alojamiento_tipo_obj.pk}"
            return HttpResponseRedirect(url_params)
        except Exception as e:
            print(f"Error al construir la URL: {str(e)}")



def add_selecion(request):
    habitacion_selecion = {}

    habitacion_selecion[str(request.GET[id])] = {
        'alojamiento_id': request.GET['alojamiento_id'],
        'alojamiento_nombre': request.GET['alojamiento_nombre'],
        'habitacion_nombre': request.GET['habitacion_nombre'],
        'habitacion_precio': request.GET['habitacion_precio'],
        'numero_camas': request.GET['numero_camas'],
        'num_habitacion': request.GET['num_habitacion'],
        'habitacion_tipo': request.GET['habitacion_tipo'],
        'habitacion_id': request.GET['habitacion_id'],
        'fecha_ingreso': request.GET['fecha_ingreso'],
        'fecha_salida': request.GET['fecha_salida'],
        'num_ninos': request.GET['num_ninos'],
        'num_adultos': request.GET['num_adultos'],
    }
    if 'selecion_data_obj' in request.session:
        if str(request.GET['id']) in request.session['selecion_data_obj']:
            selecion_data = request.session['selecion_data_obj']
            selecion_data[str(request.GET['id'])]['num_adultos'] = int(
                habitacion_selecion)[str(request.GET['id'])]['num_adultos']
            selecion_data[str(request.GET['id'])]['num_ninos'] = int(
                habitacion_selecion)[str(request.GET['id'])]['num_ninos']
            request.session['selecion_data_obj'] = selecion_data
        else:
            selecion_data = request.session['selecion_data_obj']
            selecion_data.update(habitacion_selecion)

    else:
        request.session['selecion_data_obj'] = habitacion_selecion

    data = {
        "data": request.session['selecion_data_obj'],
        "total_selecion_items": request.session['selecion_data_obj']

    }
    return JsonResponse(data)

def mi_reserva(request):
    habitacion_id = request.GET.get('habitacion_id')
    num_habitacion = request.GET.get('num_habitacion')

    habitacion = get_object_or_404(Habitacion, id=habitacion_id)

    tipo_alojamiento = habitacion.alojamiento_tipo
    alojamiento = tipo_alojamiento.alojamiento
    precio = Decimal(tipo_alojamiento.precio)
    precio = tipo_alojamiento.precio

    context = {
        'habitacion_id': habitacion_id,
        'num_habitacion': num_habitacion,
        'habitacion': habitacion,
        'tipo_alojamiento': tipo_alojamiento,
        'alojamiento': alojamiento,
        'precio': precio,
        'precio_str': str(precio),

    }

    return render(request, "reservacion/mi-reserva.html", context)


@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            intent = stripe.PaymentIntent.create(
                amount=int(data['amount']),
                currency='usd',
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_image_url = f"{settings.DOMAIN}{data['product_image']}"  # verificar si es necesario
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': data['product_name'],
                                'images': [data['product_image']],
                            },
                            'unit_amount': data['amount'],
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f"{settings.DOMAIN}/reservacion/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.DOMAIN}/reservacion/payment-cancel/",
                metadata={
                    'user_id': str(request.user.id),
                    'alojamiento_id': str(data['alojamiento_id']),
                    'habitacion_tipo_id': str(data['habitacion_tipo_id']),
                    'habitacion_ids': json.dumps(data['habitacion_ids']),
                    'fecha_ingreso': data['fecha_ingreso'],
                    'fecha_salida': data['fecha_salida'],
                    'num_adultos': str(data['num_adultos']),
                    'num_ninos': str(data['num_ninos'])
                }
            )
            return JsonResponse({'url': checkout_session.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@medir_tiempo
def payment_success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    # Aquí obtenemos los metadatos de la sesión para crear la Reservacion
    user_id = session.metadata.user_id
    alojamiento_id = session.metadata.alojamiento_id
    habitacion_tipo_id = session.metadata.habitacion_tipo_id
    habitacion_ids = json.loads(session.metadata.habitacion_ids)
    total = session.amount_total / 100  # Stripe amounts are in cents
    fecha_ingreso = session.metadata.fecha_ingreso
    fecha_salida = session.metadata.fecha_salida
    num_adultos = session.metadata.num_adultos
    num_ninos = session.metadata.num_ninos
    pago_id = session.payment_intent
    
    
    habitacion_id = json.loads(session.metadata.habitacion_ids)  # Asumiendo que solo hay una habitación
    
    
    # Crear el objeto Reservacion
    reservacion = Reservacion.objects.create(
        user_id=user_id,
        estado_pago='Pagado',
        alojamiento_id=alojamiento_id,
        habitacion_tipo_id=habitacion_tipo_id,
        total=total,
        fecha_ingreso=fecha_ingreso,
        fecha_salida=fecha_salida,
        num_adultos=num_adultos,
        num_ninos=num_ninos,
        estado=True,
        pago_id=pago_id
    )
    
    
    actualizar_disponibilidad_habitacion(habitacion_id)

    # Añadir las habitaciones
    reservacion.habitacion.add(habitacion_ids)
    
    reservacion.save()

    # Enviar correo de confirmación
    user = Usuario.objects.get(id=user_id)
    enviar_correo_reservacion(user, reservacion, 'alojamiento')

    return render(request, 'reservacion/success.html')

def actualizar_disponibilidad_habitacion(habitacion_id):
    try:
        habitacion = get_object_or_404(Habitacion, id=habitacion_id)
        habitacion.disponible = False
        habitacion.save()
        print(f"Disponibilidad de la habitación {habitacion_id} actualizada a False")
        return True
    except Exception as e:
        print(f"Error al actualizar la disponibilidad de la habitación {habitacion_id}: {str(e)}")
        return False



def payment_cancel(request):
    return render(request, 'reservacion/cancel.html')



@csrf_exempt
def create_checkout_session_2(request):
    print("Request method:", request.method)
    if request.user.is_authenticated:
        print("User ID:", request.user.id)
    else:
        print("User not authenticated")

    if request.method == 'POST':
        data = json.loads(request.body)
        print("Received data:", data)
        if 'ruta_id' not in data:
            return JsonResponse({'error': 'Missing ruta_id'}, status=400)

        try:
            product_image_url = f"{settings.DOMAIN}{data['product_image']}"
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': data['product_name'],
                                'images': [data['product_image']],
                            },
                            'unit_amount': data['amount'],
                        },
                        'quantity': data['num_person'],
                    },
                ],
                mode='payment',
                success_url=f"{settings.DOMAIN}/reservacion/payment-success-2/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.DOMAIN}/reservacion/payment-cancel/",
                metadata={
                    'user_id': str(request.user.id),
                    'ruta_id': str(data['ruta_id']),
                    'fecha_reserva': data['fecha'],
                    'num_personas': str(data['num_person']),
                    'total': str(float(data['amount']) * int(data['num_person']) / 100)
                }
            )
            return JsonResponse({'url': checkout_session.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return JsonResponse({'error': 'Invalid request method'}, status=400)



def payment_success_2(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    # Obtener los metadatos de la sesión
    user_id = session.metadata.user_id
    ruta_id = session.metadata.ruta_id
    fecha_reserva = session.metadata.fecha_reserva
    num_personas = session.metadata.num_personas
    total = session.metadata.total
    pago_id = session.payment_intent

    # Crear la reservación
    user = Usuario.objects.get(id=user_id)
    ruta = Ruta.objects.get(id=ruta_id)
    guia = ruta.guias.first()  # Ajusta esto según cómo seleccionas la guía turística

    reservacion = ReservacionGuia.objects.create(
        user=user,
        guia=guia,
        ruta=ruta,
        fecha_reserva=fecha_reserva,
        num_personas=num_personas,
        estado_pago='Pagado',
        total=total,
        pago_id=pago_id
    )
    guia.estado = "Reservado"
    guia.save()

    # Enviar correo de confirmación
    enviar_correo_reservacion(user, reservacion, 'guia')

    return render(request, 'reservacion/success.html')


def payment_cancel(request):
    return render(request, 'reservacion/cancel.html')


def mis_reservas(request):
    reservaciones = Reservacion.objects.filter(user=request.user)
    reservaciones_guias = ReservacionGuia.objects.filter(user=request.user)

    context = {
        'reservaciones': reservaciones,
        'reservaciones_guias': reservaciones_guias
    }

    return render(request, 'reservacion/mis-reservas.html', context)

from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from io import BytesIO

def generar_ticket(reservacion):
    buffer = BytesIO()
    width, height = 9.5 * cm, 20 * cm  # Tamaño del ticket
    
    styles = getSampleStyleSheet()
    custom_styles = {
        'Title': ParagraphStyle(name='Title', parent=styles['Title'], alignment=1, fontSize=12, leading=14, spaceAfter=6),
        'Subtitle': ParagraphStyle(name='Subtitle', parent=styles['Normal'], alignment=1, fontSize=10, leading=12, spaceAfter=4),
        'BodyText': ParagraphStyle(name='BodyText', parent=styles['Normal'], alignment=0, fontSize=9, leading=10, spaceAfter=4),
        'SmallText': ParagraphStyle(name='SmallText', parent=styles['Normal'], fontSize=8, leading=9, spaceAfter=2),
    }

    # Cálculo de días de estancia
    dias_estancia = (reservacion.fecha_salida - reservacion.fecha_ingreso).days
    
    doc = SimpleDocTemplate(buffer, pagesize=(width, height), topMargin=3*mm, bottomMargin=3*mm, leftMargin=3*mm, rightMargin=3*mm)
    
    elements = []

    # Encabezado
    elements.append(Paragraph("Ticket de Reservación", custom_styles['Title']))
    elements.append(Spacer(1, 3*mm))

    # Información del usuario
    elements.append(Paragraph(f"Usuario: {reservacion.user.username}", custom_styles['BodyText']))
    elements.append(Paragraph(f"Nombre: {reservacion.user.full_name}", custom_styles['BodyText']))
    elements.append(Paragraph(f"Teléfono: {reservacion.user.telefono}", custom_styles['BodyText']))
    elements.append(Spacer(1, 3*mm))

    # Línea separadora
    elements.append(Paragraph("-" * 90, custom_styles['SmallText']))
    elements.append(Spacer(1, 1*mm))

    # Información de la reservación
    info_reserva = [
        ["Reserva ID:", str(reservacion.id)],
        ["Pago ID:", reservacion.pago_id or "N/A"],
        ["Estado:", reservacion.estado_pago],
        ["Alojamiento:", reservacion.alojamiento.nombre],
        ["Tipo Habitación:", reservacion.habitacion_tipo.tipo],
        ["Ingreso:", reservacion.fecha_ingreso.strftime("%d/%m/%Y")],
        ["Salida:", reservacion.fecha_salida.strftime("%d/%m/%Y")],
        ["Adultos:", str(reservacion.num_adultos)],
        ["Niños:", str(reservacion.num_ninos)],
    ]
    
    t_info_reserva = Table(info_reserva, colWidths=[2.5*cm, 6.5*cm])
    t_info_reserva.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_info_reserva)
    elements.append(Spacer(1, 3*mm))

    # Línea separadora
    elements.append(Paragraph("-" * 90, custom_styles['SmallText']))
    elements.append(Spacer(1, 2*mm))

    # Habitaciones reservadas
    elements.append(Paragraph("Detalle de Habitaciones:", custom_styles['Subtitle']))

    info_habitaciones = [['N° Habitación', 'Precio por Día', 'Días', 'Precio Total']]
    total = 0
    for habitacion in reservacion.habitacion.all():
        precio_unitario = habitacion.precio()
        precio_total = precio_unitario * dias_estancia
        total += precio_total
        info_habitaciones.append([f"{habitacion.numero_habitacion}", f"${precio_unitario:.2f}", str(dias_estancia), f"${precio_total:.2f}"])
    
    t_habitaciones = Table(info_habitaciones, colWidths=[2.5*cm, 2.5*cm, 1.5*cm, 2.5*cm])
    t_habitaciones.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_habitaciones)
    elements.append(Spacer(1, 3*mm))

    # Descripciones de las habitaciones
    for habitacion in reservacion.habitacion.all():
        if habitacion.descripcion:
            elements.append(Paragraph(f"Descripción: {habitacion.descripcion}", custom_styles['SmallText']))
            elements.append(Spacer(1, 2*mm))

    # Línea separadora
    elements.append(Paragraph("-" * 90, custom_styles['SmallText']))
    elements.append(Spacer(1, 2*mm))

    # Total
    elements.append(Paragraph(f"Total: ${total:.2f}", custom_styles['BodyText']))
    elements.append(Paragraph(f"Fecha de reserva: {reservacion.fecha.strftime('%d/%m/%Y')}", custom_styles['BodyText']))

    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Gracias por su reserva", custom_styles['Subtitle']))

    # Generar PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf



def descargar_ticket(request, reserva_id):
    reserva = get_object_or_404(Reservacion, id=reserva_id)
    pdf = generar_ticket(reserva)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_reserva_{reserva_id}.pdf"'
    return response


# ---------------------------------------------------------

def generar_ticket_guia(reservacion):
    buffer = BytesIO()
    width, height = 9.5 * cm, 20 * cm  # Tamaño del ticket
    
    styles = getSampleStyleSheet()
    custom_styles = {
        'Title': ParagraphStyle(name='Title', parent=styles['Title'], alignment=1, fontSize=12, leading=14, spaceAfter=6),
        'Subtitle': ParagraphStyle(name='Subtitle', parent=styles['Normal'], alignment=1, fontSize=10, leading=12, spaceAfter=4),
        'BodyText': ParagraphStyle(name='BodyText', parent=styles['Normal'], alignment=0, fontSize=9, leading=10, spaceAfter=4),
        'SmallText': ParagraphStyle(name='SmallText', parent=styles['Normal'], fontSize=8, leading=9, spaceAfter=2),
    }
    
    doc = SimpleDocTemplate(buffer, pagesize=(width, height), topMargin=3*mm, bottomMargin=3*mm, leftMargin=3*mm, rightMargin=3*mm)
    
    elements = []

    # Encabezado
    elements.append(Paragraph("Ticket de Reservación de Guía", custom_styles['Title']))
    elements.append(Spacer(1, 3*mm))

    # Información del usuario
    elements.append(Paragraph(f"Usuario: {reservacion.user.username}", custom_styles['BodyText']))
    elements.append(Paragraph(f"Nombre: {reservacion.user.full_name}", custom_styles['BodyText']))
    elements.append(Paragraph(f"Teléfono: {reservacion.user.telefono}", custom_styles['BodyText']))
    elements.append(Spacer(1, 3*mm))

    # Línea separadora
    elements.append(Paragraph("-" * 90, custom_styles['SmallText']))
    elements.append(Spacer(1, 1*mm))

    # Información de la reservación
    info_reserva = [
        ["Reserva ID:", str(reservacion.id)],
        ["Pago ID:", reservacion.pago_id or "N/A"],
        ["Estado:", reservacion.estado_pago],
        ["Guía:", reservacion.guia.nombre],
        ["Ruta:", reservacion.ruta.nombre],
        ["Fecha Reserva:", reservacion.fecha_reserva.strftime("%d/%m/%Y")],
        ["Nº Personas:", str(reservacion.num_personas)],
    ]
    
    t_info_reserva = Table(info_reserva, colWidths=[2.5*cm, 6.5*cm])
    t_info_reserva.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_info_reserva)
    elements.append(Spacer(1, 3*mm))

    # Línea separadora
    elements.append(Paragraph("-" * 90, custom_styles['SmallText']))
    elements.append(Spacer(1, 2*mm))

    # Detalles del Guía
    elements.append(Paragraph("Detalles del Guía:", custom_styles['Subtitle']))
    info_guia = [
        ["Nombre:", reservacion.guia.nombre],
        ["Email:", reservacion.guia.email],
        ["Teléfono:", reservacion.guia.telefono],
    ]
    t_guia = Table(info_guia, colWidths=[2.5*cm, 6.5*cm])
    t_guia.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_guia)
    elements.append(Spacer(1, 3*mm))

    # Detalles de la Ruta
    elements.append(Paragraph("Detalles de la Ruta:", custom_styles['Subtitle']))
    info_ruta = [
        ["Nombre:", reservacion.ruta.nombre],
        ["Precio:", f"${reservacion.ruta.precio:.2f}"],
        ["Capacidad:", str(reservacion.ruta.capacidad)],
    ]
    t_ruta = Table(info_ruta, colWidths=[2.5*cm, 6.5*cm])
    t_ruta.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_ruta)
    elements.append(Spacer(1, 2*mm))

    elements.append(Paragraph(f"Descripción de la Ruta: {reservacion.ruta.descripcion}", custom_styles['SmallText']))
    elements.append(Spacer(1, 3*mm))

    # Línea separadora
    elements.append(Paragraph("-" * 90, custom_styles['SmallText']))
    elements.append(Spacer(1, 2*mm))

    # Total
    elements.append(Paragraph(f"Total: ${reservacion.total:.2f}", custom_styles['BodyText']))
    elements.append(Paragraph(f"Fecha de reserva: {reservacion.fecha_creacion.strftime('%d/%m/%Y %H:%M')}", custom_styles['BodyText']))

    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Gracias por su reserva", custom_styles['Subtitle']))

    # Generar PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def descargar_ticket_guia(request, reserva_id):
    reserva = get_object_or_404(ReservacionGuia, id=reserva_id)
    pdf = generar_ticket_guia(reserva)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_reserva_guia_{reserva_id}.pdf"'
    return response