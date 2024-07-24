from django import forms
from django.contrib.auth import get_user_model
from .models import Alojamiento

User = get_user_model()

class AlojamientoAdminForm(forms.ModelForm):
    class Meta:
        model = Alojamiento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_staff=True)