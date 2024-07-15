from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from userauths.models import Usuario
from django.utils.translation import gettext_lazy as _
import re
from django.contrib.auth.forms import PasswordResetForm
from userauths.models import Usuario

class UsuarioRegistradoForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-field'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-field'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={
        'type': 'tel',
        'pattern': '^\d{10}$',
        'title': 'Ingrese un número de teléfono válido de 10 dígitos',
        'class': 'input-field'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input-field'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-field'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-field'}))

    class Meta:
        model = Usuario
        fields = ['full_name', 'username', 'telefono', 'email', 'password1', 'password2']

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not re.match(r'^\d{10}$', telefono):
            raise ValidationError(_("El número de teléfono debe tener 10 dígitos."))
        if Usuario.objects.filter(telefono=telefono).exists():
            raise ValidationError(_("Este número de teléfono ya está registrado."))
        return telefono

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError(_("Este correo electrónico ya está registrado."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', _("Las contraseñas no coinciden."))

        return cleaned_data

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'input-field'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Usuario.objects.filter(email=email).exists():
            raise ValidationError(_("No existe una cuenta con este correo electrónico."))
        return email