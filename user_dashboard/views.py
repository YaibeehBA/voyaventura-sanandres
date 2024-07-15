from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Sum
from .forms import ReporteAlojamientoForm, ReporteGuiaForm
from alojamiento.models import Reservacion, Alojamiento
from guias.models import ReservacionGuia
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView

@login_required(login_url="/admin/login/")
def generar_reporte_alojamiento(request):
    if request.method == 'POST':
        form = ReporteAlojamientoForm(request.POST)
        if form.is_valid():
            alojamiento = form.cleaned_data['alojamiento']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']

            reservaciones = Reservacion.objects.filter(
                alojamiento=alojamiento,
                fecha_ingreso__range=[fecha_inicio, fecha_fin]
            ).order_by('fecha_ingreso')

            total_general = reservaciones.aggregate(Sum('total'))['total__sum'] or 0

            usuario_generador = request.user.full_name or request.user.username

            context = {
                'alojamiento': alojamiento,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'reservaciones': reservaciones,
                'total_general': total_general,
                'usuario_generador': usuario_generador
            }

            if 'vista_previa' in request.POST:
                template = get_template('reportes/reporte_alojamiento.html')
                html = template.render(context)
                return JsonResponse({'html': html})

            if 'generar_pdf' in request.POST:
                template = get_template('reportes/reporte_alojamiento.html')
                html = template.render(context)

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename=reporte_{alojamiento.nombre}.pdf'

                pdf_options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                }

                pisa_status = pisa.CreatePDF(html, dest=response, options=pdf_options)
                if pisa_status.err:
                    return HttpResponse('Hubo un error al generar el PDF', status=500)

                return response
    else:
        form = ReporteAlojamientoForm()
    alojamientos = Alojamiento.objects.all()

    return render(request, 'reportes/generar_reporte.html', {'form': form, 'alojamientos': alojamientos})




@login_required(login_url="/admin/login/")
def generar_reporte_guia(request):
    if request.method == 'POST':
        form = ReporteGuiaForm(request.POST)
        if form.is_valid():
            guia = form.cleaned_data['guia']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']

            reservaciones = ReservacionGuia.objects.filter(
                guia=guia,
                fecha_reserva__range=[fecha_inicio, fecha_fin]
            ).order_by('fecha_reserva')

            total_general = reservaciones.aggregate(Sum('total'))['total__sum'] or 0

            context = {
                'guia': guia,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'reservaciones': reservaciones,
                'total_general': total_general,
                'usuario_generador': request.user.full_name or request.user.username
            }

            if 'vista_previa' in request.POST:
                template = get_template('reportes/reporte_guia.html')
                html = template.render(context)
                return JsonResponse({'html': html})

            if 'generar_pdf' in request.POST:
                template = get_template('reportes/reporte_guia.html')
                html = template.render(context)

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename=reporte_{guia.nombre}.pdf'

                pdf_options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                }

                pisa_status = pisa.CreatePDF(html, dest=response, options=pdf_options)
                if pisa_status.err:
                    return HttpResponse('Hubo un error al generar el PDF', status=500)

                return response
    else:
        form = ReporteGuiaForm()
    
    return render(request, 'reportes/generar_reporte_guia.html', {'form': form})



# def generar_reporte_alojamiento(request):
#     if request.method == 'POST':
#         form = ReporteAlojamientoForm(request.POST)
#         if form.is_valid():
#             alojamiento = form.cleaned_data['alojamiento']
#             fecha_inicio = form.cleaned_data['fecha_inicio']
#             fecha_fin = form.cleaned_data['fecha_fin']

#             reservaciones = Reservacion.objects.filter(
#                 alojamiento=alojamiento,
#                 fecha_ingreso__range=[fecha_inicio, fecha_fin]
#             ).order_by('fecha_ingreso')

#             total_general = reservaciones.aggregate(Sum('total'))['total__sum'] or 0

#             context = {
#                 'alojamiento': alojamiento,
#                 'fecha_inicio': fecha_inicio,
#                 'fecha_fin': fecha_fin,
#                 'reservaciones': reservaciones,
#                 'total_general': total_general,
#                 'usuario_generador': request.user.full_name or request.user.username  # Nombre del usuario que genera el reporte
#             }

#             template = get_template('reportes/reporte_alojamiento.html')
#             html = template.render(context)

#             # Crear el PDF
#             response = HttpResponse(content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename=reporte_{alojamiento.nombre}.pdf'

#             pdf_options = {
#                 'page-size': 'A4',
#                 'margin-top': '0.75in',
#                 'margin-right': '0.75in',
#                 'margin-bottom': '0.75in',
#                 'margin-left': '0.75in',
#             }


#             # Generar PDF
#             pisa_status = pisa.CreatePDF(html, dest=response, options=pdf_options)
#             if pisa_status.err:
#                 return HttpResponse('Hubo un error al generar el PDF', status=500)
            
#             return response
#     else:
#         form = ReporteAlojamientoForm()

#     return render(request, 'reportes/generar_reporte.html', {'form': form})



# # def generar_reporte_alojamiento(request):
#     if request.method == 'POST':
#         form = ReporteAlojamientoForm(request.POST)
#         if form.is_valid():
#             alojamiento = form.cleaned_data['alojamiento']
#             fecha_inicio = form.cleaned_data['fecha_inicio']
#             fecha_fin = form.cleaned_data['fecha_fin']

#             reservaciones = Reservacion.objects.filter(
#                 alojamiento=alojamiento,
#                 fecha_ingreso__range=[fecha_inicio, fecha_fin]
#             ).order_by('fecha_ingreso')

#             # Crear PDF
#             buffer = BytesIO()
#             p = canvas.Canvas(buffer, pagesize=landscape(letter))
#             width, height = landscape(letter)

#             p.setFont("Helvetica-Bold", 16)
#             p.drawString(30, height - 30, f"Reporte de Reservaciones - {alojamiento.nombre}")
#             p.setFont("Helvetica", 12)
#             p.drawString(30, height - 50, f"Periodo: {fecha_inicio} a {fecha_fin}")

#             data = [['Cliente', 'Fecha Ingreso', 'Fecha Salida', 'Tipo Habitación', 'Total']]
#             total_general = 0

#             for reserva in reservaciones:
#                 # Usar full_name si está disponible, de lo contrario usar username
#                 nombre_cliente = reserva.user.full_name if reserva.user.full_name else reserva.user.username
#                 data.append([
#                     nombre_cliente,
#                     reserva.fecha_ingreso.strftime('%d/%m/%Y'),
#                     reserva.fecha_salida.strftime('%d/%m/%Y'),
#                     reserva.habitacion_tipo.tipo,
#                     f"${reserva.total:.2f}"
#                 ])
#                 total_general += reserva.total

#             data.append(['', '', '', 'Total General', f"${total_general:.2f}"])

#             table = Table(data)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 12),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
#                 ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
#                 ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 1), (-1, -1), 10),
#                 ('TOPPADDING', (0, 1), (-1, -1), 6),
#                 ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black)
#             ]))

#             table.wrapOn(p, width - 60, height)
#             table.drawOn(p, 30, height - 100 - len(data)*20)

#             p.showPage()
#             p.save()

#             buffer.seek(0)
#             response = HttpResponse(content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename=reporte_{alojamiento.nombre}.pdf'
#             response.write(buffer.getvalue())
#             buffer.close()
#             return response
#     else:
#         form = ReporteAlojamientoForm()

#     return render(request, 'reportes/generar_reporte.html', {'form': form})

# user_dashboard/views.py

