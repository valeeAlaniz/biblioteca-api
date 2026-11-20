from django.contrib import admin

from .models import Libro


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "anio_publicacion", "isbn", "disponible")
    list_filter = ("disponible",)
    search_fields = ("titulo", "autor", "isbn")
