from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/",
        include("products.urls"),
    ),

    path(
        "api/",
        include("orders.urls"),
    ),

    path(
        "api/store/",
        include("store.urls"),
    ),
    path(
        "api/users/",
        include("users.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )