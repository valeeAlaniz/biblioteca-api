from django.contrib.auth.models import User
from rest_framework.test import APITestCase

CLAVE = "UnaClaveSegura2026"


class AutenticacionJwtTests(APITestCase):
    def registrar(self, **extra):
        datos = {"username": "ana", "password": CLAVE}
        datos.update(extra)
        return self.client.post("/api/auth/registro/", datos, format="json")

    def obtener_tokens(self):
        respuesta = self.client.post(
            "/api/auth/token/",
            {"username": "ana", "password": CLAVE},
            format="json",
        )
        return respuesta

    def test_registro_crea_un_usuario_comun(self):
        respuesta = self.registrar()
        self.assertEqual(respuesta.status_code, 201)
        usuario = User.objects.get(username="ana")
        self.assertFalse(usuario.is_staff)
        self.assertNotIn("password", respuesta.data)

    def test_registro_rechaza_clave_debil(self):
        respuesta = self.registrar(password="123")
        self.assertEqual(respuesta.status_code, 400)

    def test_registro_rechaza_usuario_repetido(self):
        self.registrar()
        respuesta = self.registrar()
        self.assertEqual(respuesta.status_code, 400)

    def test_login_devuelve_access_y_refresh(self):
        self.registrar()
        respuesta = self.obtener_tokens()
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("access", respuesta.data)
        self.assertIn("refresh", respuesta.data)

    def test_login_con_clave_incorrecta_da_401(self):
        self.registrar()
        respuesta = self.client.post(
            "/api/auth/token/",
            {"username": "ana", "password": "incorrecta"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_sin_token_no_se_accede_a_prestamos(self):
        respuesta = self.client.get("/api/prestamos/")
        self.assertEqual(respuesta.status_code, 401)

    def test_con_token_se_accede_a_prestamos(self):
        self.registrar()
        access = self.obtener_tokens().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        respuesta = self.client.get("/api/prestamos/")
        self.assertEqual(respuesta.status_code, 200)

    def test_token_invalido_da_401(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token-falso")
        respuesta = self.client.get("/api/prestamos/")
        self.assertEqual(respuesta.status_code, 401)

    def test_refresh_entrega_un_access_nuevo(self):
        self.registrar()
        refresh = self.obtener_tokens().data["refresh"]
        respuesta = self.client.post(
            "/api/auth/token/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("access", respuesta.data)
