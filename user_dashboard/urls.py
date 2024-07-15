from django.urls import path
from . import views
app_name = 'reportes'
urlpatterns = [
    path('generar-reporte/', views.generar_reporte_alojamiento, name='generar_reporte_alojamiento'),
    
    path('generar-reporte-guia/', views.generar_reporte_guia, name='generar_reporte_guia'),

]