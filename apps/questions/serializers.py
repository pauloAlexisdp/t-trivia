from rest_framework import serializers

from apps.questions.models import Answer, Question


class AnswerReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]


class AnswerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["text", "is_correct"]


class AnswerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["text"]


class QuestionReadSerializer(serializers.ModelSerializer):
    answers = AnswerReadSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "difficult_level", "answers"]


class AnswerPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text"]


class QuestionPlayerSerializer(serializers.ModelSerializer):
    answers = AnswerPlayerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "answers"]


class QuestionWriteSerializer(serializers.ModelSerializer):
    answers = AnswerWriteSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ["text", "difficult_level", "answers"]
        extra_kwargs = {"difficult_level": {"required": False}}
