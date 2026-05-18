import pytest
from rest_framework.test import APIClient

from apps.users.models import User
from apps.users.services import UserService


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_client():
    client = APIClient()
    admin = UserService.create_user(
        name="Admin",
        email="admin@example.com",
        password="admin123",
        role=User.Role.ADMIN,
    )
    token = UserService.login_user(email="admin@example.com", password="admin123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def player_client():
    client = APIClient()
    UserService.create_user(
        name="Luffy", email="luffy@example.com", password="secret123"
    )
    token = UserService.login_user(email="luffy@example.com", password="secret123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
class TestRegisterView:
    def test_register_user(self, client):
        payload = {
            "name": "Luffy",
            "email": "luffy@example.com",
            "password": "secret123",
        }
        response = client.post("/register/", payload)
        assert response.status_code == 201
        assert response.data["name"] == "Luffy"
        assert response.data["email"] == "luffy@example.com"
        assert "password" not in response.data

    def test_register_always_creates_player(self, client):
        payload = {
            "name": "Luffy",
            "email": "luffy@example.com",
            "password": "secret123",
            "role": "admin",
        }
        response = client.post("/register/", payload)
        assert response.status_code == 201
        assert response.data["role"] == User.Role.PLAYER

    def test_register_invalid_data(self, client):
        response = client.post("/register/", {})
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:
    def test_login_user(self, client):
        UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        response = client.post(
            "/login/", {"email": "luffy@example.com", "password": "secret123"}
        )
        assert response.status_code == 200
        assert "token" in response.data

    def test_login_invalid_credentials(self, client):
        response = client.post(
            "/login/", {"email": "luffy@example.com", "password": "wrong"}
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserListCreateView:
    def test_list_users_as_admin(self, admin_client):
        response = admin_client.get("/users/")
        assert response.status_code == 200

    def test_list_users_as_player_is_forbidden(self, player_client):
        response = player_client.get("/users/")
        assert response.status_code == 403

    def test_list_users_unauthenticated_is_forbidden(self, client):
        response = client.get("/users/")
        assert response.status_code == 401

    def test_create_user_as_admin(self, admin_client):
        payload = {
            "name": "Zoro",
            "email": "zoro@example.com",
            "password": "secret123",
            "role": "admin",
        }
        response = admin_client.post("/users/", payload)
        assert response.status_code == 201
        assert response.data["role"] == User.Role.ADMIN

    def test_create_user_as_player_is_forbidden(self, player_client):
        payload = {"name": "Zoro", "email": "zoro@example.com", "password": "secret123"}
        response = player_client.post("/users/", payload)
        assert response.status_code == 403


@pytest.mark.django_db
class TestPlayerListView:
    def test_list_players_as_admin(self, admin_client):
        UserService.create_user(
            name="Luffy",
            email="luffy@example.com",
            password="secret123",
            role=User.Role.PLAYER,
        )
        UserService.create_user(
            name="Zoro",
            email="zoro@example.com",
            password="secret123",
            role=User.Role.ADMIN,
        )
        response = admin_client.get("/users/players/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_players_as_player_is_forbidden(self, player_client):
        response = player_client.get("/users/players/")
        assert response.status_code == 403

    def test_list_players_unauthenticated_is_forbidden(self, client):
        response = client.get("/users/players/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestAdminListView:
    def test_list_admins_as_admin(self, admin_client):
        UserService.create_user(
            name="Luffy",
            email="luffy@example.com",
            password="secret123",
            role=User.Role.PLAYER,
        )
        response = admin_client.get("/users/admins/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_admins_as_player_is_forbidden(self, player_client):
        response = player_client.get("/users/admins/")
        assert response.status_code == 403

    def test_list_admins_unauthenticated_is_forbidden(self, client):
        response = client.get("/users/admins/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserDetailDeleteUpdateView:
    def test_get_user_as_admin(self, admin_client):
        user = UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        response = admin_client.get(f"/users/{user.id}/")
        assert response.status_code == 200
        assert response.data["email"] == "luffy@example.com"

    def test_get_own_user_as_player(self, player_client):
        user = User.objects.get(email="luffy@example.com")
        response = player_client.get(f"/users/{user.id}/")
        assert response.status_code == 200

    def test_get_other_user_as_player_is_forbidden(self, player_client):
        other = UserService.create_user(
            name="Zoro", email="zoro@example.com", password="secret123"
        )
        response = player_client.get(f"/users/{other.id}/")
        assert response.status_code == 403

    def test_get_user_not_found(self, admin_client):
        response = admin_client.get("/users/999/")
        assert response.status_code == 404

    def test_update_user_as_admin(self, admin_client):
        user = UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        response = admin_client.put(f"/users/{user.id}/", {"email": "luffy@gmail.com"})
        assert response.status_code == 200
        assert response.data["email"] == "luffy@gmail.com"

    def test_update_own_user_as_player(self, player_client):
        user = User.objects.get(email="luffy@example.com")
        response = player_client.put(f"/users/{user.id}/", {"name": "Luffy Updated"})
        assert response.status_code == 200
        assert response.data["name"] == "Luffy Updated"

    def test_update_other_user_as_player_is_forbidden(self, player_client):
        other = UserService.create_user(
            name="Zoro", email="zoro@example.com", password="secret123"
        )
        response = player_client.put(f"/users/{other.id}/", {"name": "Hacked"})
        assert response.status_code == 403

    def test_update_user_not_found(self, admin_client):
        response = admin_client.put("/users/999/", {"email": "luffy@gmail.com"})
        assert response.status_code == 404

    def test_delete_user_as_admin(self, admin_client):
        user = UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        response = admin_client.delete(f"/users/{user.id}/")
        assert response.status_code == 204

    def test_delete_user_not_found(self, admin_client):
        response = admin_client.delete("/users/999/")
        assert response.status_code == 404

    def test_delete_user_as_player_is_forbidden(self, player_client):
        user = User.objects.get(email="luffy@example.com")
        response = player_client.delete(f"/users/{user.id}/")
        assert response.status_code == 403
