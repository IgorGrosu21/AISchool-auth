from typing import TYPE_CHECKING

from django.contrib import admin

from api.models import VerificationCode

if TYPE_CHECKING:
    ModelAdmin = admin.ModelAdmin[VerificationCode]
else:
    ModelAdmin = admin.ModelAdmin


@admin.register(VerificationCode)
class VerificationCodeAdmin(ModelAdmin):
    list_display = ["id", "user", "purpose", "code", "created_at"]
    search_fields = ["id", "user__id", "user__email", "purpose", "code"]
    list_filter = ["purpose", "created_at"]
    readonly_fields = ["id", "user", "created_at"]
    raw_id_fields = ["user"]
    autocomplete_fields = ["user"]
    ordering = ["-created_at"]
    list_per_page = 25
    list_max_show_all = 100
    list_editable = ["purpose", "code"]
    list_display_links = ["id", "user"]
    list_select_related = ["user"]
