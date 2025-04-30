from django.contrib import admin

from booking_app.models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):

    list_display = ("id", "seats", "is_reserved")
    list_filter = ("is_reserved",)
    search_fields = ("id",)
    readonly_fields = ("created", "modified")
    ordering = ("-created",)
