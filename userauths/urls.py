from django.urls import include, path
from django.contrib.auth import views as auth_views
from userauths import views
from userauths.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
app_name = 'userauths'

urlpatterns = [
    path("sign-up", views.RegistrarVista, name="sign-up"),
    path("sign-in", views.LoginVista, name="sign-in"),
    path("sign-out", views.Cerrar_Sesion, name="sign-out"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]