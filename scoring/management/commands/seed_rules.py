from django.core.management.base import BaseCommand

from scoring.models import RiskRule

DEFAULT_RULES = [
    {
        "condition_field": "account_age_days",
        "operator": "lt",
        "threshold": 7,
        "deduction": 20,
        "description": "New account",
    },
    {
        "condition_field": "failed_logins",
        "operator": "gt",
        "threshold": 3,
        "deduction": 15,
        "description": "High failed login attempts",
    },
    {
        "condition_field": "transactions_last_24h",
        "operator": "gt",
        "threshold": 20,
        "deduction": 20,
        "description": "Unusual transaction volume",
    },
    {
        "condition_field": "ip_changes",
        "operator": "gt",
        "threshold": 2,
        "deduction": 10,
        "description": "Suspicious IP changes",
    },
    {
        "condition_field": "avg_transaction_amount",
        "operator": "gt",
        "threshold": 5000,
        "deduction": 15,
        "description": "High average transaction amount",
    },
]


class Command(BaseCommand):
    help = "Seed the database with default risk rules."

    def handle(self, *args, **options):
        created_count = 0
        for rule_data in DEFAULT_RULES:
            _, created = RiskRule.objects.get_or_create(
                condition_field=rule_data["condition_field"],
                operator=rule_data["operator"],
                defaults=rule_data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} new rule(s) created, "
                f"{len(DEFAULT_RULES) - created_count} already existed."
            )
        )
