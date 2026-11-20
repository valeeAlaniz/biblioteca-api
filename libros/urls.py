from django.urls import path

from . import views

urlpatterns = [
    path("libros/", views.libro_list, name="libro-list"),
    path("libros/<int:pk>/", views.libro_detail, name="libro-detail"),
]
