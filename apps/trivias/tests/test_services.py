import pytest

from apps.questions.models import Question
from apps.questions.services import QuestionService
from apps.trivias.exceptions import ParticipantNotFound, TriviaNotFound
from apps.trivias.models import Trivia, TriviaParticipant
from apps.trivias.services import ParticipationService, TriviaService
from apps.users.models import User
from apps.users.services import UserService


@pytest.fixture
def admin():
    return UserService.create_user(
        name="Admin", email="admin@example.com", password="admin123", role=User.Role.ADMIN
    )


@pytest.fixture
def player():
    return UserService.create_user(
        name="Luffy", email="luffy@example.com", password="secret123"
    )


@pytest.fixture
def player2():
    return UserService.create_user(
        name="Zoro", email="zoro@example.com", password="secret123"
    )


@pytest.fixture
def question_easy():
    return QuestionService.create_question(
        text="What is Luffy's dream?",
        difficult_level=Question.Difficulty.EASY,
        answers=[
            {"text": "King of the Pirates", "is_correct": True},
            {"text": "Best swordsman", "is_correct": False},
        ],
    )


@pytest.fixture
def question_medium():
    return QuestionService.create_question(
        text="What fruit did Luffy eat?",
        difficult_level=Question.Difficulty.MEDIUM,
        answers=[
            {"text": "Gomu Gomu no Mi", "is_correct": True},
            {"text": "Mera Mera no Mi", "is_correct": False},
        ],
    )


@pytest.fixture
def question_hard():
    return QuestionService.create_question(
        text="What is Zoro's highest ranked sword?",
        difficult_level=Question.Difficulty.HARD,
        answers=[
            {"text": "Enma", "is_correct": True},
            {"text": "Shusui", "is_correct": False},
        ],
    )


@pytest.fixture
def trivia(admin, question_easy, player):
    return TriviaService.create_trivia(
        name="One Piece Trivia",
        description="Test your One Piece knowledge",
        created_by_id=admin.id,
        question_ids=[question_easy.id],
        user_ids=[player.id],
    )


@pytest.mark.django_db
class TestTriviaExists:
    def test_trivia_exists_returns_true(self, trivia):
        assert TriviaService._trivia_exists(trivia.id) is True

    def test_trivia_exists_returns_false(self):
        assert TriviaService._trivia_exists(999) is False


@pytest.mark.django_db
class TestCreateTrivia:
    def test_create_trivia_is_persisted(self, admin):
        trivia = TriviaService.create_trivia(
            name="Trivia", description="Desc", created_by_id=admin.id
        )
        assert Trivia.objects.filter(id=trivia.id).exists()

    def test_create_trivia_assigns_questions(self, admin, question_easy, question_medium):
        trivia = TriviaService.create_trivia(
            name="Trivia",
            description="Desc",
            created_by_id=admin.id,
            question_ids=[question_easy.id, question_medium.id],
        )
        assert trivia.questions.count() == 2

    def test_create_trivia_assigns_participants(self, admin, player, player2):
        trivia = TriviaService.create_trivia(
            name="Trivia",
            description="Desc",
            created_by_id=admin.id,
            user_ids=[player.id, player2.id],
        )
        assert TriviaParticipant.objects.filter(trivia=trivia).count() == 2

    def test_create_trivia_without_questions_and_users(self, admin):
        trivia = TriviaService.create_trivia(
            name="Trivia", description="Desc", created_by_id=admin.id
        )
        assert trivia.questions.count() == 0
        assert TriviaParticipant.objects.filter(trivia=trivia).count() == 0


@pytest.mark.django_db
class TestGetAllTrivias:
    def test_get_all_trivias(self, trivia):
        assert TriviaService.get_all_trivias().count() == 1

    def test_get_all_trivias_empty(self):
        assert TriviaService.get_all_trivias().count() == 0


@pytest.mark.django_db
class TestGetTriviaById:
    def test_get_trivia_by_id(self, trivia):
        result = TriviaService.get_trivia_by_id(trivia.id)
        assert result.id == trivia.id

    def test_get_trivia_by_id_not_found(self):
        with pytest.raises(TriviaNotFound):
            TriviaService.get_trivia_by_id(999)


@pytest.mark.django_db
class TestUpdateTrivia:
    def test_update_trivia_name(self, trivia):
        updated = TriviaService.update_trivia(trivia.id, name="Updated Name")
        assert updated.name == "Updated Name"

    def test_update_trivia_description(self, trivia):
        updated = TriviaService.update_trivia(trivia.id, description="New desc")
        assert updated.description == "New desc"

    def test_update_trivia_question_ids_replaces_questions(self, trivia, question_medium):
        updated = TriviaService.update_trivia(trivia.id, question_ids=[question_medium.id])
        assert updated.questions.count() == 1
        assert updated.questions.first().id == question_medium.id

    def test_update_trivia_user_ids_adds_participants(self, trivia, player2):
        TriviaService.update_trivia(trivia.id, user_ids=[player2.id])
        assert TriviaParticipant.objects.filter(trivia=trivia).count() == 2

    def test_update_trivia_not_found(self):
        with pytest.raises(TriviaNotFound):
            TriviaService.update_trivia(999, name="X")


@pytest.mark.django_db
class TestDeleteTrivia:
    def test_delete_trivia(self, trivia):
        TriviaService.delete_trivia(trivia.id)
        assert not Trivia.objects.filter(id=trivia.id).exists()

    def test_delete_trivia_not_found(self):
        with pytest.raises(TriviaNotFound):
            TriviaService.delete_trivia(999)


@pytest.mark.django_db
class TestGetTriviasForUser:
    def test_get_trivias_for_user(self, trivia, player):
        result = TriviaService.get_trivias_for_user(player.id)
        assert result.count() == 1

    def test_get_trivias_for_user_empty(self, player2):
        assert TriviaService.get_trivias_for_user(player2.id).count() == 0


@pytest.mark.django_db
class TestGetRanking:
    def test_get_ranking_trivia_not_found(self):
        with pytest.raises(TriviaNotFound):
            TriviaService.get_ranking(999)

    def test_get_ranking_ordered_by_score(self, trivia, player, player2, admin, question_easy):
        TriviaParticipant.objects.get_or_create(trivia=trivia, user=player2)
        p1 = TriviaParticipant.objects.get(trivia=trivia, user=player)
        p2 = TriviaParticipant.objects.get(trivia=trivia, user=player2)
        p1.score = 6
        p1.save()
        p2.score = 2
        p2.save()
        ranking = TriviaService.get_ranking(trivia.id)
        assert ranking[0].score == 6
        assert ranking[1].score == 2


@pytest.mark.django_db
class TestGetParticipant:
    def test_get_participant(self, trivia, player):
        participant = ParticipationService.get_participant(trivia.id, player.id)
        assert participant.trivia == trivia
        assert participant.user == player

    def test_get_participant_not_found(self, trivia, player2):
        with pytest.raises(ParticipantNotFound):
            ParticipationService.get_participant(trivia.id, player2.id)


@pytest.mark.django_db
class TestSubmitAnswers:
    def test_submit_correct_answers_calculates_score(self, trivia, player, question_easy):
        correct_answer = question_easy.answers.get(is_correct=True)
        participant = ParticipationService.submit_answers(
            trivia_id=trivia.id,
            user_id=player.id,
            answers=[{"question_id": question_easy.id, "answer_id": correct_answer.id}],
        )
        assert participant.score == 1

    def test_submit_incorrect_answers_score_is_zero(self, trivia, player, question_easy):
        wrong_answer = question_easy.answers.get(is_correct=False)
        participant = ParticipationService.submit_answers(
            trivia_id=trivia.id,
            user_id=player.id,
            answers=[{"question_id": question_easy.id, "answer_id": wrong_answer.id}],
        )
        assert participant.score == 0

    def test_submit_answers_marks_completed(self, trivia, player, question_easy):
        correct_answer = question_easy.answers.get(is_correct=True)
        participant = ParticipationService.submit_answers(
            trivia_id=trivia.id,
            user_id=player.id,
            answers=[{"question_id": question_easy.id, "answer_id": correct_answer.id}],
        )
        assert participant.completed is True

    def test_submit_answers_already_completed_raises_error(self, trivia, player, question_easy):
        correct_answer = question_easy.answers.get(is_correct=True)
        ParticipationService.submit_answers(
            trivia_id=trivia.id,
            user_id=player.id,
            answers=[{"question_id": question_easy.id, "answer_id": correct_answer.id}],
        )
        with pytest.raises(ValueError, match="already been completed"):
            ParticipationService.submit_answers(
                trivia_id=trivia.id,
                user_id=player.id,
                answers=[{"question_id": question_easy.id, "answer_id": correct_answer.id}],
            )

    def test_submit_answers_question_not_in_trivia_raises_error(
        self, trivia, player, question_medium
    ):
        answer = question_medium.answers.first()
        with pytest.raises(ValueError, match="does not belong to this trivia"):
            ParticipationService.submit_answers(
                trivia_id=trivia.id,
                user_id=player.id,
                answers=[{"question_id": question_medium.id, "answer_id": answer.id}],
            )

    def test_submit_answers_answer_not_in_question_raises_error(
        self, trivia, player, question_easy, question_medium
    ):
        wrong_answer = question_medium.answers.first()
        with pytest.raises(ValueError, match="does not belong to question"):
            ParticipationService.submit_answers(
                trivia_id=trivia.id,
                user_id=player.id,
                answers=[{"question_id": question_easy.id, "answer_id": wrong_answer.id}],
            )

    def test_submit_answers_score_by_difficulty(self, admin, player, question_easy, question_medium, question_hard):
        trivia = TriviaService.create_trivia(
            name="Full Trivia",
            description="All difficulties",
            created_by_id=admin.id,
            question_ids=[question_easy.id, question_medium.id, question_hard.id],
            user_ids=[player.id],
        )
        answers = [
            {"question_id": question_easy.id, "answer_id": question_easy.answers.get(is_correct=True).id},
            {"question_id": question_medium.id, "answer_id": question_medium.answers.get(is_correct=True).id},
            {"question_id": question_hard.id, "answer_id": question_hard.answers.get(is_correct=True).id},
        ]
        participant = ParticipationService.submit_answers(
            trivia_id=trivia.id, user_id=player.id, answers=answers
        )
        assert participant.score == 6
