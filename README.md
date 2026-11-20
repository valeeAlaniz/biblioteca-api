# Biblioteca API

API REST de una biblioteca, hecha con Django y Django REST Framework.
Primer práctico: un modelo, un serializer y vistas funcionales de CRUD con `@api_view`.

## Modelo

`Libro`: `titulo`, `autor`, `anio_publicacion`, `isbn` (único), `disponible`, `creado`.

## Endpoints

| Método | Ruta | Qué hace |
| --- | --- | --- |
| GET | `/api/libros/` | Lista los libros. Filtros: `?disponible=true`, `?autor=borges` |
| POST | `/api/libros/` | Crea un libro |
| GET | `/api/libros/<id>/` | Detalle de un libro |
| PUT | `/api/libros/<id>/` | Reemplaza un libro (todos los campos) |
| PATCH | `/api/libros/<id>/` | Edita campos sueltos |
| DELETE | `/api/libros/<id>/` | Elimina un libro |

Ejemplo de cuerpo para crear:

```json
{
  "titulo": "Rayuela",
  "autor": "Julio Cortázar",
  "anio_publicacion": 1963,
  "isbn": "978-84-376-0494-7",
  "disponible": true
}
```

## Cómo correrlo

Requiere [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

La API queda en http://127.0.0.1:8000/api/libros/

## Tests

```
uv run python manage.py test libros
```

## Autores

Valentina Alaniz
## Práctico 2: préstamos

Se agrega el modelo `Prestamo`, relacionado con `Libro` por clave foránea (un libro tiene muchos préstamos).
Las vistas son basadas en clases (`ListCreateAPIView` y `RetrieveUpdateDestroyAPIView`) y los serializers son anidados.

Campos de `Prestamo`: `libro`, `lector`, `fecha_prestamo`, `fecha_devolucion`, `devuelto`.

| Método | Ruta | Qué hace |
| --- | --- | --- |
| GET | `/api/prestamos/` | Lista préstamos con el libro anidado. Filtros: `?devuelto=false`, `?libro=1` |
| POST | `/api/prestamos/` | Crea un préstamo. Se envía `libro_id` y `lector`. El libro queda no disponible |
| GET | `/api/prestamos/<id>/` | Detalle de un préstamo |
| PUT / PATCH | `/api/prestamos/<id>/` | Edita un préstamo. Con `{"devuelto": true}` se registra la devolución y el libro vuelve a estar disponible |
| DELETE | `/api/prestamos/<id>/` | Elimina un préstamo |
| GET | `/api/libros/<id>/detalle/` | Un libro con la lista de sus préstamos anidada |

Reglas: no se puede prestar un libro no disponible, no se puede cambiar el libro de un préstamo existente y la fecha de devolución no puede ser anterior a la del préstamo.
