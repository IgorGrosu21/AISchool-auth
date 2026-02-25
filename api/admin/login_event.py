from typing import TYPE_CHECKING

from django.contrib import admin

from api.models import LoginEvent

if TYPE_CHECKING:
    ModelAdmin = admin.ModelAdmin[LoginEvent]
else:
    ModelAdmin = admin.ModelAdmin


@admin.register(LoginEvent)
class LoginEventAdmin(ModelAdmin):
    list_display = [
        "id",
        "user",
        "login_at",
        "last_activity",
        "login_method",
        "success",
        "failure_reason",
    ]
    search_fields = ["id", "user__id", "user__email", "login_method"]
    list_filter = ["success", "failure_reason", "login_method"]
    readonly_fields = ["id", "user", "login_at", "last_activity", "login_method"]
    raw_id_fields = ["user"]
    autocomplete_fields = ["user"]
    ordering = ["-login_at"]
    list_per_page = 25
    list_max_show_all = 100
    list_editable = ["success", "failure_reason"]
    list_display_links = ["id", "user", "login_at"]
    list_select_related = ["user"]
