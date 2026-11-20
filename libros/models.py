from django.db import models


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
