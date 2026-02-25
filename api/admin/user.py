from typing import TYPE_CHECKING

from django.contrib import admin

from api.models import User

if TYPE_CHECKING:
    ModelAdmin = admin.ModelAdmin[User]
else:
    ModelAdmin = admin.ModelAdmin


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ["id", "email", "is_verified", "date_joined"]
    search_fields = ["id", "email"]
    list_filter = ["is_verified", "date_joined"]
    readonly_fields = ["id", "email", "date_joined"]
    ordering = ["-date_joined"]
    list_per_page = 25
    list_max_show_all = 100
    list_editable = ["is_verified"]
    list_display_links = ["id", "email"]
