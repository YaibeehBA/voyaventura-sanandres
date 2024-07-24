from django.contrib import admin
from alojamiento.models import Alojamiento,TipoAlojamiento,GaleriaAlojamiento ,Habitacion, Reservacion
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from alojamiento.forms import AlojamientoAdminForm

class AlojamientoGaleriaInline(admin.TabularInline):
    model = GaleriaAlojamiento
    fields = ['alojamiento','imagen'] 
    

class TipoAlojamientoInline(admin.TabularInline):
    model = TipoAlojamiento
    fields = ['tipo','precio','numero_camas','capacidad','imagen_1']  
   

class HabitacionInline(admin.TabularInline):
    model = Habitacion
    fields= ('alojamiento', 'alojamiento_tipo', 'numero_habitacion', 'disponible')
   

class AlojamientoAdmin(admin.ModelAdmin):
    form = AlojamientoAdminForm
    inlines = [AlojamientoGaleriaInline, TipoAlojamientoInline, HabitacionInline]
    list_per_page = 15

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

    list_display = ('miniatura', 'nombre', 'celular','estado')



class GaleriaAlojamientoAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'alojamiento', 'imagen')
    search_fields = ('alojamiento__nombre',)
    list_per_page = 15


class TipoAlojamientoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'alojamiento', 'precio', 'numero_camas', 'capacidad')
    search_fields = ('alojamiento__nombre', 'tipo')
    list_filter = ('precio',)
    list_per_page=15


class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('alojamiento', 'alojamiento_tipo', 'numero_habitacion', 'disponible', 'cambiar_disponibilidad')
    search_fields = ('alojamiento__nombre', 'numero_habitacion')
    list_filter = ('disponible', 'alojamiento', 'alojamiento_tipo')
    list_per_page = 15

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si no hay parámetros en la URL (incluyendo página), mostrar solo las no disponibles
        if not request.GET or (len(request.GET) == 1 and 'p' in request.GET):
            return qs.filter(disponible=False)
        return qs

    def cambiar_disponibilidad(self, obj):
        if not obj.disponible:
            return format_html(
                '<a class="button" href="#" onclick="confirmarCambioDisponibilidad({}, event);">Liberar habitación</a>',
                obj.pk
            )
        return "Disponible"
    cambiar_disponibilidad.short_description = 'Acciones'
    cambiar_disponibilidad.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'cambiar_disponibilidad/<int:habitacion_id>/',
                self.admin_site.admin_view(self.cambiar_disponibilidad_view),
                name='cambiar_disponibilidad_habitacion',
            ),
        ]
        return custom_urls + urls

    def cambiar_disponibilidad_view(self, request, habitacion_id, *args, **kwargs):
        habitacion = self.get_object(request, habitacion_id)
        if habitacion:
            habitacion.disponible = True
            habitacion.save()
        return HttpResponseRedirect(reverse('admin:alojamiento_habitacion_changelist'))

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.all.min.js',
            'admin/js/confirmar_cambio_disponibilidad.js',
        )

class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('user', 'estado_pago', 'alojamiento',  'numeros_habitaciones','total', 'fecha_salida')
    search_fields = ('user__username', 'alojamiento__nombre', 'habitacion__numero_habitacion')
    list_filter = ('estado_pago', 'fecha_ingreso', 'fecha_salida')
    list_per_page = 15

    def numeros_habitaciones(self, obj):
        return ", ".join([h.numero_habitacion for h in obj.habitacion.all()])
    numeros_habitaciones.short_description = 'Habitación'



admin.site.register(Alojamiento, AlojamientoAdmin)
admin.site.register(GaleriaAlojamiento, GaleriaAlojamientoAdmin)

admin.site.register(TipoAlojamiento, TipoAlojamientoAdmin)
admin.site.register(Habitacion, HabitacionAdmin)
admin.site.register(Reservacion, ReservacionAdmin)

# Register your models here.
