from django.urls import path
from alojamiento import views

app_name = "alojamiento"

urlpatterns = [
    path("", views.index, name="index"),
    path('webhook/', views.webhook, name='webhook'),
    

    path("detalle/<int:pk>", views.alojamiento_detalle, name="alojamiento_detalle"),
    path("detalle/<int:pk>/tipos-alojamiento/<int:ta_pk>/", views.tipos_alojamiento_detalle, name="tipos_alojamiento_detalle"),
    path("ver_alojamiento_detalle/", views.ver_alojamientos_detalle, name="ver_alojamientos_detalle"),
]
