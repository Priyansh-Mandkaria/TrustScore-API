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
from .throttles import EvaluateRateThrottle


class EvaluateUserView(APIView):
    """
    POST /api/evaluate-user/

    Accepts user activity data, evaluates it against active risk rules,
    stores the result, and returns the trust score breakdown.

    Rate-limited to 60 requests/minute per IP (configurable via settings).
    """

    throttle_classes = [EvaluateRateThrottle]

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


from celery.result import AsyncResult
from .tasks import evaluate_user_async

class EvaluateUserAsyncView(APIView):
    """
    POST /api/evaluate-user-async/

    Accepts user activity data, queues it for background scoring,
    and returns a task ID to check status later.
    """

    throttle_classes = [EvaluateRateThrottle]

    def post(self, request):
        serializer = EvaluateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        task = evaluate_user_async.delay(validated)

        return Response({"task_id": task.id, "status": "QUEUED"}, status=status.HTTP_202_ACCEPTED)


class EvaluationStatusView(APIView):
    """
    GET /api/evaluation-status/<task_id>/

    Check the status and result of a queued background evaluation.
    """

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        
        response_data = {
            "task_id": task_id,
            "status": result.status
        }
        
        if result.ready():
            if result.successful():
                response_data["result"] = result.result
            else:
                response_data["error"] = str(result.result)
                
        return Response(response_data, status=status.HTTP_200_OK)
