from django.urls import path

from .views import (
    EvaluateUserView, 
    UserHistoryView, 
    EvaluateUserAsyncView, 
    EvaluationStatusView
)

urlpatterns = [
    path("evaluate-user/", EvaluateUserView.as_view(), name="evaluate-user"),
    path("user-history/<str:user_id>/", UserHistoryView.as_view(), name="user-history"),
    path("evaluate-user-async/", EvaluateUserAsyncView.as_view(), name="evaluate-user-async"),
    path("evaluation-status/<str:task_id>/", EvaluationStatusView.as_view(), name="evaluation-status"),
]
