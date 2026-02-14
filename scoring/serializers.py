from rest_framework import serializers

from .models import EvaluationRecord


class EvaluateUserSerializer(serializers.Serializer):
    """Validates incoming POST data for user evaluation."""

    user_id = serializers.CharField(
        max_length=100,
        help_text="Unique user identifier.",
    )
    account_age_days = serializers.IntegerField(
        min_value=0,
        help_text="Number of days since account creation.",
    )
    failed_logins = serializers.IntegerField(
        min_value=0,
        help_text="Count of failed login attempts.",
    )
    transactions_last_24h = serializers.IntegerField(
        min_value=0,
        help_text="Number of transactions in the last 24 hours.",
    )
    ip_changes = serializers.IntegerField(
        min_value=0,
        help_text="Number of IP address changes.",
    )
    avg_transaction_amount = serializers.FloatField(
        min_value=0,
        help_text="Average transaction amount.",
    )


class EvaluationResultSerializer(serializers.Serializer):
    """Read-only serializer for the evaluation response."""

    trust_score = serializers.IntegerField()
    risk_level = serializers.CharField()
    flags = serializers.ListField(child=serializers.CharField())


class EvaluationHistorySerializer(serializers.ModelSerializer):
    """Serializer for evaluation history records."""

    class Meta:
        model = EvaluationRecord
        fields = [
            "id",
            "user_id",
            "trust_score",
            "risk_level",
            "flags",
            "input_data",
            "evaluated_at",
        ]
        read_only_fields = fields
