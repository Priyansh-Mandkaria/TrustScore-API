import operator as op

from .models import RiskRule


class RiskScoringEngine:
    """
    Evaluates user activity data against all active risk rules
    and produces a trust score, risk level, and list of triggered flags.

    Fully decoupled from views — can be unit-tested independently.
    """

    # Map operator strings to Python comparison functions
    OPERATOR_MAP = {
        "lt": op.lt,
        "gt": op.gt,
        "eq": op.eq,
    }

    @classmethod
    def evaluate(cls, input_data: dict, rules=None) -> dict:
        """
        Evaluate the input data against active risk rules.

        Args:
            input_data: Dictionary of user activity fields.
            rules: Optional queryset/list of RiskRule objects.
                   If None, fetches all active rules from the database.

        Returns:
            dict with keys: trust_score, risk_level, flags
        """
        if rules is None:
            rules = RiskRule.objects.filter(is_active=True)

        score = 100
        flags = []

        for rule in rules:
            field_value = input_data.get(rule.condition_field)

            # Skip if the field is not present in the input
            if field_value is None:
                continue

            comparator = cls.OPERATOR_MAP.get(rule.operator)
            if comparator is None:
                continue  # Unknown operator — skip gracefully

            try:
                if comparator(float(field_value), rule.threshold):
                    score -= rule.deduction
                    flags.append(rule.description)
            except (TypeError, ValueError):
                continue  # Non-numeric value — skip gracefully

        # Clamp score to [0, 100]
        score = max(0, min(100, score))

        return {
            "trust_score": score,
            "risk_level": cls._classify(score),
            "flags": flags,
        }

    @staticmethod
    def _classify(score: int) -> str:
        """Classify trust score into a risk level."""
        if score >= 80:
            return "LOW"
        elif score >= 50:
            return "MEDIUM"
        else:
            return "HIGH"
