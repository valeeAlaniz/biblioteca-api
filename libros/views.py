from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Libro
from .serializers import LibroSerializer


@api_view(["GET", "POST"])
def libro_list(request):
    """GET: lista los libros (filtros opcionales). POST: crea un libro."""
    if request.method == "GET":
        libros = Libro.objects.all()

        disponible = request.query_params.get("disponible")
        if disponible is not None:
            libros = libros.filter(disponible=disponible.lower() in ("true", "1"))

        autor = request.query_params.get("autor")
        if autor:
            libros = libros.filter(autor__icontains=autor)

        serializer = LibroSerializer(libros, many=True)
        return Response(serializer.data)

    serializer = LibroSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def libro_detail(request, pk):
    """GET: detalle. PUT/PATCH: edita. DELETE: elimina."""
    libro = get_object_or_404(Libro, pk=pk)

    if request.method == "GET":
        return Response(LibroSerializer(libro).data)

    if request.method in ("PUT", "PATCH"):
        serializer = LibroSerializer(
            libro, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    libro.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
