from django.urls import path

from .views import EvaluateUserView, UserHistoryView

urlpatterns = [
    path("evaluate-user/", EvaluateUserView.as_view(), name="evaluate-user"),
    path("user-history/<str:user_id>/", UserHistoryView.as_view(), name="user-history"),
]
