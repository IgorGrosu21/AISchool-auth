from typing import TYPE_CHECKING

from django.contrib import admin

from api.models import RefreshToken

if TYPE_CHECKING:
    ModelAdmin = admin.ModelAdmin[RefreshToken]
else:
    ModelAdmin = admin.ModelAdmin


@admin.register(RefreshToken)
class RefreshTokenAdmin(ModelAdmin):
    list_display = ["jti", "chain", "user_email", "is_revoked", "expires_at", "created_at"]
    search_fields = ["jti", "chain__id", "chain__user__email"]
    list_filter = ["is_revoked", "expires_at", "created_at"]
    readonly_fields = ["jti", "chain", "created_at", "expires_at"]
    raw_id_fields = ["chain"]
    autocomplete_fields = ["chain"]
    ordering = ["-created_at"]
    list_per_page = 25
    list_max_show_all = 100
    list_editable = ["is_revoked"]
    list_display_links = ["jti", "chain"]
    list_select_related = ["chain", "chain__user"]

    def user_email(self, obj: RefreshToken) -> str:
        return obj.chain.user.email

    user_email.short_description = "User Email"  # type: ignore
    user_email.admin_order_field = "chain__user__email"  # type: ignore
