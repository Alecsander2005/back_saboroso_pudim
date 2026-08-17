from rest_framework.routers import DefaultRouter

from .views import StoreSettingsViewSet


router = DefaultRouter()

router.register(
    "settings",
    StoreSettingsViewSet,
    basename="store-settings"
)

urlpatterns = router.urls