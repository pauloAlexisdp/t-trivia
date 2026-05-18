from django.urls import path

from apps.users.views import (
    AdminListView,
    LoginView,
    PlayerListView,
    RegisterView,
    UserDetailDeleteUpdateView,
    UserListCreateView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/players/", PlayerListView.as_view(), name="user-players"),
    path("users/admins/", AdminListView.as_view(), name="user-admins"),
    path(
        "users/<int:id>/",
        UserDetailDeleteUpdateView.as_view(),
        name="user-detail-delete-update",
    ),
]
