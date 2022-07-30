from urllib.parse import urlparse
from django.urls import path
from webapps.image_process import views

urlpatterns = [
    path("", views.ImageView.as_view()),
    path("save/", views.ImageDownload.as_view())
]
