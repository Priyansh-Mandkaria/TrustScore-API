from django.contrib import admin

from .models import EvaluationRecord, RiskRule
from .services import RiskScoringEngine


@admin.register(RiskRule)
class RiskRuleAdmin(admin.ModelAdmin):
    list_display = ("description", "condition_field", "operator", "threshold", "deduction", "is_active")
    list_filter = ("is_active", "operator")
    search_fields = ("description", "condition_field")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        RiskScoringEngine.invalidate_rules_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        RiskScoringEngine.invalidate_rules_cache()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        RiskScoringEngine.invalidate_rules_cache()


@admin.register(EvaluationRecord)
class EvaluationRecordAdmin(admin.ModelAdmin):
    list_display = ("user_id", "trust_score", "risk_level", "evaluated_at")
    list_filter = ("risk_level",)
    search_fields = ("user_id",)
    readonly_fields = ("user_id", "trust_score", "risk_level", "flags", "input_data", "evaluated_at")
