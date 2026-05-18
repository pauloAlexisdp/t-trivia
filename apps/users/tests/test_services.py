import pytest

from apps.users.exceptions import UserNotFound
from apps.users.models import User
from apps.users.services import UserService


@pytest.mark.django_db
class TestCreateUser:
    def test_create_user_with_all_fields(self):
        user = UserService.create_user(
            name="Luffy",
            email="luffy@example.com",
            password="secret123",
            role=User.Role.ADMIN,
        )
        assert user.id is not None
        assert user.name == "Luffy"
        assert user.email == "luffy@example.com"
        assert user.role == User.Role.ADMIN

    def test_create_user_default_role_is_player(self):
        user = UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        assert user.role == User.Role.PLAYER

    def test_create_user_is_persisted(self):
        UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        assert User.objects.filter(email="luffy@example.com").exists()


@pytest.mark.django_db
class TestGetUserById:
    def test_get_user_by_id(self):
        user = UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        assert UserService.get_user_by_id(user.id) == user

    def test_get_user_by_id_not_found(self):
        with pytest.raises(UserNotFound):
            UserService.get_user_by_id(999)


@pytest.mark.django_db
class TestGetAllUsers:
    def test_get_all_users(self):
        UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        UserService.create_user(
            name="Zoro", email="zoro@example.com", password="secret123"
        )
        assert UserService.get_all_users().count() == 2

    def test_get_all_users_empty(self):
        assert UserService.get_all_users().count() == 0


@pytest.mark.django_db
class TestGetPlayers:
    def test_get_players(self):
        UserService.create_user(
            name="Luffy",
            email="luffy@example.com",
            password="secret123",
            role=User.Role.PLAYER,
        )
        UserService.create_user(
            name="Admin",
            email="admin@example.com",
            password="secret123",
            role=User.Role.ADMIN,
        )
        assert UserService.get_players().count() == 1

    def test_get_players_empty(self):
        assert UserService.get_players().count() == 0


@pytest.mark.django_db
class TestGetAdmins:
    def test_get_admins(self):
        UserService.create_user(
            name="Luffy",
            email="luffy@example.com",
            password="secret123",
            role=User.Role.PLAYER,
        )
        UserService.create_user(
            name="Admin",
            email="admin@example.com",
            password="secret123",
            role=User.Role.ADMIN,
        )
        assert UserService.get_admins().count() == 1

    def test_get_admins_empty(self):
        assert UserService.get_admins().count() == 0


@pytest.mark.django_db
class TestUpdateUser:
    def test_update_user_email(self):
        user = UserService.create_user(
            name="Luffy", email="luffy@example.com", password="secret123"
        )
        new_email = "luffy@gmail.com"
        UserService.update_user(user.id, email=new_email)
        assert User.objects.get(id=user.id).email == new_email

    def test_update_user_name(self):
        user = UserService.create_user(
            name="Zoro", email="zoro@example.com", password="secret123"
        )
        new_name = "Zoro Roronoa"
        UserService.update_user(id=user.id, name=new_name)
        user.refresh_from_db()
        assert user.name == new_name

    def test_update_user_password(self):
        user = UserService.create_user(
            name="Sanji", email="sanji@example.com", password="secret123"
        )
        new_password = "Sanji1234"
        UserService.update_user(id=user.id, password=new_password)
        user.refresh_from_db()
        assert user.check_password(new_password)


@pytest.mark.django_db
class TestDeleteUser:
    def test_delete_user(self):
        user = UserService.create_user(
            name="Nami", email="nami@example.com", password="secret123"
        )
        UserService.delete_user(id=user.id)
        assert not User.objects.filter(id=user.id).exists()

    def test_delete_user_not_found(self):
        with pytest.raises(UserNotFound):
            UserService.delete_user(id=999)
