from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.trivias.exceptions import ParticipantNotFound, TriviaNotFound
from apps.trivias.permissions import IsAdmin, IsAuthenticated, IsPlayer
from apps.trivias.serializers import (
    RankingSerializer,
    TriviaAnswersSerializer,
    TriviaListSerializer,
    TriviaParticipantSerializer,
    TriviaPlayerListSerializer,
    TriviaPlayerSerializer,
    TriviaReadSerializer,
    TriviaWriteSerializer,
)
from apps.trivias.services import ParticipationService, TriviaService


class TriviaListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        trivias = TriviaService.get_all_trivias()
        return Response(TriviaListSerializer(trivias, many=True).data)

    def post(self, request):
        serializer = TriviaWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        trivia = TriviaService.create_trivia(
            created_by_id=request.user.id,
            **serializer.validated_data,
        )
        return Response(
            TriviaReadSerializer(trivia).data, status=status.HTTP_201_CREATED
        )


class TriviaDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id):
        try:
            trivia = TriviaService.get_trivia_by_id(id)
        except TriviaNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(TriviaReadSerializer(trivia).data)

    def put(self, request, id):
        try:
            TriviaService.get_trivia_by_id(id)
        except TriviaNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TriviaWriteSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        trivia = TriviaService.update_trivia(id, **serializer.validated_data)
        return Response(TriviaReadSerializer(trivia).data)

    def delete(self, request, id):
        try:
            TriviaService.delete_trivia(id)
        except TriviaNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TriviaRankingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            ranking = TriviaService.get_ranking(id)
        except TriviaNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(RankingSerializer(ranking, many=True).data)


class MyTriviasView(APIView):
    permission_classes = [IsPlayer]

    def get(self, request):
        trivias = TriviaService.get_trivias_for_user(request.user.id)
        return Response(TriviaPlayerListSerializer(trivias, many=True).data)


class TriviaPlayView(APIView):
    permission_classes = [IsPlayer]

    def get(self, request, id):
        try:
            participant = ParticipationService.get_participant(id, request.user.id)
        except ParticipantNotFound:
            return Response(
                {"error": "You are not a participant in this trivia"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            trivia = TriviaService.get_trivia_by_id(id)
        except TriviaNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = TriviaPlayerSerializer(trivia).data
        data["completed"] = participant.completed
        data["score"] = participant.score
        return Response(data)


class SubmitAnswersView(APIView):
    permission_classes = [IsPlayer]

    def post(self, request, id):
        try:
            ParticipationService.get_participant(id, request.user.id)
        except ParticipantNotFound:
            return Response(
                {"error": "You are not a participant in this trivia"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = TriviaAnswersSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            participant = ParticipationService.submit_answers(
                trivia_id=id,
                user_id=request.user.id,
                answers=serializer.validated_data["answers"],
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TriviaParticipantSerializer(participant).data)
