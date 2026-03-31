from django.contrib import admin

from .models import FlagCategory, ModerationResult


@admin.register(FlagCategory)
class FlagCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = ["id", "message", "is_flagged", "created_at"]
    list_filter = ["is_flagged", "created_at"]
