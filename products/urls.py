from rest_framework.routers import DefaultRouter

from .views import (
    ProductSizeViewSet,
    ProductViewSet,
)


router = DefaultRouter()

router.register(
    "products",
    ProductViewSet,
    basename="products"
)

router.register(
    "product-sizes",
    ProductSizeViewSet,
    basename="product-sizes"
)

urlpatterns = router.urls