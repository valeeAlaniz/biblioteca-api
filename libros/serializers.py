from django.utils import timezone
from rest_framework import serializers

from .models import Libro


class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = [
            "id",
            "titulo",
            "autor",
            "anio_publicacion",
            "isbn",
            "disponible",
            "creado",
        ]
        read_only_fields = ["id", "creado"]

    def validate_anio_publicacion(self, value):
        if value > timezone.localdate().year:
            raise serializers.ValidationError(
                "El año de publicación no puede ser futuro."
            )
        return value

    def validate_titulo(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El título debe tener al menos 2 caracteres."
            )
        return value.strip()
