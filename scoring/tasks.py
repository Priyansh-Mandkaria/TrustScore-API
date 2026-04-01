import logging
from celery import shared_task
from .services import RiskScoringEngine
from .models import EvaluationRecord

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def evaluate_user_async(self, validated_data):
    """
    Asynchronous task for scoring users.
    Returns the evaluation properties.
    """
    logger.info(f"Starting async evaluation for user {validated_data.get('user_id')}")
    
    # Run the scoring engine
    result = RiskScoringEngine.evaluate(validated_data)

    # Persist the evaluation record
    EvaluationRecord.objects.create(
        user_id=validated_data["user_id"],
        trust_score=result["trust_score"],
        risk_level=result["risk_level"],
        flags=result["flags"],
        input_data=validated_data,
    )

    return result
