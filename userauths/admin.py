from django.contrib import admin
from userauths.models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username']
    list_display = ['username', 'full_name', 'email', 'telefono']



admin.site.register(Usuario, UsuarioAdmin)

