from django.urls import path

from . import prestamos_views, views

urlpatterns = [
    # Práctico 1: vistas funcionales con @api_view
    path("libros/", views.libro_list, name="libro-list"),
    path("libros/<int:pk>/", views.libro_detail, name="libro-detail"),
    # Práctico 2: vistas basadas en clases
    path(
        "libros/<int:pk>/detalle/",
        prestamos_views.LibroDetalleView.as_view(),
        name="libro-detalle",
    ),
    path(
        "prestamos/",
        prestamos_views.PrestamoListCreateView.as_view(),
        name="prestamo-list",
    ),
    path(
        "prestamos/<int:pk>/",
        prestamos_views.PrestamoDetailView.as_view(),
        name="prestamo-detail",
    ),
]
