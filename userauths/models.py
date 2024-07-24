from django.db import models
from django.contrib.auth.models import AbstractUser




def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (instance.user.id, filename)
    return "user_{0}/{1}".format(instance.user.id, filename)

class Usuario(AbstractUser):  
    full_name = models.CharField(max_length=500, null=True, blank=True)  
    username = models.CharField(max_length=500, unique=True) 
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=30, null=True, blank=True, unique=True)  
   

    
    # como va iniciar session

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class MensajeUsuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"