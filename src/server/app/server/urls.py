from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda a: redirect('ui/vacancies')),
    path("ui/", include("ui.urls")),
    path("admin/", admin.site.urls),
]