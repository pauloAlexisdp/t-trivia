from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.exceptions import AnswerNotFound, QuestionNotFound
from apps.questions.permissions import IsAdmin
from apps.questions.serializers import (
    AnswerReadSerializer,
    AnswerUpdateSerializer,
    AnswerWriteSerializer,
    QuestionReadSerializer,
    QuestionWriteSerializer,
)
from apps.questions.services import AnswerService, QuestionService


class QuestionCreateListView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = QuestionWriteSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            question = QuestionService.create_question(**data)
            return Response(
                QuestionReadSerializer(question).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        questions = QuestionService.get_all_questions()
        serializer = QuestionReadSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionDetailDeleteUpdateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id):
        try:
            question = QuestionService.get_question_by_id(id)
        except QuestionNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionReadSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            QuestionService.get_question_by_id(id)
        except QuestionNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionWriteSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            question = QuestionService.update_question(id, **serializer.validated_data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            QuestionReadSerializer(question).data, status=status.HTTP_200_OK
        )

    def delete(self, request, id):
        try:
            QuestionService.delete_question(id)
        except QuestionNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnswerCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, question_id):
        try:
            QuestionService.get_question_by_id(question_id)
        except QuestionNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            answer = AnswerService.create_answer(
                question_id, **serializer.validated_data
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            AnswerReadSerializer(answer).data, status=status.HTTP_201_CREATED
        )


class AnswerDetailView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, question_id, answer_id):
        try:
            AnswerService.get_answer(question_id, answer_id)
        except (QuestionNotFound, AnswerNotFound):
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            answer = AnswerService.update_answer(
                question_id, answer_id, **serializer.validated_data
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AnswerReadSerializer(answer).data, status=status.HTTP_200_OK)

    def delete(self, request, question_id, answer_id):
        try:
            AnswerService.delete_answer(question_id, answer_id)
        except (QuestionNotFound, AnswerNotFound):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
