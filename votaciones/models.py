from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Número de Cédula")
    ha_votado = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} ({self.cedula})"

class EdicionFestival(models.Model):
    anio = models.IntegerField(default=2027)
    numero_edicion = models.CharField(max_length=50, default="60° Edición Especial")
    nombre_homenajeado = models.CharField(max_length=150, default="Omar Geles Suárez")
    titulo_homenajeado = models.CharField(max_length=150, default="Rey Vallenato 1989 & Cantor Inmortal del Folclor")
    anios_homenajeado = models.CharField(max_length=50, default="1967 - 2024")
    biografia_homenajeado = models.TextField(default="En la fiesta folclórica más importante de Colombia, la Fundación Festival de la Leyenda Vallenata rinde tributo a la vida y obra del juglar.")
    imagen_homenajeado = models.ImageField(upload_to="homenajeados/", blank=True, null=True)

    def __str__(self):
        return f"Festival Vallenato {self.anio} - {self.numero_edicion}"

class Categoria(models.Model):
    ESTADOS = [
        ('abierta', 'Abierta'),
        ('programada', 'Programada'),
        ('cerrada', 'Cerrada'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierta')
    fecha_apertura = models.CharField(max_length=50, default="2027-04-28 08:00")
    fecha_cierre = models.CharField(max_length=50, default="2027-04-30 22:00")

    def __str__(self):
        return self.nombre

class Candidato(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="candidatos")
    nombre_artistico = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to="candidatos/", blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_artistico} - {self.categoria.nombre}"

class Voto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="votos")
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name="votos")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'candidato')

    def __str__(self):
        return f"Voto de {self.usuario.cedula} por {self.candidato.nombre_artistico}"




class ConfiguracionSitio(models.Model):
    """Permite editar el título y subtítulo principal desde el Admin de Django"""
    titulo_banner = models.CharField(
        max_length=255, 
        default="Apoya a tus acordeoneros en el Festival Vallenato 2027"
    )
    subtitulo_banner = models.TextField(
        default="Plataforma oficial certificada por la Fundación Festival de la Leyenda Vallenata. Emite tu voto seguro, transparente y verificado con tu documento de identidad."
    )

    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuraciones del Sitio"

    def __str__(self):
        return "Configuración del Encabezado Principal"


class EventoProgramacion(models.Model):
    """Módulo de Cronograma del Festival"""
    edicion = models.ForeignKey('EdicionFestival', on_delete=models.CASCADE, related_name='eventos')
    titulo = models.CharField(max_length=200, help_text="Ej: Eliminatoria Acordeón Profesional")
    lugar = models.CharField(max_length=200, help_text="Ej: Parque de la Leyenda Vallenata / Plaza Primero de Mayo")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Evento del Cronograma"
        verbose_name_plural = "Cronograma del Festival"
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"