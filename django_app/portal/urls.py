from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("modelos/mm1/", views.model_mm1, name="mm1"),
    path("modelos/mms/", views.model_mms, name="mms"),
    path("api/queue/", views.queue_api, name="queue_api"),
]
