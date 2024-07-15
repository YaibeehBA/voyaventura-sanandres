from django.contrib import admin
from alojamiento.models import Alojamiento,TipoAlojamiento,GaleriaAlojamiento ,Habitacion, Reservacion
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse


class AlojamientoGaleriaInline(admin.TabularInline):
    model = GaleriaAlojamiento
    fields = ['alojamiento','imagen'] 
    

class TipoAlojamientoInline(admin.TabularInline):
    model = TipoAlojamiento
    fields = ['tipo','precio','numero_camas','capacidad','imagen_1']  
   

class HabitacionInline(admin.TabularInline):
    model = Habitacion
    fields= ('alojamiento', 'alojamiento_tipo', 'numero_habitacion', 'disponible')
   
# class AlojamientoAdmin(admin.ModelAdmin):
#     inlines = [AlojamientoGaleriaInline,TipoAlojamientoInline,HabitacionInline]
    
#     list_display=['miniatura', 'nombre','celular','estado']
#     list_per_page=5

# class AlojamientoAdmin(admin.ModelAdmin):
#     inlines = [AlojamientoGaleriaInline,TipoAlojamientoInline,HabitacionInline]
#     list_display = ('miniatura', 'nombre','estado', 'generar_reporte_link')
#     list_per_page=5
#     def generar_reporte_link(self, obj):
#         url = reverse('generar_reporte_alojamiento')
#         return format_html('<a href="{}?alojamiento={}">Generar Reporte</a>', url, obj.id)

#     generar_reporte_link.short_description = "Reporte"


# class AlojamientoAdmin(admin.ModelAdmin):
#     inlines = [AlojamientoGaleriaInline, TipoAlojamientoInline, HabitacionInline]
#     # list_display = ('miniatura', 'nombre', 'estado')
#     list_per_page = 5
    
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('generar-reporte/', self.admin_site.admin_view(self.generar_reporte_view), name='generar_reporte_alojamiento'),
#         ]
#         return custom_urls + urls

#     def generar_reporte_view(self, request):
#         return redirect('generar_reporte_alojamiento')

#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['show_generar_reporte'] = True
#         return super().changelist_view(request, extra_context=extra_context)


#     list_display = ('miniatura', 'nombre', 'estado')
class AlojamientoAdmin(admin.ModelAdmin):
    inlines = [AlojamientoGaleriaInline, TipoAlojamientoInline, HabitacionInline]
    list_per_page = 5

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generar-reporte/', self.admin_site.admin_view(self.generar_reporte_view), name='generar_reporte_alojamiento'),
        ]
        return custom_urls + urls

    def generar_reporte_view(self, request):
        return redirect(reverse('reportes:generar_reporte_alojamiento'))  # Asegúrate de usar el namespace si es necesario

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generar_reporte'] = True
        return super().changelist_view(request, extra_context=extra_context)

    list_display = ('miniatura', 'nombre', 'estado')



class GaleriaAlojamientoAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'alojamiento', 'imagen')
    search_fields = ('alojamiento__nombre',)
    list_per_page = 5


class TipoAlojamientoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'alojamiento', 'precio', 'numero_camas', 'capacidad')
    search_fields = ('alojamiento__nombre', 'tipo')
    list_filter = ('precio',)
    list_per_page=5

class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('alojamiento', 'alojamiento_tipo', 'numero_habitacion', 'disponible')
    search_fields = ('alojamiento__nombre', 'numero_habitacion')
    list_filter = ('disponible',)
    list_per_page=5

class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('user', 'estado_pago', 'alojamiento', 'fecha_ingreso', 'fecha_salida', 'num_adultos', 'num_ninos')
    search_fields = ('user__username', 'alojamiento__nombre')
    list_filter = ('estado_pago', 'fecha_ingreso', 'fecha_salida')
    list_per_page = 5




admin.site.register(Alojamiento, AlojamientoAdmin)
admin.site.register(GaleriaAlojamiento, GaleriaAlojamientoAdmin)

admin.site.register(TipoAlojamiento, TipoAlojamientoAdmin)
admin.site.register(Habitacion, HabitacionAdmin)
admin.site.register(Reservacion, ReservacionAdmin)

# Register your models here.
