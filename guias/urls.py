
from django.urls import path
from . import views
app_name = 'guias'
urlpatterns = [
    path('guia/<int:guia_id>/rutas/', views.rutas_por_guia, name='rutas_por_guia'),
    path('ruta/<int:ruta_id>/', views.detalle_ruta, name='detalle_ruta'),
     path('ruta/<int:ruta_id>/guia/<int:guia_id>/', views.detalle_ruta_con_guia, name='detalle_ruta_con_guia'),
    path('ver_guias/', views.ver_guias, name='ver_guias'),
]
