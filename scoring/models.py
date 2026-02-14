from django.db import models


class RiskRule(models.Model):
    """
    Dynamic risk rule stored in the database.
    Each rule checks a specific input field against a threshold
    and applies a point deduction if the condition is met.
    """

    OPERATOR_CHOICES = [
        ("lt", "Less Than"),
        ("gt", "Greater Than"),
        ("eq", "Equal To"),
    ]

    condition_field = models.CharField(
        max_length=100,
        help_text="Input field name to evaluate (e.g. 'account_age_days').",
    )
    operator = models.CharField(
        max_length=2,
        choices=OPERATOR_CHOICES,
        help_text="Comparison operator: lt, gt, or eq.",
    )
    threshold = models.FloatField(
        help_text="Threshold value for the comparison.",
    )
    deduction = models.IntegerField(
        help_text="Points to deduct when the rule triggers (positive number).",
    )
    description = models.CharField(
        max_length=255,
        help_text="Human-readable flag text (e.g. 'New account').",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active rules are evaluated.",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.description} ({self.condition_field} {self.operator} {self.threshold} → -{self.deduction})"


class EvaluationRecord(models.Model):
    """
    Stores the result of each user evaluation for audit/history purposes.
    """

    RISK_LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    user_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="The evaluated user's identifier.",
    )
    trust_score = models.IntegerField(
        help_text="Calculated trust score (0–100).",
    )
    risk_level = models.CharField(
        max_length=6,
        choices=RISK_LEVEL_CHOICES,
    )
    flags = models.JSONField(
        default=list,
        help_text="List of triggered rule descriptions.",
    )
    input_data = models.JSONField(
        help_text="Original request payload for auditability.",
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-evaluated_at"]

    def __str__(self):
        return f"Eval({self.user_id}) → {self.trust_score} ({self.risk_level})"
