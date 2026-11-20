from rest_framework.routers import DefaultRouter

from .viewsets import CatalogoViewSet, LibroViewSet, PrestamoViewSet

router = DefaultRouter()
router.register("libros", LibroViewSet, basename="libro")
router.register("prestamos", PrestamoViewSet, basename="prestamo")
router.register("catalogo", CatalogoViewSet, basename="catalogo")

urlpatterns = router.urls
