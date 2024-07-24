from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from alojamiento.models import Alojamiento,TipoAlojamiento,GaleriaAlojamiento ,Habitacion, Reservacion
from guias.models import GuiaTuristico, Ruta
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max, Count
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from userauths.models import MensajeUsuario

from san_andres import settings
import openai

def index(request):
    alojamiento = Alojamiento.objects.filter(estado="Aprobado")[:3]
    guiaturisticos = GuiaTuristico.objects.filter(
    Q(estado="Aprobado") | Q(estado="Disponible")
    )
    
    context = {
        "alojamiento": alojamiento,
        "guiaturisticos": guiaturisticos,  # Pasamos los guías turísticos al contexto
    }
    return render(request, "alojamiento/alojamiento.html", context)


def alojamiento_detalle(request, pk):
    alojamiento = Alojamiento.objects.get(estado="Aprobado", pk=pk)
    context = {
        "alojamiento": alojamiento,
    }
    return render(request, "alojamiento/alojamiento_detalle.html", context)


    
@login_required(login_url="userauths:sign-in")
def tipos_alojamiento_detalle(request, pk, ta_pk):
    alojamiento = Alojamiento.objects.get(estado="Aprobado", pk=pk)
    tipos_alojamiento = TipoAlojamiento.objects.get(alojamiento=alojamiento, pk=ta_pk)
    habitaciones = Habitacion.objects.filter(alojamiento_tipo=tipos_alojamiento, disponible=True)
    
    id= request.GET.get("alojamiento-id")
    fecha_ingreso = request.GET.get("fecha_ingreso")
    fecha_salida = request.GET.get("fecha_salida")
    num_adultos = request.GET.get("num_adultos")
    num_ninos = request.GET.get("num_ninos")

    

    context = {
        "alojamiento": alojamiento,
        "tipos_alojamiento": tipos_alojamiento,
        "habitaciones": habitaciones,
        "fecha_ingreso": fecha_ingreso,
        "fecha_salida": fecha_salida,
        "num_adultos": num_adultos,
        "num_ninos": num_ninos,
    }
    return render(request, "alojamiento/tipos_alojamiento_detalle.html", context)

def ver_alojamientos_detalle(request):
    alojamientos = Alojamiento.objects.filter(estado="Aprobado")
    applied_filters = False
    page  = request.GET.get('page',1)

    # Obtener parámetros de filtro
    precio_max = request.GET.get('precio_max')
    num_camas = request.GET.get('num_camas')
    capacidad = request.GET.get('capacidad')
    mas_reservas = request.GET.get('mas_reservas')

    # Aplicar filtros
    if precio_max and precio_max.strip():
        alojamientos = alojamientos.filter(tipoalojamiento__precio__lte=float(precio_max))
        applied_filters = True

    if num_camas and num_camas.strip():
        alojamientos = alojamientos.filter(tipoalojamiento__numero_camas__gte=int(num_camas))
        applied_filters = True

    if capacidad and capacidad.strip():
        alojamientos = alojamientos.filter(tipoalojamiento__capacidad__gte=int(capacidad))
        applied_filters = True

    # Ordenar por más reservas si está activado el filtro
    if mas_reservas:
        alojamientos = alojamientos.annotate(num_reservas=Count('reservacion')).order_by('-num_reservas')
        applied_filters = True

    # Anotar campos adicionales
    alojamientos = alojamientos.annotate(
        precio_min=Min('tipoalojamiento__precio'),
        precio_max=Max('tipoalojamiento__precio'),
        max_capacidad=Max('tipoalojamiento__capacidad'),
        max_camas=Max('tipoalojamiento__numero_camas'),
        num_reservas=Count('reservacion')
    ).distinct()

    # Verificar si no hay resultados después de aplicar filtros
    if applied_filters and not alojamientos.exists():
        messages.warning(request, "No se encontraron resultados para los filtros seleccionados.")
        return redirect(reverse('alojamiento:ver_alojamientos_detalle'))
    
    # paginado 
    try:
         paginator = Paginator(alojamientos,3)
         alojamientos = paginator.page(page)
    except:
         raise Http404
    context = {
        "alojamientos": alojamientos,
        "paginator":paginator,
    }

    return render(request, "alojamiento/ver_alojamientos.html", context)




@csrf_exempt
def webhook(request):
    try:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        action = body['queryResult'].get('action')
        event = body['queryResult'].get('queryText')  # El evento se recibe en queryText cuando se activa por un chip
        parameters = body['queryResult']['parameters']

        # Punto de interrupción para inspeccionar la acción y el evento
        print(f"Action: {action}, Event: {event}")
        
        
        if action == 'input.welcome':
            return bienvenida(request) 
        elif action == 'get_alojamiento':
            return get_alojamiento(request)
        elif action == 'info_alojamiento' or event == 'detalle_alojamiento':
            nombre_alojamiento = parameters.get('alojamiento')
            print(f"Nombre del Alojamiento consultado: {nombre_alojamiento}")
            return get_info_alojamiento(request, nombre_alojamiento)
        elif action == 'get_guias':
            return get_guias(request)
        elif action == 'get_detalles_guias'or event == 'detalle_guia' :
            nombre_guia = parameters.get('nombre_guia')
            print(f"Nombre del Guía consultado: {nombre_guia}")
            return get_info_guia(request, nombre_guia)
        elif action == 'responder_pregunta' :
             return responder_pregunta_especifica(request, body)
        elif action == 'capturar_mensaje_usuario':
            return capturar_mensaje_usuario(request, parameters)
        
        elif action == 'capturar_precio':
            return capturar_precio(request, parameters)
       

        elif action == 'mostrar_menu':
            return mostrar_menu(request)
        else:
            return JsonResponse({'fulfillmentText': 'No se pudo procesar la acción solicitada.'})
    except Exception as e:
        print(f"Error en webhook: {str(e)}")
        return JsonResponse({'fulfillmentText': 'Ocurrió un error procesando la solicitud.'})
    # https://voyaventura-san-andres.up.railway.app/webhook/

import time
from functools import wraps

def medir_tiempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        tiempo_transcurrido = fin - inicio
        print(f"Tiempo de {func.__name__}: {tiempo_transcurrido} segundos")
        return resultado
    return wrapper

# @medir_tiempo
# def get_info_alojamiento(request, nombre_alojamiento):
#     try:
#         alojamiento = Alojamiento.objects.filter(
#             Q(nombre__icontains=nombre_alojamiento) & Q(estado="Aprobado")
#         ).first()
        
#         if alojamiento:
#             print(f"Alojamiento encontrado: {alojamiento.nombre}")
#             response = {
#                 "fulfillmentMessages": [
#                     {
#                         "payload": {
#                             "richContent": [
#                                 [
#                                     {
#                                         "type": "info",
#                                         "title": alojamiento.nombre,
#                                         "subtitle": f"Dirección: {alojamiento.direccion}",
#                                         "image": {
#                                             "src": {
#                                                 "rawUrl": request.build_absolute_uri(alojamiento.imagen.url)
#                                             }
#                                         },
#                                         "actionLink": f"{settings.DOMAIN}/detalle/{alojamiento.id}"
#                                     }
#                                 ]
#                             ]
#                         }
#                     },
#                     {
#                         "text": {
#                             "text": [
#                                 f"Teléfono: {alojamiento.celular}",
#                                 f"Descripción: {alojamiento.descripcion}"
#                             ]
#                         }
#                     }
#                 ]
#             }
#         else:
#             print(f"No se encontró alojamiento para: {nombre_alojamiento}")
#             response = {
#                 "fulfillmentMessages": [
#                     {
#                         "text": {
#                             "text": ["Lo siento, no pude encontrar información sobre ese alojamiento."]
#                         }
#                     }
#                 ]
#             }
#     except Exception as e:
#         print(f"Error en get_info_alojamiento: {str(e)}")
#         response = {
#             "fulfillmentMessages": [
#                 {
#                     "text": {
#                         "text": ["Ocurrió un error al buscar la información del alojamiento."]
#                     }
#                 }
#             ]
#         }

    
    
#     return JsonResponse(response)


def get_info_alojamiento(request, nombre_alojamiento):
    try:
        alojamiento = Alojamiento.objects.filter(
            Q(nombre__icontains=nombre_alojamiento) & Q(estado="Aprobado")
        ).first()
        
        if alojamiento:
            print(f"Alojamiento encontrado: {alojamiento.nombre}")
            response = {
                "fulfillmentMessages": [
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "info",
                                        "title": alojamiento.nombre,
                                        "subtitle": f"Dirección: {alojamiento.direccion}",
                                        "image": {
                                            "src": {
                                                "rawUrl": request.build_absolute_uri(alojamiento.imagen.url)
                                            }
                                        },
                                        "actionLink": f"{settings.DOMAIN}/detalle/{alojamiento.id}"
                                    }
                                ]
                            ]
                        }
                    },
                    {
                        "text": {
                            "text": [
                                f"Teléfono: {alojamiento.celular}",
                                f"Descripción: {alojamiento.descripcion}"
                            ]
                        }
                    },
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "chips",
                                        "options": [
                                            {
                                                "text": "Volver al Menú Principal",
                                                "postback": "mostrar_menu"
                                            }
                                        ]
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
        else:
            print(f"No se encontró alojamiento para: {nombre_alojamiento}")
            response = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": ["Lo siento, no pude encontrar información sobre ese alojamiento."]
                        }
                    },
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "chips",
                                        "options": [
                                            {
                                                "text": "Volver al Menú Principal",
                                                "postback": "mostrar_menu"
                                            }
                                        ]
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
    except Exception as e:
        print(f"Error en get_info_alojamiento: {str(e)}")
        response = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["Ocurrió un error al buscar la información del alojamiento."]
                    }
                },
                {
                    "payload": {
                        "richContent": [
                            [
                                {
                                    "type": "chips",
                                    "options": [
                                        {
                                            "text": "Volver al Menú",
                                            "postback": "mostrar_menu"
                                        }
                                    ]
                                }
                            ]
                        ]
                    }
                }
            ]
        }

    return JsonResponse(response)


@medir_tiempo
def get_alojamiento(request):
    alojamientos = Alojamiento.objects.filter(estado="Aprobado")
    
    response = {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": ["Estos son los alojamientos disponibles selecciona uno:"]
                }
            },
            {
                "payload": {
                    "richContent": [
                        [
                            {
                                "type": "chips",
                                "options": []
                            }
                        ]
                    ]
                }
            }
        ]
    }

    for alojamiento in alojamientos:
        response["fulfillmentMessages"][1]["payload"]["richContent"][0][0]["options"].append({
            "text": alojamiento.nombre,
            "image": {
                "src": {
                    "rawUrl": request.build_absolute_uri(alojamiento.imagen.url)
                }
            },
            "event": {
                "name": "detalle_alojamiento",
                "languageCode": "es",
                "parameters": {
                    "nombre_alojamiento": alojamiento.nombre
                }
            }
        })
   
    response["fulfillmentMessages"][1]["payload"]["richContent"][0][0]["options"].append({
        "text": "Volver al Menú ",
        "postback": "mostrar_menu"
    })
    return JsonResponse(response)

@medir_tiempo
def get_guias(request):
    guias = GuiaTuristico.objects.filter( Q(estado="Aprobado") | Q(estado="Disponible"))

    # Inicializamos el mensaje de respuesta
    response = {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": ["Estos son los guías turísticos disponibles:"]
                }
            },
            {
                "payload": {
                    "richContent": [[]]
                }
            }
        ]
    }

    # Construimos el mensaje con la lista de guías
    for guia in guias:
        card = {
            "type": "info",
            "title": guia.nombre,
            "subtitle": f"Teléfono: {guia.telefono}",
            "image": {
                "src": {
                    "rawUrl": request.build_absolute_uri(guia.foto.url) if guia.foto else ""
                }
            },
            "actionLink": f"{settings.DOMAIN}/guias/guia/{guia.id}/rutas/"  # Ajusta el enlace según sea necesario
        }
        response["fulfillmentMessages"][1]["payload"]["richContent"][0].append(card)
    
    # Añadimos la instrucción final
    final_message = {
        "type": "info",
        "title": "Información adicional",
        "subtitle": "Si desea saber más sobre un guía específico, escriba 'guía' seguido del nombre del guía."
    }
    response["fulfillmentMessages"][1]["payload"]["richContent"][0].append(final_message)
    response["fulfillmentMessages"].append({
        "payload": {
            "richContent": [
                [
                    {
                        "type": "chips",
                        "options": [
                            {
                                "text": "Volver al Menú",
                                "postback": "mostrar_menu"
                            }
                        ]
                    }
                ]
            ]
        }
    })
    return JsonResponse(response)

@medir_tiempo
def get_info_guia(request, nombre_guia):
    try:
        guia = GuiaTuristico.objects.filter(
            Q(nombre__icontains=nombre_guia) & (Q(estado="Aprobado") | Q(estado="Disponible"))
        ).first()
        
        if guia:
            print(f"Guía encontrado: {guia.nombre}")
            rutas = guia.rutas.all()
            rutas_info = ", ".join([ruta.nombre for ruta in rutas])
            response = {
                "fulfillmentMessages": [
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "info",
                                        "title": guia.nombre,
                                        "subtitle": f"Teléfono: {guia.telefono}",
                                        "image": {
                                            "src": {
                                                "rawUrl": request.build_absolute_uri(guia.foto.url) if guia.foto else ""
                                            }
                                        },
                                        "actionLink": f"{settings.DOMAIN}/guias/guia/{guia.id}/rutas/"
                                    }
                                ]
                            ]
                        }
                    },
                    {
                        "text": {
                            "text": [
                                f"Email: {guia.email}",
                                f"Rutas ofrecidas: {rutas_info}"
                            ]
                        }
                    }
                ]
            }
        else:
            print(f"No se encontró guía para: {nombre_guia}")
            response = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": ["Lo siento, no pude encontrar información sobre ese guía."]
                        }
                    }
                ]
            }
    except Exception as e:
        print(f"Error en get_info_guia: {str(e)}")
        response = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["Ocurrió un error al buscar la información del guía."]
                    }
                }
            ]
        }

    return JsonResponse(response)



def capturar_mensaje_usuario(request, parameters):
    try:
        nombre = parameters.get('nombre')
        correo = parameters.get('correo')
        asunto = parameters.get('asunto')
        mensaje = parameters.get('mensaje')

        print(f"Nombre: {nombre}, Correo: {correo}, Asunto: {asunto}, Mensaje: {mensaje}")
       
        response_text = f"Gracias, {nombre}. Hemos recibido tu mensaje sobre \"{asunto}\". Nos pondremos en contacto contigo a través de tu correo {correo}."
        MensajeUsuario.objects.create(
            nombre=nombre,
            correo=correo,
            asunto=asunto,
            mensaje=mensaje
        )
        # Agregar el botón para volver al menú
        menu_button = {
            "type": "chips",
            "options": [
                {
                    "text": "Volver al Menú ",
                    "postback": "mostrar_menu"
                }
            ]
        }

        return JsonResponse({
            'fulfillmentMessages': [
                {
                    'text': {
                        'text': [response_text]
                    }
                },
                {
                    'payload': {
                        'richContent': [[menu_button]]
                    }
                }
            ]
        })
    
    except Exception as e:
        print(f"Error al capturar mensaje del usuario: {str(e)}")
        return JsonResponse({'fulfillmentText': 'Ocurrió un error capturando el mensaje del usuario.'})



def mostrar_menu(request):
    try:
        response = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Selecciona una opción:"
                        ]
                    }
                },
                {
                    "payload": {
                        "richContent": [
                            [
                                {
                                    "type": "chips",
                                    "options": [
                                        {
                                            "text": "Alojamiento 🏨🛏️",
                                            "postback": "get_alojamiento"
                                        },
                                        {
                                            "text": "Guías Turísticas 🗺️🌍",
                                            "postback": "get_guias"
                                        },
                                        {
                                            "text": "Precios 🗒️🧳",
                                            "postback": "get_precios"
                                        },
                                        {
                                            "text": "Contáctanos 🆘🤔👨‍💻",
                                            "postback": "get_contacto"
                                        }
                                    ]
                                }
                            ]
                        ]
                    }
                }
            ]
        }
        return JsonResponse(response)
    except Exception as e:
        print(f"Error al mostrar el menú: {str(e)}")
        return JsonResponse({'fulfillmentText': 'Ocurrió un error mostrando el menú.'})

def bienvenida(request):
    try:
        response = {
            "fulfillmentMessages": [
                {
                    "title": "Hola ",
                    "text": {
                        "text": [
                            "Hola Te damos la bienvenida a la parroquia San Andres de Chimborazo. 😊",
                            "Selecciona una opción:"

                        ]
                    }
                },
                {
                    "payload": {
                        "richContent": [
                            [
                                {
                                    "type": "chips",
                                    "options": [
                                        {
                                            "text": "Alojamiento 🏨🛏️",
                                            "postback": "get_alojamiento"
                                        },
                                        {
                                            "text": "Guías Turísticas 🗺️🌍",
                                            "postback": "get_guias"
                                        },
                                        {
                                            "text": "Precios 🗒️🧳",
                                            "postback": "get_precios"
                                        },
                                        {
                                            "text": "Contáctanos 🆘🤔👨‍💻",
                                            "postback": "get_contacto"
                                        }
                                    ]
                                }
                            ]
                        ]
                    }
                }
            ]
        }
        return JsonResponse(response)
    except Exception as e:
        print(f"Error al mostrar el menú: {str(e)}")
        return JsonResponse({'fulfillmentText': 'Ocurrió un error mostrando el menú.'})



def capturar_precio(request, parameters):
    tipo_precio = parameters.get('tipo_precio')
    
    if tipo_precio == 'alojamiento':
        return consultar_precios_alojamiento(request)
    elif tipo_precio == 'rutas':
        return consultar_precios_rutas(request)
    else:
        return JsonResponse({'fulfillmentText': 'Lo siento, no puedo proporcionar información sobre ese tipo de precio.'})




def consultar_precios_alojamiento(request):
    alojamientos_aprobados = Alojamiento.objects.filter(estado="Aprobado")
    
    if alojamientos_aprobados:
        accordion_content = []
        
        for alojamiento in alojamientos_aprobados:
            tipos_alojamiento = TipoAlojamiento.objects.filter(alojamiento=alojamiento)
            precios_text = ""
            
            for tipo in tipos_alojamiento:
                precios_text += f"{tipo.tipo}: ${tipo.precio:.2f}\n"
            
            accordion_item = {
                "type": "accordion",
                "title": alojamiento.nombre,
                "subtitle": "Precios disponibles de las habitaciones",
                "image": {
                    "src": {
                        "rawUrl": alojamiento.imagen.url if alojamiento.imagen else ""
                    }
                },
                "text": precios_text.strip()
            }
            
            accordion_content.append(accordion_item)
        
        # Agregar el botón para volver al menú
        menu_button = {
            "type": "chips",
            "options": [
                {
                    "text": "Volver al Menú ",
                    "postback": "mostrar_menu"
                }
            ]
        }
        
        return JsonResponse({
            'fulfillmentMessages': [
                {
                    'text': {
                        'text': ['Aquí tienes los precios de nuestros alojamientos aprobados:']
                    }
                },
                {
                    'payload': {
                        'richContent': [accordion_content, [menu_button]]
                    }
                }
            ]
        })
    else:
        return JsonResponse({'fulfillmentText': 'Lo siento, no tenemos información sobre alojamientos aprobados en este momento.'})




def consultar_precios_rutas(request):
    rutas = Ruta.objects.all()
    
    if rutas:
        rich_content = [
            {
                'type': 'info',
                'title': ruta.nombre,
                'subtitle': f'Precio: ${ruta.precio}',
                'image': {
                    'src': {
                        'rawUrl': ruta.imagen.url if ruta.imagen else ''
                    }
                }
            } for ruta in rutas
        ]
        
        # Agregar el botón para volver al menú
        menu_button = {
            "type": "chips",
            "options": [
                {
                    "text": "Volver al Menú",
                    "postback": "mostrar_menu"
                }
            ]
        }
        
        return JsonResponse({
            'fulfillmentMessages': [
                {
                    'text': {
                        'text': ['Aquí tienes los precios de nuestras rutas:']
                    }
                },
                {
                    'payload': {
                        'richContent': [rich_content, [menu_button]]
                    }
                }
            ]
        })
        
    else:
        return JsonResponse({'fulfillmentText': 'Lo siento, no tenemos información sobre rutas en este momento.'})





# -----------------------------open ai------------------------------------------
from openai import OpenAI
@medir_tiempo
def responder_pregunta_especifica(request, body):
    pregunta = body['queryResult']['queryText']
    
    # Obtén información sobre alojamientos, guías y rutas de tu base de datos
    alojamientos = Alojamiento.objects.filter(estado="Aprobado")
    guias = GuiaTuristico.objects.filter(estado="Aprobado")
    rutas = Ruta.objects.all()
    
    # Crea un contexto con la información de tu sistema
    contexto = "Información sobre alojamientos:\n"
    for alojamiento in alojamientos:
        contexto += f"- {alojamiento.nombre}: {alojamiento.descripcion}\n"
        tipos = TipoAlojamiento.objects.filter(alojamiento=alojamiento)
        for tipo in tipos:
            contexto += f"  * {tipo.tipo}: Precio: ${tipo.precio}, Capacidad: {tipo.capacidad} personas, Camas: {tipo.numero_camas}\n"
    
    contexto += "\nInformación sobre guías turísticos:\n"
    for guia in guias:
        contexto += f"- {guia.nombre}: Contacto: {guia.email}, {guia.telefono}\n"
        rutas_guia = guia.rutas.all()
        if rutas_guia:
            contexto += "  Rutas:\n"
            for ruta in rutas_guia:
                contexto += f"    * {ruta.nombre}: {ruta.descripcion}. Precio: ${ruta.precio}, Capacidad: {ruta.capacidad} personas\n"
    
    contexto += "\nInformación sobre rutas turísticas:\n"
    for ruta in rutas:
        contexto += f"- {ruta.nombre}: {ruta.descripcion}. Precio: ${ruta.precio}, Capacidad: {ruta.capacidad} personas\n"
    
    # Configura el cliente de OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    respuesta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""Eres un asistente para un sistema de turismo. Responde preguntas basándote en esta información: {contexto}. 
            Si no tienes información específica para responder una pregunta, proporciona una respuesta general basada en conocimientos comunes sobre turismo y actividades relacionadas. 
            Asegúrate de indicar cuando estés dando información general que no es específica de los alojamientos, guías o rutas mencionados.
            Al final de cada respuesta, pregunta si el usuario desea hacer otra consulta."""},
            {"role": "user", "content": pregunta}
        ]
    )
    
    respuesta_texto = respuesta.choices[0].message.content
    
    # Añade la invitación a hacer otra pregunta
    respuesta_texto += "\n\n¿Deseas hacer otra pregunta sobre nuestros alojamientos, guías turísticas?"
    
    return JsonResponse({'fulfillmentText': respuesta_texto})