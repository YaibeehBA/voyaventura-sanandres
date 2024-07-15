from django.shortcuts import render, redirect
from django.contrib.auth import  authenticate,login,logout
from django.contrib import  messages
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from userauths.models import Usuario
from userauths.forms import UsuarioRegistradoForm, CustomPasswordResetForm




def RegistrarVista(request):
    if request.user.is_authenticated:
        messages.warning(request, "Ya has iniciado sesión")
        return redirect("alojamiento:index")

    if request.method == 'POST':
        form = UsuarioRegistradoForm(request.POST)
        if form.is_valid():
            user = form.save()
            full_name = form.cleaned_data.get("full_name")
            telefono = form.cleaned_data.get("telefono")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")

            user = authenticate(email=email, password=password)
            login(request, user)

            messages.success(request, f"{full_name}, su cuenta fue creada exitosamente")

            
            return redirect("alojamiento:index")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UsuarioRegistradoForm()

    context = {
        "form": form,
    }
    return render(request, "userauths/sign-up.html", context)


def LoginVista(request):

    if request.user.is_authenticated:
        messages.warning(request,f"Ya has iniciado session")
        return redirect("alojamiento:index")
    if request.method== 'POST':
        email= request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_query = Usuario.objects.get(email=email)
            user_auth = authenticate (request, email=email, password= password)
            
            if user_query is not None:
                login(request,user_auth)
                messages.success(request,"has iniciado session" )
                next_url = request.GET.get("next", "alojamiento:index")
                return redirect (next_url)
            else:
                messages.success(request,"Usuario o Contraseña incorrecta" )
                return redirect ("userauths:sign-in")
            
        
        except:
            messages.success(request,"Usuario no existe" )
            return redirect ("userauths:sign-in")
    return render( request, "userauths/sign-in.html")

def Cerrar_Sesion(request):
    logout(request)
    messages.warning(request,f"Session cerrada con éxito")
    return redirect("userauths:sign-in")
    





class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('userauths:password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('userauths:password_reset_done')
    template_name = 'registration/password_reset_form.html'