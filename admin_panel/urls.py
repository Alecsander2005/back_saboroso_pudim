from django.urls import path
from .views import login_view, dashboard_view


urlpatterns = [
    path("", login_view, name="admin-login"),
    path("dashboard/", dashboard_view, name="admin-dashboard"),
    path("admin.html", dashboard_view, name="admin-html"),
]