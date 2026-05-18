from django.core.management.base import BaseCommand

from apps.questions.models import Answer, Question
from apps.trivias.models import Trivia, TriviaParticipant
from apps.users.models import User
from apps.users.services import UserService


class Command(BaseCommand):
    help = "Seed the database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        admin = self._create_user(
            name="Admin Talana",
            email="admin@talana.com",
            password="admin123",
            role=User.Role.ADMIN,
        )
        player1 = self._create_user(
            name="Ussop",
            email="ussop@onepiece.com",
            password="ussop123",
            role=User.Role.PLAYER,
        )
        player2 = self._create_user(
            name="Nami",
            email="nami@onepiece.com",
            password="nami123",
            role=User.Role.PLAYER,
        )

        q1 = self._create_question(
            text="¿Cuál es el sueño de Ussop como pirata?",
            difficult_level=Question.Difficulty.EASY,
            answers=[
                {"text": "Convertirse en un valiente guerrero del mar", "is_correct": True},
                {"text": "Encontrar el One Piece", "is_correct": False},
                {"text": "Ser el mejor navegante del mundo", "is_correct": False},
            ],
        )
        q2 = self._create_question(
            text="¿Qué fruta del diablo comió Luffy?",
            difficult_level=Question.Difficulty.MEDIUM,
            answers=[
                {"text": "Gomu Gomu no Mi", "is_correct": True},
                {"text": "Mera Mera no Mi", "is_correct": False},
                {"text": "Hito Hito no Mi", "is_correct": False},
            ],
        )
        q3 = self._create_question(
            text="¿Cómo se llama la espada de rango más alto que usa Zoro?",
            difficult_level=Question.Difficulty.HARD,
            answers=[
                {"text": "Enma", "is_correct": True},
                {"text": "Sandai Kitetsu", "is_correct": False},
                {"text": "Shusui", "is_correct": False},
            ],
        )

        self._create_trivia(
            name="Trivia One Piece",
            description="¿Cuánto sabes del mundo de los piratas?",
            created_by=admin,
            questions=[q1, q2, q3],
            players=[player1, player2],
        )

        self.stdout.write(self.style.SUCCESS("Done! Data seeded successfully."))
        self.stdout.write("")
        self.stdout.write("Credentials:")
        self.stdout.write("  Admin   → admin@talana.com / admin123")
        self.stdout.write("  Player1 → ussop@onepiece.com / ussop123")
        self.stdout.write("  Player2 → nami@onepiece.com  / nami123")

    def _create_user(self, name, email, password, role):
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"  User {email} already exists, skipping.")
            return User.objects.get(email=email)
        user = UserService.create_user(name=name, email=email, password=password, role=role)
        self.stdout.write(f"  Created user: {email}")
        return user

    def _create_question(self, text, difficult_level, answers):
        if Question.objects.filter(text=text).exists():
            self.stdout.write(f"  Question already exists, skipping: {text[:50]}")
            return Question.objects.get(text=text)
        question = Question.objects.create(text=text, difficult_level=difficult_level)
        for answer in answers:
            Answer.objects.create(question=question, **answer)
        self.stdout.write(f"  Created question: {text[:50]}")
        return question

    def _create_trivia(self, name, description, created_by, questions, players):
        if Trivia.objects.filter(name=name).exists():
            self.stdout.write(f"  Trivia '{name}' already exists, skipping.")
            return
        trivia = Trivia.objects.create(
            name=name, description=description, created_by=created_by
        )
        trivia.questions.set(questions)
        for player in players:
            TriviaParticipant.objects.create(trivia=trivia, user=player)
        self.stdout.write(f"  Created trivia: {name}")
