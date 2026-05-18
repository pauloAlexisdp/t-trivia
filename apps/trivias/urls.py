from django.urls import path

from apps.trivias.views import (
    MyTriviasView,
    SubmitAnswersView,
    TriviaDetailView,
    TriviaListCreateView,
    TriviaPlayView,
    TriviaRankingView,
)

urlpatterns = [
    path("trivias/", TriviaListCreateView.as_view(), name="trivia-list-create"),
    path("trivias/my/", MyTriviasView.as_view(), name="my-trivias"),
    path("trivias/<int:id>/", TriviaDetailView.as_view(), name="trivia-detail"),
    path(
        "trivias/<int:id>/ranking/", TriviaRankingView.as_view(), name="trivia-ranking"
    ),
    path("trivias/<int:id>/play/", TriviaPlayView.as_view(), name="trivia-play"),
    path(
        "trivias/<int:id>/answers/",
        SubmitAnswersView.as_view(),
        name="trivia-submit-answers",
    ),
]
