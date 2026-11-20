from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Libro, Prestamo
from .serializers import LibroSerializer


class PrestamoSerializer(serializers.ModelSerializer):
    """Lee el libro anidado completo; escribe el libro con libro_id."""

    libro = LibroSerializer(read_only=True)
    libro_id = serializers.PrimaryKeyRelatedField(
        queryset=Libro.objects.all(), source="libro", write_only=True
    )

    class Meta:
        model = Prestamo
        fields = [
            "id",
            "libro",
            "libro_id",
            "lector",
            "fecha_prestamo",
            "fecha_devolucion",
            "devuelto",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        libro = attrs.get("libro")

        if self.instance is None:
            if libro is not None and not libro.disponible:
                raise serializers.ValidationError(
                    {"libro_id": "El libro no está disponible para préstamo."}
                )
        elif libro is not None and libro != self.instance.libro:
            raise serializers.ValidationError(
                {"libro_id": "No se puede cambiar el libro de un préstamo."}
            )

        inicio = attrs.get(
            "fecha_prestamo", getattr(self.instance, "fecha_prestamo", None)
        )
        fin = attrs.get(
            "fecha_devolucion", getattr(self.instance, "fecha_devolucion", None)
        )
        if inicio and fin and fin < inicio:
            raise serializers.ValidationError(
                {"fecha_devolucion": "No puede ser anterior a la fecha del préstamo."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        prestamo = super().create(validated_data)
        prestamo.libro.disponible = False
        prestamo.libro.save(update_fields=["disponible"])
        return prestamo

    @transaction.atomic
    def update(self, instance, validated_data):
        estaba_devuelto = instance.devuelto
        prestamo = super().update(instance, validated_data)

        if prestamo.devuelto and not estaba_devuelto:
            if prestamo.fecha_devolucion is None:
                prestamo.fecha_devolucion = timezone.localdate()
                prestamo.save(update_fields=["fecha_devolucion"])
            prestamo.libro.disponible = True
            prestamo.libro.save(update_fields=["disponible"])
        return prestamo


class PrestamoResumenSerializer(serializers.ModelSerializer):
    """Préstamo sin el libro: se usa anidado dentro del detalle de un libro."""

    class Meta:
        model = Prestamo
        fields = ["id", "lector", "fecha_prestamo", "fecha_devolucion", "devuelto"]


class LibroConPrestamosSerializer(LibroSerializer):
    """Libro con la lista de sus préstamos anidada."""

    prestamos = PrestamoResumenSerializer(many=True, read_only=True)

    class Meta(LibroSerializer.Meta):
        fields = LibroSerializer.Meta.fields + ["prestamos"]
