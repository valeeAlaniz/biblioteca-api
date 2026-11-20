from rest_framework import generics

from .models import Libro, Prestamo
from .prestamos_serializers import LibroConPrestamosSerializer, PrestamoSerializer


class PrestamoListCreateView(generics.ListCreateAPIView):
    """GET: lista préstamos (?devuelto=true, ?libro=<id>). POST: crea un préstamo."""

    serializer_class = PrestamoSerializer

    def get_queryset(self):
        queryset = Prestamo.objects.select_related("libro")

        devuelto = self.request.query_params.get("devuelto")
        if devuelto is not None:
            queryset = queryset.filter(devuelto=devuelto.lower() in ("true", "1"))

        libro = self.request.query_params.get("libro")
        if libro and libro.isdigit():
            queryset = queryset.filter(libro_id=int(libro))

        return queryset


class PrestamoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, PATCH y DELETE de un préstamo."""

    queryset = Prestamo.objects.select_related("libro")
    serializer_class = PrestamoSerializer

    def perform_destroy(self, instance):
        # Si se borra un préstamo que seguía abierto, el libro vuelve a estar disponible
        if not instance.devuelto:
            instance.libro.disponible = True
            instance.libro.save(update_fields=["disponible"])
        instance.delete()


class LibroDetalleView(generics.RetrieveAPIView):
    """GET: un libro con sus préstamos anidados."""

    queryset = Libro.objects.prefetch_related("prestamos")
    serializer_class = LibroConPrestamosSerializer
