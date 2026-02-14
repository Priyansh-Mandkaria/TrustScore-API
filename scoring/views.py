from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EvaluationRecord
from .serializers import (
    EvaluateUserSerializer,
    EvaluationHistorySerializer,
    EvaluationResultSerializer,
)
from .services import RiskScoringEngine


class EvaluateUserView(APIView):
    """
    POST /api/evaluate-user/

    Accepts user activity data, evaluates it against active risk rules,
    stores the result, and returns the trust score breakdown.
    """

    def post(self, request):
        serializer = EvaluateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data

        # Run the scoring engine
        result = RiskScoringEngine.evaluate(validated)

        # Persist the evaluation record
        EvaluationRecord.objects.create(
            user_id=validated["user_id"],
            trust_score=result["trust_score"],
            risk_level=result["risk_level"],
            flags=result["flags"],
            input_data=validated,
        )

        output = EvaluationResultSerializer(result)
        return Response(output.data, status=status.HTTP_200_OK)


class UserHistoryView(APIView):
    """
    GET /api/user-history/<user_id>/

    Returns the evaluation history for a specific user,
    ordered by most recent first.
    """

    def get(self, request, user_id):
        records = EvaluationRecord.objects.filter(user_id=user_id)
        serializer = EvaluationHistorySerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
