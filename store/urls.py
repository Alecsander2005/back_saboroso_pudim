from rest_framework.routers import DefaultRouter

from .views import StoreSettingsViewSet


router = DefaultRouter()

router.register(
    "store",
    StoreSettingsViewSet,
    basename="store"
)

urlpatterns = router.urls