from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# in records/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.document_list, name="document_list"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="records/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
