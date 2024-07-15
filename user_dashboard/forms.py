from django import forms
from alojamiento.models import Alojamiento
from guias.models import GuiaTuristico

# class ReporteAlojamientoForm(forms.Form):
#     alojamiento = forms.ModelChoiceField(queryset=Alojamiento.objects.all())
#     PERIODO_CHOICES = [
#         ('dia', 'Día'),
#         ('mes', 'Mes'),
#         ('año', 'Año'),
#     ]
#     periodo = forms.ChoiceField(choices=PERIODO_CHOICES)
#     fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class ReporteAlojamientoForm(forms.Form):
    alojamiento = forms.ModelChoiceField(
        queryset=Alojamiento.objects.filter(estado="Aprobado"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class ReporteGuiaForm(forms.Form):
    guia = forms.ModelChoiceField(
        queryset=GuiaTuristico.objects.filter(estado="Aprobado"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )