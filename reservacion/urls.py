from django.urls import path
from reservacion import views

app_name = "reservacion"

urlpatterns = [
    path("habitacion_disponible/", views.habitacion_disponible,
         name="habitacion_disponible"),
    path("add_selecion/", views.add_selecion, name="add_selecion"),
    path('mi-reserva/', views.mi_reserva, name='mi-reserva'),
    path('create-payment/', views.create_payment, name='create_payment'),
    path('create-checkout-session/', views.create_checkout_session,
         name='create_checkout_session'),
    path('create-checkout-session-2/', views.create_checkout_session_2,
         name='create_checkout_session_2'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-success-2/', views.payment_success_2, name='payment_success_2'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('descargar-ticket/<int:reserva_id>/', views.descargar_ticket, name='descargar_ticket'),
    path('descargar-ticket_guia/<int:reserva_id>/', views.descargar_ticket_guia, name='descargar_ticket_guia'),
]
