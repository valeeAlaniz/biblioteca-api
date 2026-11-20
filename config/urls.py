from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("libros.urls")),
    # Login por sesión para la interfaz web de DRF (autenticación opcional)
    path("api-auth/", include("rest_framework.urls")),
]
