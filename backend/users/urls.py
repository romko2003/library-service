from django.urls import path
from .views import RegisterView, MeView, TokenView, TokenRefresh

urlpatterns = [
    path("", RegisterView.as_view(), name="register"),
    path("token/", TokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefresh.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
]
