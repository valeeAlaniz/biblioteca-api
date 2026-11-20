from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Libro, Prestamo

CLAVE = "UnaClaveSegura2026"


class PrestamoApiTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user("ana", password=CLAVE)
        self.admin = User.objects.create_user("admin", password=CLAVE, is_staff=True)
        self.client.force_authenticate(self.usuario)
        self.libro = Libro.objects.create(
            titulo="Rayuela",
            autor="Julio Cortázar",
            anio_publicacion=1963,
            isbn="978-84-376-0494-7",
        )
        self.otro = Libro.objects.create(
            titulo="El Aleph",
            autor="Borges",
            anio_publicacion=1949,
            isbn="978-0-14-118013-9",
        )

    def crear(self, **extra):
        datos = {"libro_id": self.libro.id, "lector": "Ana"}
        datos.update(extra)
        return self.client.post("/api/prestamos/", datos, format="json")

    def test_crear_devuelve_el_libro_anidado(self):
        respuesta = self.crear()
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data["libro"]["titulo"], "Rayuela")
        self.assertFalse(respuesta.data["devuelto"])

    def test_crear_deja_el_libro_no_disponible(self):
        self.crear()
        self.libro.refresh_from_db()
        self.assertFalse(self.libro.disponible)

    def test_no_se_presta_un_libro_no_disponible(self):
        self.crear()
        respuesta = self.crear(lector="Beto")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("libro_id", respuesta.data)

    def test_crear_con_libro_inexistente_falla(self):
        respuesta = self.crear(libro_id=9999)
        self.assertEqual(respuesta.status_code, 400)

    def test_crear_sin_lector_falla(self):
        respuesta = self.client.post(
            "/api/prestamos/", {"libro_id": self.libro.id}, format="json"
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_fecha_de_devolucion_anterior_falla(self):
        respuesta = self.crear(
            fecha_prestamo="2026-05-10", fecha_devolucion="2026-05-01"
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_listar_trae_libros_anidados(self):
        self.crear()
        respuesta = self.client.get("/api/prestamos/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(respuesta.data[0]["libro"]["autor"], "Julio Cortázar")

    def test_filtrar_por_devuelto(self):
        Prestamo.objects.create(libro=self.libro, lector="Ana", devuelto=True)
        Prestamo.objects.create(libro=self.otro, lector="Beto")
        respuesta = self.client.get("/api/prestamos/?devuelto=false")
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(respuesta.data[0]["lector"], "Beto")

    def test_filtrar_por_libro(self):
        Prestamo.objects.create(libro=self.libro, lector="Ana")
        Prestamo.objects.create(libro=self.otro, lector="Beto")
        respuesta = self.client.get(f"/api/prestamos/?libro={self.otro.id}")
        self.assertEqual(len(respuesta.data), 1)

    def test_detalle_del_prestamo(self):
        prestamo_id = self.crear().data["id"]
        respuesta = self.client.get(f"/api/prestamos/{prestamo_id}/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["lector"], "Ana")

    def test_detalle_inexistente_da_404(self):
        respuesta = self.client.get("/api/prestamos/9999/")
        self.assertEqual(respuesta.status_code, 404)

    def test_devolver_con_patch_libera_el_libro_y_pone_la_fecha(self):
        prestamo_id = self.crear().data["id"]
        respuesta = self.client.patch(
            f"/api/prestamos/{prestamo_id}/", {"devuelto": True}, format="json"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.data["fecha_devolucion"], str(timezone.localdate())
        )
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)

    def test_accion_devolver(self):
        prestamo_id = self.crear().data["id"]
        respuesta = self.client.post(f"/api/prestamos/{prestamo_id}/devolver/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.data["devuelto"])
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)

    def test_devolver_dos_veces_falla(self):
        prestamo_id = self.crear().data["id"]
        self.client.post(f"/api/prestamos/{prestamo_id}/devolver/")
        respuesta = self.client.post(f"/api/prestamos/{prestamo_id}/devolver/")
        self.assertEqual(respuesta.status_code, 400)

    def test_put_actualiza_el_lector(self):
        prestamo_id = self.crear().data["id"]
        respuesta = self.client.put(
            f"/api/prestamos/{prestamo_id}/",
            {"libro_id": self.libro.id, "lector": "Carla"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["lector"], "Carla")

    def test_no_se_puede_cambiar_el_libro_de_un_prestamo(self):
        prestamo_id = self.crear().data["id"]
        respuesta = self.client.patch(
            f"/api/prestamos/{prestamo_id}/",
            {"libro_id": self.otro.id},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_usuario_comun_no_puede_borrar_un_prestamo(self):
        prestamo_id = self.crear().data["id"]
        respuesta = self.client.delete(f"/api/prestamos/{prestamo_id}/")
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Prestamo.objects.count(), 1)

    def test_admin_borra_un_prestamo_abierto_y_libera_el_libro(self):
        prestamo_id = self.crear().data["id"]
        self.client.force_authenticate(self.admin)
        respuesta = self.client.delete(f"/api/prestamos/{prestamo_id}/")
        self.assertEqual(respuesta.status_code, 204)
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)
        self.assertEqual(Prestamo.objects.count(), 0)

    def test_anonimo_no_puede_ver_prestamos(self):
        self.client.force_authenticate(None)
        respuesta = self.client.get("/api/prestamos/")
        self.assertEqual(respuesta.status_code, 401)

    def test_anonimo_no_puede_crear_prestamos(self):
        self.client.force_authenticate(None)
        respuesta = self.crear()
        self.assertEqual(respuesta.status_code, 401)

    def test_detalle_del_libro_trae_los_prestamos_anidados(self):
        self.crear()
        respuesta = self.client.get(f"/api/libros/{self.libro.id}/detalle/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["titulo"], "Rayuela")
        self.assertEqual(len(respuesta.data["prestamos"]), 1)
        self.assertEqual(respuesta.data["prestamos"][0]["lector"], "Ana")
