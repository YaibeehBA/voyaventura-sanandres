# utils.py o en cualquier archivo de utilidad
from django.core.mail import send_mail
from django.conf import settings
import time
from functools import wraps

def medir_tiempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tiempo_inicio = time.time()
        resultado = func(*args, **kwargs)
        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio
        print(f"Tiempo de ejecución de {func.__name__}: {tiempo_total:.4f} segundos")
        return resultado
    return wrapper

@medir_tiempo
def enviar_correo_reservacion(usuario, reservacion, tipo):
    if tipo == 'alojamiento':
        subject = 'Confirmación de Reservación de Alojamiento'
        message = f'Hola {usuario.username},\n\nTu reservación para {reservacion.alojamiento.nombre} ha sido confirmada.\n\nDetalles:\nFecha de Ingreso: {reservacion.fecha_ingreso}\nFecha de Salida: {reservacion.fecha_salida}\nTotal: ${reservacion.total}\n\nGracias por reservar con nosotros.'
    elif tipo == 'guia':
        subject = 'Confirmación de Reservación de Guía Turístico'
        message = f'Hola {usuario.username},\n\nTu reservación para {reservacion.ruta.nombre} ha sido confirmada.\n\nDetalles:\nFecha de Reserva: {reservacion.fecha_reserva}\nNúmero de Personas: {reservacion.num_personas}\nTotal: ${reservacion.total}\n\nGracias por reservar con nosotros.'
    
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [usuario.email]
    send_mail(subject, message, email_from, recipient_list)