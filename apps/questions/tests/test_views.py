import pytest
from rest_framework.test import APIClient

from apps.questions.models import Question
from apps.questions.services import QuestionService
from apps.users.models import User
from apps.users.services import UserService


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_client():
    client = APIClient()
    UserService.create_user(
        name="Admin",
        email="admin@example.com",
        password="admin123",
        role=User.Role.ADMIN,
    )
    token = UserService.login_user(email="admin@example.com", password="admin123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def player_client():
    client = APIClient()
    UserService.create_user(
        name="Luffy", email="luffy@example.com", password="secret123"
    )
    token = UserService.login_user(email="luffy@example.com", password="secret123")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
class TestQuestionCreateListView:
    def test_create_question_as_admin(self, admin_client):
        payload = {
            "text": "Who will become the king of the pirates?",
            "difficult_level": "hard",
            "answers": [
                {"text": "Luffy", "is_correct": True},
                {"text": "Zoro", "is_correct": False},
            ],
        }
        response = admin_client.post("/questions/", payload, format="json")
        assert response.status_code == 201
        assert response.data["text"] == "Who will become the king of the pirates?"
        assert response.data["difficult_level"] == "hard"
        assert len(response.data["answers"]) == 2

    def test_create_question_as_player_is_forbidden(self, player_client):
        payload = {"text": "Some question"}
        response = player_client.post("/questions/", payload, format="json")
        assert response.status_code == 403

    def test_create_question_unauthenticated_is_forbidden(self, client):
        response = client.post("/questions/", {"text": "Some question"}, format="json")
        assert response.status_code == 401

    def test_create_question_invalid_data(self, admin_client):
        response = admin_client.post("/questions/", {}, format="json")
        assert response.status_code == 400

    def test_list_questions_as_admin(self, admin_client):
        QuestionService.create_question(text="Question 1")
        QuestionService.create_question(text="Question 2")
        response = admin_client.get("/questions/")
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_list_questions_as_player_is_forbidden(self, player_client):
        response = player_client.get("/questions/")
        assert response.status_code == 403

    def test_list_questions_unauthenticated_is_forbidden(self, client):
        response = client.get("/questions/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestQuestionDetailUpdateDeleteView:
    def test_get_question_as_admin(self, admin_client):
        question = QuestionService.create_question(
            text="Who will become king of the pirates?"
        )
        response = admin_client.get(f"/questions/{question.id}/")
        assert response.status_code == 200
        assert response.data["text"] == "Who will become king of the pirates?"

    def test_get_question_as_player_is_forbidden(self, player_client):
        question = QuestionService.create_question(text="Some question")
        response = player_client.get(f"/questions/{question.id}/")
        assert response.status_code == 403

    def test_get_question_not_found(self, admin_client):
        response = admin_client.get("/questions/999/")
        assert response.status_code == 404

    def test_delete_question_as_admin(self, admin_client):
        question = QuestionService.create_question(text="Some question")
        response = admin_client.delete(f"/questions/{question.id}/")
        assert response.status_code == 204
        assert not Question.objects.filter(id=question.id).exists()

    def test_delete_question_as_player_is_forbidden(self, player_client):
        question = QuestionService.create_question(text="Some question")
        response = player_client.delete(f"/questions/{question.id}/")
        assert response.status_code == 403

    def test_delete_question_not_found(self, admin_client):
        response = admin_client.delete("/questions/999/")
        assert response.status_code == 404

    def test_update_question_text_as_admin(self, admin_client):
        question = QuestionService.create_question(text="Original text")
        response = admin_client.put(
            f"/questions/{question.id}/", {"text": "Updated text"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["text"] == "Updated text"

    def test_update_question_difficult_level_as_admin(self, admin_client):
        question = QuestionService.create_question(text="Some question")
        response = admin_client.put(
            f"/questions/{question.id}/", {"difficult_level": "hard"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["difficult_level"] == "hard"

    def test_update_question_as_player_is_forbidden(self, player_client):
        question = QuestionService.create_question(text="Some question")
        response = player_client.put(
            f"/questions/{question.id}/", {"text": "Hacked"}, format="json"
        )
        assert response.status_code == 403

    def test_update_question_not_found(self, admin_client):
        response = admin_client.put(
            "/questions/999/", {"text": "Updated text"}, format="json"
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestAnswerCreateView:
    def test_create_answer_as_admin(self, admin_client):
        question = QuestionService.create_question(
            text="Who is the King of the Pirates?"
        )
        response = admin_client.post(
            f"/questions/{question.id}/answers/",
            {"text": "Monkey D. Luffy", "is_correct": True},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["text"] == "Monkey D. Luffy"
        assert response.data["is_correct"] is True

    def test_create_answer_duplicate_correct_returns_400(self, admin_client):
        question = QuestionService.create_question(
            text="Who is the King of the Pirates?",
            answers=[{"text": "Monkey D. Luffy", "is_correct": True}],
        )
        response = admin_client.post(
            f"/questions/{question.id}/answers/",
            {"text": "Roronoa Zoro", "is_correct": True},
            format="json",
        )
        assert response.status_code == 400

    def test_create_answer_question_not_found(self, admin_client):
        response = admin_client.post(
            "/questions/999/answers/", {"text": "Monkey D. Luffy"}, format="json"
        )
        assert response.status_code == 404

    def test_create_answer_as_player_is_forbidden(self, player_client):
        question = QuestionService.create_question(
            text="Who is the King of the Pirates?"
        )
        response = player_client.post(
            f"/questions/{question.id}/answers/", {"text": "Luffy"}, format="json"
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestAnswerDeleteView:
    def test_delete_answer_as_admin(self, admin_client):
        question = QuestionService.create_question(
            text="Some question",
            answers=[
                {"text": "Option A", "is_correct": True},
                {"text": "Option B", "is_correct": False},
            ],
        )
        answer = question.answers.first()
        response = admin_client.delete(f"/questions/{question.id}/answers/{answer.id}/")
        assert response.status_code == 204
        assert question.answers.count() == 1

    def test_delete_answer_as_player_is_forbidden(self, player_client):
        question = QuestionService.create_question(
            text="Some question", answers=[{"text": "Option A", "is_correct": True}]
        )
        answer = question.answers.first()
        response = player_client.delete(
            f"/questions/{question.id}/answers/{answer.id}/"
        )
        assert response.status_code == 403

    def test_delete_answer_question_not_found(self, admin_client):
        response = admin_client.delete("/questions/999/answers/1/")
        assert response.status_code == 404

    def test_delete_answer_not_found(self, admin_client):
        question = QuestionService.create_question(text="Some question")
        response = admin_client.delete(f"/questions/{question.id}/answers/999/")
        assert response.status_code == 404

    def test_update_answer_text_as_admin(self, admin_client):
        question = QuestionService.create_question(
            text="Some question", answers=[{"text": "Option A", "is_correct": True}]
        )
        answer = question.answers.first()
        response = admin_client.put(
            f"/questions/{question.id}/answers/{answer.id}/",
            {"text": "Updated A"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["text"] == "Updated A"

    def test_update_answer_is_correct_is_not_allowed(self, admin_client):
        question = QuestionService.create_question(
            text="Some question", answers=[{"text": "Option A", "is_correct": False}]
        )
        answer = question.answers.first()
        response = admin_client.put(
            f"/questions/{question.id}/answers/{answer.id}/",
            {"is_correct": True},
            format="json",
        )
        assert response.status_code == 400

    def test_update_answer_as_player_is_forbidden(self, player_client):
        question = QuestionService.create_question(
            text="Some question", answers=[{"text": "Option A", "is_correct": True}]
        )
        answer = question.answers.first()
        response = player_client.put(
            f"/questions/{question.id}/answers/{answer.id}/",
            {"text": "Hacked"},
            format="json",
        )
        assert response.status_code == 403

    def test_update_answer_not_found(self, admin_client):
        question = QuestionService.create_question(text="Some question")
        response = admin_client.put(
            f"/questions/{question.id}/answers/999/", {"text": "Updated"}, format="json"
        )
        assert response.status_code == 404
