from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_file, name="upload_file"),
    path("view/", views.view_data, name="view_data"),
    path("download/", views.download_file, name="download_file"),
]
