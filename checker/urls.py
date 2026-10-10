from django.urls import path

from . import views


urlpatterns = [
    path("", views.upload_transactions, name="upload_transactions"),
    path(
        "sample-data/",
        views.download_sample,
        name="download_sample",
    ),
]