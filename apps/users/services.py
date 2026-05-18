from typing import List, Optional

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from apps.users.exceptions import UserNotFound
from apps.users.models import User


class UserService:
    @staticmethod
    def create_user(
        name: str, email: str, password: str, role: Optional[str] = None
    ) -> User:
        """
        Create a new user with the given name, email, password and role.
        Args:
            name: str: The name of the user
            email: str: The email of the user
            password: str: The password of the user
            role: Optional[str]: The role of the user. Defaults to player
        Returns:
            User: The created user
        """
        role = role if role else User.Role.PLAYER
        return User.objects.create_user(
            name=name, email=email, password=password, role=role
        )

    @staticmethod
    def delete_user(id: int) -> None:
        """
        Delete a user by their id.
        Args:
            id: int: The id of the user to delete
        Raises:
            UserNotFound: If no user exists with the given id
        """
        user = UserService.get_user_by_id(id)
        user.delete()

    @staticmethod
    def get_admins() -> List[User]:
        """
        Retrieve all users with the admin role.
        Returns:
            List[User]: All admin users
        """
        return User.objects.filter(role=User.Role.ADMIN)

    @staticmethod
    def get_all_users() -> List[User]:
        """
        Retrieve all users regardless of role.
        Returns:
            List[User]: All users in the database
        """
        return User.objects.all()

    @staticmethod
    def get_players() -> List[User]:
        """
        Retrieve all users with the player role.
        Returns:
            List[User]: All player users
        """
        return User.objects.filter(role=User.Role.PLAYER)

    @staticmethod
    def get_user_by_id(id: int) -> User:
        """
        Retrieve a single user by their id.
        Args:
            id: int: The id of the user
        Returns:
            User: The user with the given id
        Raises:
            UserNotFound: If no user exists with the given id
        """
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise UserNotFound(f"User with id {id} not found")

    @staticmethod
    def login_user(email: str, password: str) -> Token:
        """
        Authenticate a user and return their token.
        Args:
            email: str: The email of the user
            password: str: The password of the user
        Returns:
            Token: The authentication token for the user
        Raises:
            ValueError: If the credentials are invalid
        """
        user = authenticate(username=email, password=password)
        if not user:
            raise ValueError("Invalid credentials")
        token, _ = Token.objects.get_or_create(user=user)
        return token

    @staticmethod
    def update_user(
        id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
    ) -> User:
        """
        Partially update a user's fields.
        Args:
            id: int: The id of the user to update
            name: Optional[str]: The new name of the user
            email: Optional[str]: The new email of the user
            password: Optional[str]: The new password of the user
            role: Optional[str]: The new role of the user
        Returns:
            User: The updated user
        Raises:
            ValueError: If no fields are provided
            UserNotFound: If no user exists with the given id
        """
        if not name and not email and not password and not role:
            raise ValueError("At least one field must be provided to update the user")
        user = UserService.get_user_by_id(id)
        if name:
            user.name = name
        if email:
            user.email = email
        if password:
            user.set_password(password)
        if role:
            user.role = role
        user.save()
        return user
