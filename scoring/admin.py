from django.contrib import admin

from .models import EvaluationRecord, RiskRule


@admin.register(RiskRule)
class RiskRuleAdmin(admin.ModelAdmin):
    list_display = ("description", "condition_field", "operator", "threshold", "deduction", "is_active")
    list_filter = ("is_active", "operator")
    search_fields = ("description", "condition_field")


@admin.register(EvaluationRecord)
class EvaluationRecordAdmin(admin.ModelAdmin):
    list_display = ("user_id", "trust_score", "risk_level", "evaluated_at")
    list_filter = ("risk_level",)
    search_fields = ("user_id",)
    readonly_fields = ("user_id", "trust_score", "risk_level", "flags", "input_data", "evaluated_at")
