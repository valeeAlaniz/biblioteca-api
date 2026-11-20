from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Libro


class LibroApiTests(APITestCase):
    def setUp(self):
        self.libro = Libro.objects.create(
            titulo="Rayuela",
            autor="Julio Cortázar",
            anio_publicacion=1963,
            isbn="978-84-376-0494-7",
        )

    def datos(self, **extra):
        base = {
            "titulo": "El Aleph",
            "autor": "Jorge Luis Borges",
            "anio_publicacion": 1949,
            "isbn": "978-0-14-118013-9",
        }
        base.update(extra)
        return base

    def test_listar(self):
        respuesta = self.client.get("/api/libros/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.data), 1)

    def test_filtrar_por_autor(self):
        Libro.objects.create(
            titulo="Ficciones", autor="Borges", anio_publicacion=1944, isbn="1"
        )
        respuesta = self.client.get("/api/libros/?autor=borges")
        self.assertEqual(len(respuesta.data), 1)

    def test_filtrar_por_disponible(self):
        self.libro.disponible = False
        self.libro.save()
        respuesta = self.client.get("/api/libros/?disponible=true")
        self.assertEqual(len(respuesta.data), 0)

    def test_crear(self):
        respuesta = self.client.post("/api/libros/", self.datos(), format="json")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Libro.objects.count(), 2)

    def test_crear_con_anio_futuro_falla(self):
        anio = timezone.localdate().year + 1
        respuesta = self.client.post(
            "/api/libros/", self.datos(anio_publicacion=anio), format="json"
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_crear_con_isbn_repetido_falla(self):
        respuesta = self.client.post(
            "/api/libros/", self.datos(isbn=self.libro.isbn), format="json"
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_crear_sin_titulo_falla(self):
        datos = self.datos()
        del datos["titulo"]
        respuesta = self.client.post("/api/libros/", datos, format="json")
        self.assertEqual(respuesta.status_code, 400)

    def test_detalle(self):
        respuesta = self.client.get(f"/api/libros/{self.libro.id}/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["titulo"], "Rayuela")

    def test_detalle_inexistente_da_404(self):
        respuesta = self.client.get("/api/libros/9999/")
        self.assertEqual(respuesta.status_code, 404)

    def test_put_reemplaza(self):
        respuesta = self.client.put(
            f"/api/libros/{self.libro.id}/", self.datos(), format="json"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.titulo, "El Aleph")

    def test_patch_edita_un_campo(self):
        respuesta = self.client.patch(
            f"/api/libros/{self.libro.id}/", {"disponible": False}, format="json"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.libro.refresh_from_db()
        self.assertFalse(self.libro.disponible)
        self.assertEqual(self.libro.titulo, "Rayuela")

    def test_eliminar(self):
        respuesta = self.client.delete(f"/api/libros/{self.libro.id}/")
        self.assertEqual(respuesta.status_code, 204)
        self.assertEqual(Libro.objects.count(), 0)
