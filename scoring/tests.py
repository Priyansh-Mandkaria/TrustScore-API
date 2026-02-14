from django.test import TestCase
from rest_framework.test import APIClient

from .models import EvaluationRecord, RiskRule
from .services import RiskScoringEngine


class RiskScoringEngineTests(TestCase):
    """Unit tests for the scoring engine, independent of views."""

    def setUp(self):
        """Create a standard set of rules for testing."""
        RiskRule.objects.create(
            condition_field="account_age_days", operator="lt",
            threshold=7, deduction=20, description="New account",
        )
        RiskRule.objects.create(
            condition_field="failed_logins", operator="gt",
            threshold=3, deduction=15, description="High failed login attempts",
        )
        RiskRule.objects.create(
            condition_field="transactions_last_24h", operator="gt",
            threshold=20, deduction=20, description="Unusual transaction volume",
        )
        RiskRule.objects.create(
            condition_field="ip_changes", operator="gt",
            threshold=2, deduction=10, description="Suspicious IP changes",
        )
        RiskRule.objects.create(
            condition_field="avg_transaction_amount", operator="gt",
            threshold=5000, deduction=15, description="High average transaction amount",
        )

    def test_low_risk_user(self):
        """A user with all safe values should get 100 and LOW risk."""
        data = {
            "user_id": "U999",
            "account_age_days": 365,
            "failed_logins": 0,
            "transactions_last_24h": 2,
            "ip_changes": 0,
            "avg_transaction_amount": 100,
        }
        result = RiskScoringEngine.evaluate(data)
        self.assertEqual(result["trust_score"], 100)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["flags"], [])

    def test_high_risk_user(self):
        """The example input from the requirements should produce HIGH risk."""
        data = {
            "user_id": "U123",
            "account_age_days": 5,
            "failed_logins": 6,
            "transactions_last_24h": 30,
            "ip_changes": 4,
            "avg_transaction_amount": 7000,
        }
        result = RiskScoringEngine.evaluate(data)
        # Expected: 100 - 20 - 15 - 20 - 10 - 15 = 20
        self.assertEqual(result["trust_score"], 20)
        self.assertEqual(result["risk_level"], "HIGH")
        self.assertEqual(len(result["flags"]), 5)

    def test_medium_risk_user(self):
        """Trigger some rules for a MEDIUM risk level (50-79)."""
        data = {
            "user_id": "U456",
            "account_age_days": 3,     # triggers -20
            "failed_logins": 1,
            "transactions_last_24h": 5,
            "ip_changes": 0,
            "avg_transaction_amount": 200,
        }
        result = RiskScoringEngine.evaluate(data)
        # Expected: 100 - 20 = 80 → LOW boundary
        self.assertEqual(result["trust_score"], 80)
        self.assertEqual(result["risk_level"], "LOW")

    def test_score_clamps_to_zero(self):
        """Score should never go below 0 even with excessive deductions."""
        # Add an extra harsh rule
        RiskRule.objects.create(
            condition_field="failed_logins", operator="gt",
            threshold=0, deduction=200, description="Extra harsh rule",
        )
        data = {
            "user_id": "U000",
            "account_age_days": 1,
            "failed_logins": 5,
            "transactions_last_24h": 50,
            "ip_changes": 10,
            "avg_transaction_amount": 99999,
        }
        result = RiskScoringEngine.evaluate(data)
        self.assertEqual(result["trust_score"], 0)
        self.assertEqual(result["risk_level"], "HIGH")

    def test_inactive_rule_ignored(self):
        """Inactive rules should not affect the score."""
        RiskRule.objects.all().update(is_active=False)
        data = {
            "user_id": "U111",
            "account_age_days": 1,
            "failed_logins": 100,
            "transactions_last_24h": 100,
            "ip_changes": 100,
            "avg_transaction_amount": 100000,
        }
        result = RiskScoringEngine.evaluate(data)
        self.assertEqual(result["trust_score"], 100)
        self.assertEqual(result["risk_level"], "LOW")


class EvaluateUserViewTests(TestCase):
    """Integration tests for the POST /api/evaluate-user/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        RiskRule.objects.create(
            condition_field="account_age_days", operator="lt",
            threshold=7, deduction=20, description="New account",
        )
        RiskRule.objects.create(
            condition_field="failed_logins", operator="gt",
            threshold=3, deduction=15, description="High failed login attempts",
        )

    def test_evaluate_success(self):
        """POST with valid data returns 200 and correct structure."""
        payload = {
            "user_id": "U123",
            "account_age_days": 5,
            "failed_logins": 6,
            "transactions_last_24h": 2,
            "ip_changes": 0,
            "avg_transaction_amount": 100,
        }
        response = self.client.post("/api/evaluate-user/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("trust_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("flags", data)
        # Should trigger both rules: -20 -15 = 65
        self.assertEqual(data["trust_score"], 65)
        self.assertEqual(data["risk_level"], "MEDIUM")

    def test_evaluate_creates_record(self):
        """Evaluation should persist an EvaluationRecord."""
        payload = {
            "user_id": "U123",
            "account_age_days": 365,
            "failed_logins": 0,
            "transactions_last_24h": 1,
            "ip_changes": 0,
            "avg_transaction_amount": 50,
        }
        self.client.post("/api/evaluate-user/", payload, format="json")
        self.assertEqual(EvaluationRecord.objects.count(), 1)
        record = EvaluationRecord.objects.first()
        self.assertEqual(record.user_id, "U123")

    def test_evaluate_missing_fields(self):
        """POST with missing required fields should return 400."""
        payload = {"user_id": "U123"}
        response = self.client.post("/api/evaluate-user/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_evaluate_negative_values(self):
        """POST with negative numeric values should return 400."""
        payload = {
            "user_id": "U123",
            "account_age_days": -1,
            "failed_logins": 0,
            "transactions_last_24h": 0,
            "ip_changes": 0,
            "avg_transaction_amount": 0,
        }
        response = self.client.post("/api/evaluate-user/", payload, format="json")
        self.assertEqual(response.status_code, 400)


class UserHistoryViewTests(TestCase):
    """Integration tests for GET /api/user-history/<user_id>/."""

    def setUp(self):
        self.client = APIClient()
        EvaluationRecord.objects.create(
            user_id="U123", trust_score=80, risk_level="LOW",
            flags=[], input_data={"user_id": "U123"},
        )
        EvaluationRecord.objects.create(
            user_id="U123", trust_score=40, risk_level="HIGH",
            flags=["New account"], input_data={"user_id": "U123"},
        )

    def test_returns_history(self):
        """GET should return all records for the given user."""
        response = self.client.get("/api/user-history/U123/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_returns_empty_for_unknown_user(self):
        """GET for a user with no evaluations should return empty list."""
        response = self.client.get("/api/user-history/U999/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
