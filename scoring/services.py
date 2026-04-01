import operator as op

from django.core.cache import cache

from .models import RiskRule

# Cache key and TTL for active risk rules
RULES_CACHE_KEY = 'scoring:active_rules'
RULES_CACHE_TTL = 300  # 5 minutes


class RiskScoringEngine:
    """
    Evaluates user activity data against all active risk rules
    and produces a trust score, risk level, and list of triggered flags.

    Active rules are cached in Redis for 5 minutes to avoid
    repeated database queries on every evaluation request.
    """

    # Map operator strings to Python comparison functions
    OPERATOR_MAP = {
        "lt": op.lt,
        "gt": op.gt,
        "eq": op.eq,
    }

    @classmethod
    def _get_active_rules(cls):
        """
        Fetch active rules from cache, falling back to DB on cache miss.
        Returns a list of dicts (not ORM objects) so they're serialisable.
        """
        cached = cache.get(RULES_CACHE_KEY)
        if cached is not None:
            return cached

        rules = list(
            RiskRule.objects.filter(is_active=True).values(
                'condition_field', 'operator', 'threshold',
                'deduction', 'description',
            )
        )
        cache.set(RULES_CACHE_KEY, rules, RULES_CACHE_TTL)
        return rules

    @classmethod
    def invalidate_rules_cache(cls):
        """Clear the cached rules — call this when rules are created/updated/deleted."""
        cache.delete(RULES_CACHE_KEY)

    @classmethod
    def evaluate(cls, input_data: dict, rules=None) -> dict:
        """
        Evaluate the input data against active risk rules.

        Args:
            input_data: Dictionary of user activity fields.
            rules: Optional list of rule dicts or RiskRule objects.
                   If None, fetches from cache/database.

        Returns:
            dict with keys: trust_score, risk_level, flags
        """
        if rules is None:
            rules = cls._get_active_rules()

        score = 100
        flags = []

        for rule in rules:
            # Support both ORM objects and plain dicts
            if isinstance(rule, dict):
                cond_field = rule['condition_field']
                oper = rule['operator']
                threshold = rule['threshold']
                deduction = rule['deduction']
                description = rule['description']
            else:
                cond_field = rule.condition_field
                oper = rule.operator
                threshold = rule.threshold
                deduction = rule.deduction
                description = rule.description

            field_value = input_data.get(cond_field)

            # Skip if the field is not present in the input
            if field_value is None:
                continue

            comparator = cls.OPERATOR_MAP.get(oper)
            if comparator is None:
                continue  # Unknown operator — skip gracefully

            try:
                if comparator(float(field_value), threshold):
                    score -= deduction
                    flags.append(description)
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

