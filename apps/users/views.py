from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.exceptions import UserNotFound
from apps.users.models import User
from apps.users.permissions import IsAdmin, IsAdminOrSelf
from apps.users.serializers import (
    LoginSerializer,
    UserReadSerializer,
    UserWriteSerializer,
)
from apps.users.services import UserService


class RegisterView(APIView):
    def post(self, request):
        serializer = UserWriteSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data["role"] = User.Role.PLAYER
            user = UserService.create_user(**data)
            return Response(
                UserReadSerializer(user).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = UserService.login_user(**serializer.validated_data)
            except ValueError:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = UserService.get_all_users()
        serializer = UserReadSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserWriteSerializer(data=request.data)
        if serializer.is_valid():
            user = UserService.create_user(**serializer.validated_data)
            return Response(
                UserReadSerializer(user).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        players = UserService.get_players()
        serializer = UserReadSerializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        admins = UserService.get_admins()
        serializer = UserReadSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailDeleteUpdateView(APIView):

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdmin()]
        return [IsAdminOrSelf()]

    def get(self, request, id):
        try:
            user = UserService.get_user_by_id(id)
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, user)
        serializer = UserReadSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            user = UserService.get_user_by_id(id)
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, user)
        serializer = UserWriteSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserService.update_user(id, **serializer.validated_data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserReadSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        try:
            UserService.delete_user(id)
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
