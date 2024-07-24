from django.db import models
from django.utils.html import mark_safe
from userauths.models import Usuario
from django.core.validators import MaxValueValidator
from django.core.validators import RegexValidator

GUIA_ESTADO = (
    ("Borrador", "Borrador"),
    ("Rechazado", "Rechazado"),
    ("Aprobado", "Aprobado"),
    ("Reservado", "Reservado"),
    ("Disponible", "Disponible"),
)

ESTADO_PAGO = (
    ("Pagado", "Pagado"),
    ("Pendiente", "Pendiente"),
    ("Vencido", "Vencido"),
    ("Cancelado", "Cancelado"),
)

class Ruta(models.Model):
    
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    capacidad = models.PositiveSmallIntegerField(
        default=1,
        validators=[MaxValueValidator(
            15,
            message= ("La capacidad máxima no puede superar las 15 personas.")
        )],
        verbose_name="Capacidad máxima"
    )
    imagen = models.FileField(upload_to="imagenes_ruta", null=False, blank=False)
    
    def __str__(self):
        return self.nombre
    
  
    def imagen_preview(self):
        if self.imagen:
            return mark_safe(f"<img src='{self.imagen.url}' width='50' height='50' style='object-fit: cover; border-radius:6px;'/>")
        return ""
    imagen_preview.short_description = 'Imagen'

class GuiaTuristico(models.Model):
    
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message="El número de teléfono debe contener exactamente 10 dígitos."
        )]
    )
    foto = models.FileField(upload_to="fotos_guia", null=False, blank=False)
    estado = models.CharField(max_length=20, choices=GUIA_ESTADO, default="Borrador")
    rutas = models.ManyToManyField(Ruta, through='GuiaRuta', related_name='guias')

    def miniatura(self):
        if self.foto:
            return mark_safe("<img src='%s' width='50' height='50' style='object-fit: cover; border-radius:6px;'/>" % self.foto.url)
        return ""
    miniatura.short_description = 'Foto'

    def __str__(self):
        return self.nombre

class GuiaRuta(models.Model):
    guia = models.ForeignKey(GuiaTuristico, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('guia', 'ruta')
        verbose_name = 'Asignar Ruta'
        verbose_name_plural = 'Asignar Rutas'

    def __str__(self):
        return f"{self.guia.nombre} - {self.ruta.nombre}"

class ReservacionGuia(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    guia = models.ForeignKey(GuiaTuristico, on_delete=models.SET_NULL, null=True, blank=True)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_reserva = models.DateField()
    num_personas = models.PositiveIntegerField(default=1)
    estado_pago = models.CharField(max_length=100, choices=ESTADO_PAGO)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    pago_id = models.CharField(max_length=1000, null=True, blank=True)
    
    def __str__(self):
        return f"Reserva para {self.guia.nombre} - Ruta: {self.ruta.nombre} - Usuario: {self.user.username if self.user else 'Anonimo'}"
