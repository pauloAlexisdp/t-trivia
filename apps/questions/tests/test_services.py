import pytest

from apps.questions.exceptions import AnswerNotFound, QuestionNotFound
from apps.questions.models import Question
from apps.questions.services import AnswerService, QuestionService


@pytest.mark.django_db
class TestCreateQuestion:
    def test_create_question_with_all_fields(self):
        answers = [
            {"text": "Monkey D. Luffy", "is_correct": True},
            {"text": "Roronoa Zoro", "is_correct": False},
            {"text": "Vinsmoke Sanji", "is_correct": False},
            {"text": "Nami", "is_correct": False},
        ]
        question = QuestionService.create_question(
            text="Who will become the King of the Pirates?",
            difficult_level="hard",
            answers=answers,
        )
        assert question.id is not None
        assert question.text == "Who will become the King of the Pirates?"
        assert question.difficult_level == "hard"
        assert question.answers.count() == 4
        assert question.answers.filter(is_correct=True).count() == 1
        assert question.answers.first().text == "Monkey D. Luffy"

    def test_create_question_with_default_difficult_level(self):
        answers = [
            {"text": "Monkey D. Luffy", "is_correct": True},
            {"text": "Roronoa Zoro", "is_correct": False},
        ]
        question = QuestionService.create_question(
            text="Who ate the Gomu Gomu no Mi?", answers=answers
        )
        assert question.difficult_level == Question.Difficulty.EASY


@pytest.mark.django_db
class TestGetAllQuestions:
    def test_get_all_questions(self):
        QuestionService.create_question(
            text="Who is the cook of the Straw Hat crew?",
            answers=[
                {"text": "Sanji", "is_correct": True},
                {"text": "Zoro", "is_correct": False},
            ],
        )
        assert QuestionService.get_all_questions().count() == 1

    def test_get_all_questions_empty(self):
        assert QuestionService.get_all_questions().count() == 0


@pytest.mark.django_db
class TestGetQuestionById:
    def test_get_question_by_id(self):
        question = QuestionService.create_question(
            text="What is the name of Luffy's ship?",
            answers=[
                {"text": "Thousand Sunny", "is_correct": True},
                {"text": "Going Merry", "is_correct": False},
            ],
        )
        assert QuestionService.get_question_by_id(question.id) == question

    def test_get_question_by_id_not_found(self):
        with pytest.raises(QuestionNotFound):
            QuestionService.get_question_by_id(999)


@pytest.mark.django_db
class TestCreateQuestionValidation:
    def test_create_question_with_multiple_correct_answers_raises_error(self):
        answers = [
            {"text": "Monkey D. Luffy", "is_correct": True},
            {"text": "Roronoa Zoro", "is_correct": True},
        ]
        with pytest.raises(ValueError):
            QuestionService.create_question(
                text="Who is the King of the Pirates?", answers=answers
            )


@pytest.mark.django_db
class TestUpdateQuestion:
    def test_update_question_text(self):
        question = QuestionService.create_question(
            text="Who is the navigator of the Straw Hats?"
        )
        QuestionService.update_question(
            question.id, text="Who is the swordsman of the Straw Hats?"
        )
        question.refresh_from_db()
        assert question.text == "Who is the swordsman of the Straw Hats?"

    def test_update_question_difficult_level(self):
        question = QuestionService.create_question(text="What is Luffy's dream?")
        QuestionService.update_question(
            question.id, difficult_level=Question.Difficulty.HARD
        )
        question.refresh_from_db()
        assert question.difficult_level == Question.Difficulty.HARD

    def test_update_question_no_fields_raises_error(self):
        question = QuestionService.create_question(text="What is the One Piece?")
        with pytest.raises(ValueError):
            QuestionService.update_question(question.id)

    def test_update_question_not_found(self):
        with pytest.raises(QuestionNotFound):
            QuestionService.update_question(999, text="Who is Shanks?")


@pytest.mark.django_db
class TestCreateAnswer:
    def test_create_answer(self):
        question = QuestionService.create_question(
            text="Who is the King of the Pirates?"
        )
        answer = AnswerService.create_answer(
            question.id, text="Monkey D. Luffy", is_correct=True
        )
        assert answer.id is not None
        assert answer.text == "Monkey D. Luffy"
        assert answer.is_correct is True
        assert question.answers.count() == 1

    def test_create_answer_duplicate_correct_raises_error(self):
        question = QuestionService.create_question(
            text="Who is the King of the Pirates?",
            answers=[{"text": "Monkey D. Luffy", "is_correct": True}],
        )
        with pytest.raises(ValueError):
            AnswerService.create_answer(
                question.id, text="Roronoa Zoro", is_correct=True
            )

    def test_create_answer_question_not_found(self):
        with pytest.raises(QuestionNotFound):
            AnswerService.create_answer(999, text="Monkey D. Luffy")


@pytest.mark.django_db
class TestUpdateAnswer:
    def test_update_answer_text(self):
        question = QuestionService.create_question(
            text="Who is the doctor of the Straw Hats?",
            answers=[{"text": "Robin", "is_correct": False}],
        )
        answer = question.answers.first()
        updated = AnswerService.update_answer(question.id, answer.id, text="Chopper")
        assert updated.text == "Chopper"

    def test_update_answer_is_correct(self):
        question = QuestionService.create_question(
            text="Who is the doctor of the Straw Hats?",
            answers=[{"text": "Chopper", "is_correct": False}],
        )
        answer = question.answers.first()
        updated = AnswerService.update_answer(question.id, answer.id, is_correct=True)
        assert updated.is_correct is True

    def test_update_answer_no_fields_raises_error(self):
        question = QuestionService.create_question(
            text="Who is the archaeologist of the Straw Hats?",
            answers=[{"text": "Robin", "is_correct": True}],
        )
        answer = question.answers.first()
        with pytest.raises(ValueError):
            AnswerService.update_answer(question.id, answer.id)

    def test_update_answer_question_not_found(self):
        with pytest.raises(QuestionNotFound):
            AnswerService.update_answer(999, 1, text="Nami")

    def test_update_answer_not_found(self):
        question = QuestionService.create_question(
            text="Who is the musician of the Straw Hats?"
        )
        with pytest.raises(AnswerNotFound):
            AnswerService.update_answer(question.id, 999, text="Brook")


@pytest.mark.django_db
class TestDeleteAnswer:
    def test_delete_answer(self):
        question = QuestionService.create_question(
            text="Who is the sniper of the Straw Hats?",
            answers=[
                {"text": "Usopp", "is_correct": True},
                {"text": "Nami", "is_correct": False},
            ],
        )
        answer = question.answers.first()
        AnswerService.delete_answer(question.id, answer.id)
        assert question.answers.count() == 1

    def test_delete_answer_question_not_found(self):
        with pytest.raises(QuestionNotFound):
            AnswerService.delete_answer(999, 1)

    def test_delete_answer_not_found(self):
        question = QuestionService.create_question(text="Who trained Luffy in Haki?")
        with pytest.raises(AnswerNotFound):
            AnswerService.delete_answer(question.id, 999)


@pytest.mark.django_db
class TestDeleteQuestion:
    def test_delete_question(self):
        question = QuestionService.create_question(
            text="What is the name of the final island?"
        )
        QuestionService.delete_question(question.id)
        assert not Question.objects.filter(id=question.id).exists()

    def test_delete_question_not_found(self):
        with pytest.raises(QuestionNotFound):
            QuestionService.delete_question(999)
