from django.contrib import admin

from .models import Libro, Prestamo


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "anio_publicacion", "isbn", "disponible")
    list_filter = ("disponible",)
    search_fields = ("titulo", "autor", "isbn")


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ("libro", "lector", "fecha_prestamo", "fecha_devolucion", "devuelto")
    list_filter = ("devuelto",)
    search_fields = ("lector", "libro__titulo")
