import pytest
from rest_framework.test import APIClient

from apps.questions.models import Question
from apps.questions.services import QuestionService
from apps.trivias.models import TriviaParticipant
from apps.trivias.services import ParticipationService, TriviaService
from apps.users.models import User
from apps.users.services import UserService


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin():
    return UserService.create_user(
        name="Admin", email="admin@example.com", password="admin123", role=User.Role.ADMIN
    )


@pytest.fixture
def admin_client(admin):
    client = APIClient()
    token = UserService.login_user(email="admin@example.com", password="admin123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def player():
    return UserService.create_user(
        name="Luffy", email="luffy@example.com", password="secret123"
    )


@pytest.fixture
def player_client(player):
    client = APIClient()
    token = UserService.login_user(email="luffy@example.com", password="secret123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def player2():
    return UserService.create_user(
        name="Zoro", email="zoro@example.com", password="secret123"
    )


@pytest.fixture
def player2_client(player2):
    client = APIClient()
    token = UserService.login_user(email="zoro@example.com", password="secret123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


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
class TestTriviaListCreateView:
    def test_list_trivias_as_admin(self, admin_client, trivia):
        response = admin_client.get("/trivias/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_trivias_as_player_is_forbidden(self, player_client):
        response = player_client.get("/trivias/")
        assert response.status_code == 403

    def test_list_trivias_unauthenticated_is_forbidden(self, client):
        response = client.get("/trivias/")
        assert response.status_code == 401

    def test_create_trivia_as_admin(self, admin_client, question_easy, player):
        payload = {
            "name": "New Trivia",
            "description": "Some description",
            "question_ids": [question_easy.id],
            "user_ids": [player.id],
        }
        response = admin_client.post("/trivias/", payload, format="json")
        assert response.status_code == 201
        assert response.data["name"] == "New Trivia"
        assert len(response.data["questions"]) == 1
        assert len(response.data["participants"]) == 1

    def test_create_trivia_as_player_is_forbidden(self, player_client):
        payload = {"name": "Trivia", "description": "Desc"}
        response = player_client.post("/trivias/", payload, format="json")
        assert response.status_code == 403

    def test_create_trivia_unauthenticated_is_forbidden(self, client):
        payload = {"name": "Trivia", "description": "Desc"}
        response = client.post("/trivias/", payload, format="json")
        assert response.status_code == 401


@pytest.mark.django_db
class TestTriviaDetailView:
    def test_get_trivia_as_admin(self, admin_client, trivia):
        response = admin_client.get(f"/trivias/{trivia.id}/")
        assert response.status_code == 200
        assert response.data["name"] == "One Piece Trivia"
        assert "questions" in response.data
        assert "participants" in response.data

    def test_get_trivia_shows_correct_answers_to_admin(self, admin_client, trivia):
        response = admin_client.get(f"/trivias/{trivia.id}/")
        answer = response.data["questions"][0]["answers"][0]
        assert "is_correct" in answer

    def test_get_trivia_as_player_is_forbidden(self, player_client, trivia):
        response = player_client.get(f"/trivias/{trivia.id}/")
        assert response.status_code == 403

    def test_get_trivia_not_found(self, admin_client):
        response = admin_client.get("/trivias/999/")
        assert response.status_code == 404

    def test_update_trivia_name_as_admin(self, admin_client, trivia):
        response = admin_client.put(
            f"/trivias/{trivia.id}/", {"name": "Updated"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["name"] == "Updated"

    def test_update_trivia_as_player_is_forbidden(self, player_client, trivia):
        response = player_client.put(
            f"/trivias/{trivia.id}/", {"name": "Hacked"}, format="json"
        )
        assert response.status_code == 403

    def test_update_trivia_not_found(self, admin_client):
        response = admin_client.put("/trivias/999/", {"name": "X"}, format="json")
        assert response.status_code == 404

    def test_delete_trivia_as_admin(self, admin_client, trivia):
        response = admin_client.delete(f"/trivias/{trivia.id}/")
        assert response.status_code == 204

    def test_delete_trivia_as_player_is_forbidden(self, player_client, trivia):
        response = player_client.delete(f"/trivias/{trivia.id}/")
        assert response.status_code == 403

    def test_delete_trivia_not_found(self, admin_client):
        response = admin_client.delete("/trivias/999/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestMyTriviasView:
    def test_my_trivias_as_player(self, player_client, trivia):
        response = player_client.get("/trivias/my/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "One Piece Trivia"

    def test_my_trivias_does_not_include_questions(self, player_client, trivia):
        response = player_client.get("/trivias/my/")
        assert "questions" not in response.data[0]

    def test_my_trivias_as_admin_is_forbidden(self, admin_client):
        response = admin_client.get("/trivias/my/")
        assert response.status_code == 403

    def test_my_trivias_unauthenticated_is_forbidden(self, client):
        response = client.get("/trivias/my/")
        assert response.status_code == 401

    def test_my_trivias_only_shows_assigned_trivias(self, player2_client, trivia):
        response = player2_client.get("/trivias/my/")
        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestTriviaPlayView:
    def test_play_trivia_as_player(self, player_client, trivia):
        response = player_client.get(f"/trivias/{trivia.id}/play/")
        assert response.status_code == 200
        assert response.data["name"] == "One Piece Trivia"

    def test_play_trivia_does_not_show_correct_answer(self, player_client, trivia):
        response = player_client.get(f"/trivias/{trivia.id}/play/")
        answer = response.data["questions"][0]["answers"][0]
        assert "is_correct" not in answer

    def test_play_trivia_does_not_show_difficulty(self, player_client, trivia):
        response = player_client.get(f"/trivias/{trivia.id}/play/")
        assert "difficult_level" not in response.data["questions"][0]

    def test_play_trivia_shows_completed_and_score(self, player_client, trivia):
        response = player_client.get(f"/trivias/{trivia.id}/play/")
        assert "completed" in response.data
        assert "score" in response.data
        assert response.data["completed"] is False
        assert response.data["score"] == 0

    def test_play_trivia_not_participant_is_forbidden(self, player2_client, trivia):
        response = player2_client.get(f"/trivias/{trivia.id}/play/")
        assert response.status_code == 403

    def test_play_trivia_as_admin_is_forbidden(self, admin_client, trivia):
        response = admin_client.get(f"/trivias/{trivia.id}/play/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestSubmitAnswersView:
    def test_submit_answers_as_player(self, player_client, trivia, question_easy):
        correct_answer = question_easy.answers.get(is_correct=True)
        payload = {
            "answers": [
                {"question_id": question_easy.id, "answer_id": correct_answer.id}
            ]
        }
        response = player_client.post(
            f"/trivias/{trivia.id}/answers/", payload, format="json"
        )
        assert response.status_code == 200
        assert response.data["score"] == 1
        assert response.data["completed"] is True

    def test_submit_answers_calculates_score_correctly(self, player_client, trivia, question_easy):
        wrong_answer = question_easy.answers.get(is_correct=False)
        payload = {
            "answers": [
                {"question_id": question_easy.id, "answer_id": wrong_answer.id}
            ]
        }
        response = player_client.post(
            f"/trivias/{trivia.id}/answers/", payload, format="json"
        )
        assert response.status_code == 200
        assert response.data["score"] == 0

    def test_submit_answers_already_completed_returns_400(
        self, player_client, trivia, question_easy
    ):
        correct_answer = question_easy.answers.get(is_correct=True)
        payload = {
            "answers": [
                {"question_id": question_easy.id, "answer_id": correct_answer.id}
            ]
        }
        player_client.post(f"/trivias/{trivia.id}/answers/", payload, format="json")
        response = player_client.post(
            f"/trivias/{trivia.id}/answers/", payload, format="json"
        )
        assert response.status_code == 400
        assert "already been completed" in response.data["error"]

    def test_submit_answers_not_participant_is_forbidden(
        self, player2_client, trivia, question_easy
    ):
        correct_answer = question_easy.answers.get(is_correct=True)
        payload = {
            "answers": [
                {"question_id": question_easy.id, "answer_id": correct_answer.id}
            ]
        }
        response = player2_client.post(
            f"/trivias/{trivia.id}/answers/", payload, format="json"
        )
        assert response.status_code == 403

    def test_submit_answers_as_admin_is_forbidden(
        self, admin_client, trivia, question_easy
    ):
        correct_answer = question_easy.answers.get(is_correct=True)
        payload = {
            "answers": [
                {"question_id": question_easy.id, "answer_id": correct_answer.id}
            ]
        }
        response = admin_client.post(
            f"/trivias/{trivia.id}/answers/", payload, format="json"
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestTriviaRankingView:
    def test_ranking_as_admin(self, admin_client, trivia):
        response = admin_client.get(f"/trivias/{trivia.id}/ranking/")
        assert response.status_code == 200

    def test_ranking_as_player(self, player_client, trivia):
        response = player_client.get(f"/trivias/{trivia.id}/ranking/")
        assert response.status_code == 200

    def test_ranking_unauthenticated_is_forbidden(self, client, trivia):
        response = client.get(f"/trivias/{trivia.id}/ranking/")
        assert response.status_code == 401

    def test_ranking_trivia_not_found(self, admin_client):
        response = admin_client.get("/trivias/999/ranking/")
        assert response.status_code == 404

    def test_ranking_ordered_by_score(self, admin_client, trivia, player, player2):
        TriviaParticipant.objects.get_or_create(trivia=trivia, user=player2)
        p1 = TriviaParticipant.objects.get(trivia=trivia, user=player)
        p2 = TriviaParticipant.objects.get(trivia=trivia, user=player2)
        p1.score = 6
        p1.save()
        p2.score = 2
        p2.save()
        response = admin_client.get(f"/trivias/{trivia.id}/ranking/")
        assert response.status_code == 200
        assert response.data[0]["score"] == 6
        assert response.data[1]["score"] == 2

    def test_ranking_user_only_shows_id_and_name(self, admin_client, trivia):
        response = admin_client.get(f"/trivias/{trivia.id}/ranking/")
        assert response.status_code == 200
        user_data = response.data[0]["user"]
        assert "id" in user_data
        assert "name" in user_data
        assert "email" not in user_data
        assert "role" not in user_data
