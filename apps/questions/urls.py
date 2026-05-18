from django.urls import path

from apps.questions.views import (
    AnswerCreateView,
    AnswerDetailView,
    QuestionCreateListView,
    QuestionDetailDeleteUpdateView,
)

urlpatterns = [
    path("questions/", QuestionCreateListView.as_view(), name="question-list-create"),
    path(
        "questions/<int:id>/",
        QuestionDetailDeleteUpdateView.as_view(),
        name="question-detail-delete",
    ),
    path(
        "questions/<int:question_id>/answers/",
        AnswerCreateView.as_view(),
        name="answer-create",
    ),
    path(
        "questions/<int:question_id>/answers/<int:answer_id>/",
        AnswerDetailView.as_view(),
        name="answer-detail",
    ),
]
