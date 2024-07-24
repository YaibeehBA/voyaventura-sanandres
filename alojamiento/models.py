from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from userauths.models import Usuario
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, EmailValidator, FileExtensionValidator




ALOJAMIENTO_ESTADO=(

    ("Borrador","Borrador"),
    ("Rechazado","Rechazado"),
    ("Aprobado","Aprobado"),
   
)



ESTADO_PAGO=(
    ("Pagado","Pagado"),
    ("Pendiente","Pendiente"),
    ("Vencido","Vencido"),
    ("Cancelado","Cancelado"),
)


class Alojamiento(models.Model):
    user  = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    nombre = models.CharField(
    unique=True,
    max_length=150,
    validators=[
        RegexValidator(
            regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s-]+$',
            message='El nombre solo puede contener letras, espacios, guiones y tildes.'
        )
    ]
)
    email = models.EmailField(validators=[EmailValidator(message='Correo electrónico no válido.')], unique=True)
    descripcion = models.TextField(null=False, blank= False)
    imagen = models.FileField(upload_to="alojamiento_galeria", validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png','webp'])])
    direccion = models.CharField(max_length=200)
    celular = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Número de celular no válido. Debe tener exactamente 10 dígitos.'
            )
        ]
    )
    estado = models.CharField(max_length=20, choices=ALOJAMIENTO_ESTADO, default="Borrador")
   
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
  
    def miniatura(self):
        return mark_safe("<img src='%s' width='50' height='50' style='object-fit: cover; border-radius:6px;'/>" % self.imagen.url)

    def galeria_alojamiento(self):
        return GaleriaAlojamiento.objects.filter(alojamiento=self)

    def alojamiento_habitaciones_tipos(self):
        return TipoAlojamiento.objects.filter(alojamiento=self)
    

class GaleriaAlojamiento(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    imagen = models.FileField(upload_to="galeria_alojamiento", validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png','webp'])])
  

    def miniatura(self):
        return mark_safe("<img src='%s' width='50' height='50' style='object-fit: cover; border-radius:6px;'/>" % self.imagen.url)
    def __str__(self):
        return str(self.alojamiento.nombre)

    class Meta:
        verbose_name_plural = "Galería Alojamiento"



class TipoAlojamiento(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1000)
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,validators=[MinValueValidator(0)])
    imagen_1 = models.FileField(upload_to="galeria_tipo_alojamiento", null=False, blank=False)
   
    numero_camas = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0)])
    capacidad = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0)])
  

    def __str__(self):
        return f"{self.tipo} - {self.alojamiento.nombre} - {self.precio}"

    class Meta:
        verbose_name_plural = "Tipo Alojamiento"

    def alojamiento_contar(self):
        return Habitacion.objects.filter(alojamiento_tipo=self).count()

class Habitacion(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    alojamiento_tipo = models.ForeignKey(TipoAlojamiento, on_delete=models.CASCADE)
    numero_habitacion = models.CharField(max_length=1000, unique=True)
    descripcion = models.TextField(null=True, blank= True)
    disponible = models.BooleanField(default=True)
  

   
    def __str__(self):
        return f"{self.alojamiento_tipo.tipo} - {self.alojamiento.nombre}"
    
    class Meta:
        verbose_name_plural = "Habitaciones"

    def precio(self):
        return self.alojamiento_tipo.precio
    
    def numero_camas(self):
        return self.alojamiento_tipo.numero_camas
    

class Reservacion(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    estado_pago = models.CharField(max_length=100, choices=ESTADO_PAGO)
    
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.SET_NULL, null=True, blank=True)
    habitacion_tipo = models.ForeignKey(TipoAlojamiento, on_delete=models.SET_NULL, null=True, blank=True)
    habitacion = models.ManyToManyField(Habitacion)
   
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField()
   
    num_adultos = models.PositiveIntegerField(default=1)
    num_ninos = models.PositiveIntegerField(default=0)
    estado = models.BooleanField(default=False)

    fecha = models.DateField(auto_now_add=True)
    
    pago_id = models.CharField(max_length=1000, null=True, blank=True)
     








    
    


