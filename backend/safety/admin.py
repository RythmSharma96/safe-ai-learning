from django.contrib import admin

from .models import FlagCategory, ModerationResult


@admin.register(FlagCategory)
class FlagCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "has_patterns", "has_response"]

    @admin.display(boolean=True)
    def has_patterns(self, obj):
        return bool(obj.patterns)

    @admin.display(boolean=True)
    def has_response(self, obj):
        return bool(obj.canned_response)


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = ["id", "message", "is_flagged", "created_at"]
    list_filter = ["is_flagged", "created_at"]
