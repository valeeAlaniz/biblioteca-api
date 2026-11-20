from django.db import models
from django.utils import timezone


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=120)
    anio_publicacion = models.PositiveSmallIntegerField()
    isbn = models.CharField(max_length=20, unique=True)
    disponible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.titulo} ({self.autor})"


class Prestamo(models.Model):
    libro = models.ForeignKey(
        Libro, on_delete=models.CASCADE, related_name="prestamos"
    )
    lector = models.CharField(max_length=120)
    fecha_prestamo = models.DateField(default=timezone.localdate)
    fecha_devolucion = models.DateField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_prestamo", "-id"]

    def __str__(self):
        return f"{self.libro.titulo} -> {self.lector}"
