from typing import List, Optional

from django.db import transaction

from apps.questions.models import Answer, Question
from apps.trivias.exceptions import ParticipantNotFound, TriviaNotFound
from apps.trivias.models import Trivia, TriviaAnswer, TriviaParticipant

DIFFICULTY_POINTS = {
    Question.Difficulty.EASY: 1,
    Question.Difficulty.MEDIUM: 2,
    Question.Difficulty.HARD: 3,
}


class TriviaService:
    @staticmethod
    def _trivia_exists(id: int) -> bool:
        """
        Check if a trivia exists in the database without fetching the full object.
        Args:
            id: int: The id of the trivia
        Returns:
            bool: True if the trivia exists, False otherwise
        """
        return Trivia.objects.filter(id=id).exists()

    @staticmethod
    def create_trivia(
        name: str,
        description: str,
        created_by_id: int,
        question_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
    ) -> Trivia:
        """
        Create a new trivia and optionally assign questions and participants.
        Args:
            name: str: The name of the trivia
            description: str: The description of the trivia
            created_by_id: int: The id of the admin user creating the trivia
            question_ids: Optional[List[int]]: List of question ids to assign
            user_ids: Optional[List[int]]: List of player ids to assign as participants
        Returns:
            Trivia: The created trivia
        """
        with transaction.atomic():
            trivia = Trivia.objects.create(
                name=name,
                description=description,
                created_by_id=created_by_id,
            )
            if question_ids:
                questions = Question.objects.filter(id__in=question_ids)
                trivia.questions.set(questions)
            if user_ids:
                for user_id in user_ids:
                    TriviaParticipant.objects.get_or_create(
                        trivia=trivia, user_id=user_id
                    )
            return trivia

    @staticmethod
    def get_all_trivias() -> List[Trivia]:
        """
        Retrieve all trivias with their creator. Does not include questions or participants.
        Returns:
            List[Trivia]: All trivias in the database
        """
        return Trivia.objects.all().select_related("created_by")

    @staticmethod
    def get_trivia_by_id(id: int) -> Trivia:
        """
        Retrieve a single trivia with full detail: creator, questions with answers, and participants.
        Args:
            id: int: The id of the trivia
        Returns:
            Trivia: The trivia with the given id
        Raises:
            TriviaNotFound: If no trivia exists with the given id
        """
        try:
            return (
                Trivia.objects.select_related("created_by")
                .prefetch_related("questions__answers", "triviaparticipant_set__user")
                .get(id=id)
            )
        except Trivia.DoesNotExist:
            raise TriviaNotFound(f"Trivia with id {id} not found")

    @staticmethod
    def update_trivia(
        id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        question_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
    ) -> Trivia:
        """
        Partially update a trivia. question_ids replaces the full set of questions.
        user_ids adds new participants without removing existing ones.
        Args:
            id: int: The id of the trivia to update
            name: Optional[str]: The new name of the trivia
            description: Optional[str]: The new description of the trivia
            question_ids: Optional[List[int]]: Replaces all assigned questions
            user_ids: Optional[List[int]]: Adds new participants
        Returns:
            Trivia: The updated trivia with full detail
        Raises:
            TriviaNotFound: If no trivia exists with the given id
        """
        if not TriviaService._trivia_exists(id):
            raise TriviaNotFound(f"Trivia with id {id} not found")
        trivia = Trivia.objects.get(id=id)
        if name:
            trivia.name = name
        if description:
            trivia.description = description
        trivia.save()
        if question_ids is not None:
            trivia.questions.set(Question.objects.filter(id__in=question_ids))
        if user_ids is not None:
            for user_id in user_ids:
                TriviaParticipant.objects.get_or_create(trivia=trivia, user_id=user_id)
        return TriviaService.get_trivia_by_id(id)

    @staticmethod
    def delete_trivia(id: int) -> None:
        """
        Delete a trivia and all its associated participants and answers.
        Args:
            id: int: The id of the trivia to delete
        Raises:
            TriviaNotFound: If no trivia exists with the given id
        """
        if not TriviaService._trivia_exists(id):
            raise TriviaNotFound(f"Trivia with id {id} not found")
        Trivia.objects.filter(id=id).delete()

    @staticmethod
    def get_trivias_for_user(user_id: int) -> List[Trivia]:
        """
        Retrieve all trivias assigned to a specific player. Does not include questions or participants.
        Args:
            user_id: int: The id of the player
        Returns:
            List[Trivia]: Trivias assigned to the player
        """
        return Trivia.objects.filter(triviaparticipant__user_id=user_id)

    @staticmethod
    def get_ranking(trivia_id: int) -> List[TriviaParticipant]:
        """
        Retrieve the ranking of participants for a trivia, ordered by score descending.
        Args:
            trivia_id: int: The id of the trivia
        Returns:
            List[TriviaParticipant]: Participants ordered by score descending
        Raises:
            TriviaNotFound: If no trivia exists with the given id
        """
        if not TriviaService._trivia_exists(trivia_id):
            raise TriviaNotFound(f"Trivia with id {trivia_id} not found")
        return (
            TriviaParticipant.objects.filter(trivia_id=trivia_id)
            .select_related("user")
            .order_by("-score")
        )


class ParticipationService:
    @staticmethod
    def get_participant(trivia_id: int, user_id: int) -> TriviaParticipant:
        """
        Retrieve a participant record for a specific user and trivia.
        Args:
            trivia_id: int: The id of the trivia
            user_id: int: The id of the player
        Returns:
            TriviaParticipant: The participant record
        Raises:
            ParticipantNotFound: If the user is not assigned to the trivia
        """
        try:
            return TriviaParticipant.objects.get(trivia_id=trivia_id, user_id=user_id)
        except TriviaParticipant.DoesNotExist:
            raise ParticipantNotFound(
                f"User {user_id} is not a participant in trivia {trivia_id}"
            )

    @staticmethod
    def submit_answers(
        trivia_id: int,
        user_id: int,
        answers: List[dict],
    ) -> TriviaParticipant:
        """
        Submit answers for a trivia, calculate the score and mark it as completed.
        Score is calculated based on difficulty: easy=1pt, medium=2pts, hard=3pts.
        Args:
            trivia_id: int: The id of the trivia
            user_id: int: The id of the player submitting answers
            answers: List[dict]: List of dicts with question_id and answer_id
        Returns:
            TriviaParticipant: The updated participant with final score and completed=True
        Raises:
            ParticipantNotFound: If the user is not assigned to the trivia
            ValueError: If the trivia is already completed
            ValueError: If a question does not belong to the trivia
            ValueError: If an answer does not belong to the question
        """
        participant = ParticipationService.get_participant(trivia_id, user_id)
        if participant.completed:
            raise ValueError("This trivia has already been completed")

        trivia = TriviaService.get_trivia_by_id(trivia_id)
        trivia_question_ids = set(trivia.questions.values_list("id", flat=True))

        with transaction.atomic():
            score = 0
            for answer_data in answers:
                question_id = answer_data["question_id"]
                answer_id = answer_data["answer_id"]

                if question_id not in trivia_question_ids:
                    raise ValueError(
                        f"Question {question_id} does not belong to this trivia"
                    )

                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    raise ValueError(f"Question {question_id} not found")

                try:
                    selected_option = Answer.objects.get(
                        id=answer_id, question_id=question_id
                    )
                except Answer.DoesNotExist:
                    raise ValueError(
                        f"Answer {answer_id} does not belong to question {question_id}"
                    )

                TriviaAnswer.objects.update_or_create(
                    participant=participant,
                    question=question,
                    defaults={"selected_option": selected_option},
                )

                if selected_option.is_correct:
                    score += DIFFICULTY_POINTS.get(question.difficult_level, 1)

            participant.score = score
            participant.completed = True
            participant.save()
            return participant
