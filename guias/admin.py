from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.html import mark_safe
from .models import GuiaTuristico, Ruta, ReservacionGuia, GuiaRuta




class GuiaTuristicoAdmin(admin.ModelAdmin):

    list_display = ('nombre', 'email', 'telefono', 'miniatura', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre', 'email', 'telefono')
    list_per_page = 15

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generar-reporte-guia/', self.admin_site.admin_view(self.generar_reporte_view), name='generar_reporte_guia'),
        ]
        return custom_urls + urls

    def generar_reporte_view(self, request):
        # Aquí redirigimos a la vista de generar reporte
        return redirect('reportes:generar_reporte_guia')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generar_reporte'] = True
        return super().changelist_view(request, extra_context=extra_context)

class RutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'imagen_preview')
    search_fields = ('nombre', 'descripcion')
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return mark_safe(f"<img src='{obj.imagen.url}' width='50' height='50' style='object-fit: cover; border-radius:6px;'/>")
        return ""
    imagen_preview.short_description = 'Imagen'

class GuiaRutaAdmin(admin.ModelAdmin):
    list_display = ('guia', 'ruta')
    search_fields = ('guia__nombre', 'ruta__nombre')
    list_per_page = 15

class ReservacionGuiaAdmin(admin.ModelAdmin):
    list_display = ('user', 'guia', 'ruta', 'fecha_reserva', 'num_personas', 'estado_pago', 'total', 'fecha_creacion')
    list_filter = ('estado_pago', 'fecha_reserva')
    search_fields = ('user__username', 'guia__nombre', 'ruta__nombre')
    readonly_fields = ('fecha_creacion',)
    list_per_page = 15

admin.site.register(GuiaTuristico, GuiaTuristicoAdmin)
admin.site.register(Ruta, RutaAdmin)
admin.site.register(GuiaRuta, GuiaRutaAdmin)
admin.site.register(ReservacionGuia, ReservacionGuiaAdmin)