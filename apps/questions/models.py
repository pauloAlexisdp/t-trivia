from django.db import models


class Question(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Fácil"
        MEDIUM = "medium", "Medio"
        HARD = "hard", "Difícil"

    text = models.TextField()
    difficult_level = models.CharField(
        max_length=10, choices=Difficulty.choices, default=Difficulty.EASY
    )


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
