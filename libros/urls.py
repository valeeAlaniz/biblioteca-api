from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .usuarios import RegistroView

urlpatterns = [
    # Autenticación
    path("auth/registro/", RegistroView.as_view(), name="registro"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # ViewSets registrados en el router
    path("", include("libros.routers")),
]
