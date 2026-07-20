from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("delete/<int:image_id>/", views.delete_image, name="delete_image"),
    path("compare/", views.compare_images, name="compare_images"),
]