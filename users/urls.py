from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers
from users.views import CustomUserViewSet, my_profile

router = routers.DefaultRouter()
router.register("", CustomUserViewSet, basename="users")


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", my_profile, name="my-profile"),
    path("", include(router.urls)),
]

app_name = "users"
