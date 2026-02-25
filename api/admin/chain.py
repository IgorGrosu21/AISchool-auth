from typing import TYPE_CHECKING

from django.contrib import admin

from api.models import Chain

if TYPE_CHECKING:
    ModelAdmin = admin.ModelAdmin[Chain]
else:
    ModelAdmin = admin.ModelAdmin


@admin.register(Chain)
class ChainAdmin(ModelAdmin):
    list_display = ["id", "user", "login_event", "remember_me", "token_count"]
    search_fields = ["id", "user__id", "user__email", "login_event__id"]
    list_filter = ["remember_me"]
    readonly_fields = ["id", "user", "login_event"]
    raw_id_fields = ["user", "login_event"]
    autocomplete_fields = ["user", "login_event"]
    ordering = ["user__id"]
    list_per_page = 25
    list_max_show_all = 100
    list_editable = ["remember_me"]
    list_display_links = ["id", "user"]
    list_select_related = ["user", "login_event"]

    def token_count(self, obj: Chain) -> int:
        return obj.tokens.count()

    token_count.short_description = "Token Count"  # type: ignore
