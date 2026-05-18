from django.db import models


class Trivia(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    questions = models.ManyToManyField("questions.Question")
    participants = models.ManyToManyField(
        "users.User", through="TriviaParticipant", related_name="trivias"
    )
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="created_trivias"
    )

    def __str__(self):
        return self.name


class TriviaParticipant(models.Model):
    trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("trivia", "user")

    def __str__(self):
        return f"{self.user} - {self.trivia}"


class TriviaAnswer(models.Model):
    participant = models.ForeignKey(
        TriviaParticipant, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    selected_option = models.ForeignKey("questions.Answer", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("participant", "question")

    def __str__(self):
        return f"{self.participant} - {self.question}"
