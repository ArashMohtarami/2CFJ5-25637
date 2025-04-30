from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import ReservationViewSet, CustomAuthToken


router = DefaultRouter()
router.register("", ReservationViewSet, basename="reservation")


urlpatterns = [
    path("login/", CustomAuthToken.as_view(), name="api-login"),
    path("", include(router.urls)),
]
