from django.urls import path
from . import views

urlpatterns = [
    path("control/", views.control, name="propresenter_control"),
]
