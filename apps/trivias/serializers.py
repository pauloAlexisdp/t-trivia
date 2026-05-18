from rest_framework import serializers

from apps.questions.serializers import QuestionPlayerSerializer, QuestionReadSerializer
from apps.trivias.models import Trivia, TriviaParticipant
from apps.users.models import User
from apps.users.serializers import UserReadSerializer


class TriviaWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    question_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=False)


class TriviaListSerializer(serializers.ModelSerializer):
    created_by = UserReadSerializer()

    class Meta:
        model = Trivia
        fields = ["id", "name", "description", "created_by"]


class TriviaParticipantSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()

    class Meta:
        model = TriviaParticipant
        fields = ["id", "user", "score", "completed"]


class TriviaReadSerializer(serializers.ModelSerializer):
    questions = QuestionReadSerializer(many=True)
    created_by = UserReadSerializer()
    participants = TriviaParticipantSerializer(
        many=True, source="triviaparticipant_set"
    )

    class Meta:
        model = Trivia
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "questions",
            "participants",
        ]


class TriviaPlayerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trivia
        fields = ["id", "name", "description"]


class TriviaPlayerSerializer(serializers.ModelSerializer):
    questions = QuestionPlayerSerializer(many=True)

    class Meta:
        model = Trivia
        fields = ["id", "name", "description", "questions"]


class RankingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name"]


class RankingSerializer(serializers.ModelSerializer):
    user = RankingUserSerializer()

    class Meta:
        model = TriviaParticipant
        fields = ["user", "score", "completed"]


class PlayerAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()


class TriviaAnswersSerializer(serializers.Serializer):
    answers = PlayerAnswerSerializer(many=True)
