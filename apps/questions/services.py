from typing import List, Optional

from django.db import transaction

from apps.questions.exceptions import AnswerNotFound, QuestionNotFound
from apps.questions.models import Answer, Question


class QuestionService:
    @staticmethod
    def _question_exists(id: int) -> bool:
        """
        Check if a question exists in the database without fetching the full object.
        Args:
            id: int: The id of the question
        Returns:
            bool: True if the question exists, False otherwise
        """
        return Question.objects.filter(id=id).exists()

    @staticmethod
    def create_question(
        text: str,
        difficult_level: Optional[str] = None,
        answers: Optional[List[dict]] = None,
    ) -> Question:
        """
        Create a new question with optional answers. Only one answer can be correct.
        Args:
            text: str: The text of the question
            difficult_level: Optional[str]: The difficulty level (easy, medium, hard). Defaults to easy
            answers: Optional[List[dict]]: List of answers with text and is_correct fields
        Returns:
            Question: The created question
        Raises:
            ValueError: If more than one answer is marked as correct
        """
        if answers:
            correct_count = sum(1 for a in answers if a.get("is_correct"))
            if correct_count > 1:
                raise ValueError("A question can only have one correct answer")
        with transaction.atomic():
            difficult_level = (
                difficult_level if difficult_level else Question.Difficulty.EASY
            )
            question = Question.objects.create(
                text=text, difficult_level=difficult_level
            )
            if answers:
                for answer in answers:
                    Answer.objects.create(question=question, **answer)
            return question

    @staticmethod
    def delete_question(id: int) -> None:
        """
        Delete a question and all its associated answers.
        Args:
            id: int: The id of the question to delete
        Raises:
            QuestionNotFound: If no question exists with the given id
        """
        try:
            Question.objects.get(id=id).delete()
        except Question.DoesNotExist:
            raise QuestionNotFound(f"Question with id {id} not found")

    @staticmethod
    def get_all_questions() -> List[Question]:
        """
        Retrieve all questions with their answers prefetched.
        Returns:
            List[Question]: All questions in the database
        """
        return Question.objects.all().prefetch_related("answers")

    @staticmethod
    def get_question_by_id(id: int) -> Question:
        """
        Retrieve a single question by its id.
        Args:
            id: int: The id of the question
        Returns:
            Question: The question with the given id
        Raises:
            QuestionNotFound: If no question exists with the given id
        """
        try:
            return Question.objects.get(id=id)
        except Question.DoesNotExist:
            raise QuestionNotFound(f"Question with id {id} not found")

    @staticmethod
    def update_question(
        id: int,
        text: Optional[str] = None,
        difficult_level: Optional[str] = None,
        **kwargs,
    ) -> Question:
        """
        Partially update a question's text or difficulty level.
        Args:
            id: int: The id of the question to update
            text: Optional[str]: The new text of the question
            difficult_level: Optional[str]: The new difficulty level
        Returns:
            Question: The updated question
        Raises:
            ValueError: If no fields are provided
            QuestionNotFound: If no question exists with the given id
        """
        if not text and not difficult_level:
            raise ValueError(
                "At least one field must be provided to update the question"
            )
        question = QuestionService.get_question_by_id(id)
        if text:
            question.text = text
        if difficult_level:
            question.difficult_level = difficult_level
        question.save()
        return question


class AnswerService:
    @staticmethod
    def create_answer(question_id: int, text: str, is_correct: bool = False) -> Answer:
        """
        Create a new answer for a question. Only one correct answer is allowed per question.
        Args:
            question_id: int: The id of the question
            text: str: The text of the answer
            is_correct: bool: Whether this answer is correct. Defaults to False
        Returns:
            Answer: The created answer
        Raises:
            QuestionNotFound: If no question exists with the given id
            ValueError: If the question already has a correct answer and is_correct is True
        """
        if not QuestionService._question_exists(question_id):
            raise QuestionNotFound(f"Question with id {question_id} not found")
        if (
            is_correct
            and Answer.objects.filter(question_id=question_id, is_correct=True).exists()
        ):
            raise ValueError("This question already has a correct answer")
        return Answer.objects.create(
            question_id=question_id, text=text, is_correct=is_correct
        )

    @staticmethod
    def delete_answer(question_id: int, answer_id: int) -> None:
        """
        Delete an answer from a question.
        Args:
            question_id: int: The id of the question
            answer_id: int: The id of the answer to delete
        Raises:
            QuestionNotFound: If no question exists with the given id
            AnswerNotFound: If no answer exists with the given id for that question
        """
        if not QuestionService._question_exists(question_id):
            raise QuestionNotFound(f"Question with id {question_id} not found")
        try:
            Answer.objects.get(id=answer_id, question_id=question_id).delete()
        except Answer.DoesNotExist:
            raise AnswerNotFound(
                f"Answer with id {answer_id} not found for question {question_id}"
            )

    @staticmethod
    def get_answer(question_id: int, answer_id: int) -> Answer:
        """
        Retrieve a single answer belonging to a specific question.
        Args:
            question_id: int: The id of the question
            answer_id: int: The id of the answer
        Returns:
            Answer: The answer with the given id
        Raises:
            QuestionNotFound: If no question exists with the given id
            AnswerNotFound: If no answer exists with the given id for that question
        """
        if not QuestionService._question_exists(question_id):
            raise QuestionNotFound(f"Question with id {question_id} not found")
        try:
            return Answer.objects.get(id=answer_id, question_id=question_id)
        except Answer.DoesNotExist:
            raise AnswerNotFound(
                f"Answer with id {answer_id} not found for question {question_id}"
            )

    @staticmethod
    def update_answer(
        question_id: int,
        answer_id: int,
        text: Optional[str] = None,
        is_correct: Optional[bool] = None,
    ) -> Answer:
        """
        Partially update an answer's text or correctness.
        Args:
            question_id: int: The id of the question
            answer_id: int: The id of the answer to update
            text: Optional[str]: The new text of the answer
            is_correct: Optional[bool]: Whether this answer is correct
        Returns:
            Answer: The updated answer
        Raises:
            ValueError: If no fields are provided
            QuestionNotFound: If no question exists with the given id
            AnswerNotFound: If no answer exists with the given id for that question
        """
        if text is None and is_correct is None:
            raise ValueError("At least one field must be provided to update the answer")
        answer = AnswerService.get_answer(question_id, answer_id)
        if text is not None:
            answer.text = text
        if is_correct is not None:
            answer.is_correct = is_correct
        answer.save()
        return answer
