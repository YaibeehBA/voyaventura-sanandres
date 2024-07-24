from django.contrib import admin
from django.http import HttpResponseRedirect
from userauths.models import Usuario, MensajeUsuario
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path

class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username']
    list_display = ['username', 'full_name', 'email', 'telefono']

class MensajeUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'asunto', 'fecha_envio', 'eliminar_mensaje')

    def eliminar_mensaje(self, obj):
        return format_html(
            '<a class="button" href="#" onclick="confirmarEliminacion({}, event);">Eliminar</a>',
            obj.pk
        )
    eliminar_mensaje.short_description = 'Eliminar'
    eliminar_mensaje.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'eliminar/<int:mensaje_id>/',
                self.admin_site.admin_view(self.eliminar_mensaje_view),
                name='eliminar_mensaje',
            ),
        ]
        return custom_urls + urls

    def eliminar_mensaje_view(self, request, mensaje_id, *args, **kwargs):
        mensaje = self.get_object(request, mensaje_id)
        if mensaje:
            mensaje.delete()
        return HttpResponseRedirect(reverse('admin:userauths_mensajeusuario_changelist'))

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.all.min.js',
            'admin/js/confirmar_eliminacion.js',
        )
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(MensajeUsuario, MensajeUsuarioAdmin)

