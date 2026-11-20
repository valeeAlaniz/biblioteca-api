from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Libro, Prestamo
from .permissions import IsAdminOrReadOnly
from .prestamos_serializers import LibroConPrestamosSerializer, PrestamoSerializer
from .serializers import LibroSerializer


class LibroViewSet(viewsets.ModelViewSet):
    """CRUD de libros. Leer es público; escribir es solo para admin."""

    serializer_class = LibroSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        libros = Libro.objects.all()

        disponible = self.request.query_params.get("disponible")
        if disponible is not None:
            libros = libros.filter(disponible=disponible.lower() in ("true", "1"))

        autor = self.request.query_params.get("autor")
        if autor:
            libros = libros.filter(autor__icontains=autor)

        return libros

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def detalle(self, request, pk=None):
        """GET /api/libros/<id>/detalle/: el libro con sus préstamos anidados."""
        libro = self.get_object()
        return Response(LibroConPrestamosSerializer(libro).data)


class CatalogoViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo público y de solo lectura: únicamente libros disponibles."""

    serializer_class = LibroSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        libros = Libro.objects.filter(disponible=True)

        buscar = self.request.query_params.get("search")
        if buscar:
            libros = libros.filter(titulo__icontains=buscar) | libros.filter(
                autor__icontains=buscar
            )

        return libros


class PrestamoViewSet(viewsets.ModelViewSet):
    """Préstamos. Hay que estar logueado; borrar es solo para admin."""

    serializer_class = PrestamoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        prestamos = Prestamo.objects.select_related("libro")

        devuelto = self.request.query_params.get("devuelto")
        if devuelto is not None:
            prestamos = prestamos.filter(devuelto=devuelto.lower() in ("true", "1"))

        libro = self.request.query_params.get("libro")
        if libro and libro.isdigit():
            prestamos = prestamos.filter(libro_id=int(libro))

        return prestamos

    def perform_destroy(self, instance):
        # Si se borra un préstamo que seguía abierto, el libro vuelve a estar disponible
        if not instance.devuelto:
            instance.libro.disponible = True
            instance.libro.save(update_fields=["disponible"])
        instance.delete()

    @action(detail=True, methods=["post"])
    def devolver(self, request, pk=None):
        """POST /api/prestamos/<id>/devolver/: registra la devolución."""
        prestamo = self.get_object()
        if prestamo.devuelto:
            return Response(
                {"detail": "El préstamo ya fue devuelto."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(prestamo, data={"devuelto": True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
