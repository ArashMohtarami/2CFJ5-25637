from django.contrib import admin

from booking_app.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = ("id", "user", "table", "number_of_seats", "cost", "created")
    list_filter = ("user", "table")
    search_fields = ("user__username", "table__id")
    readonly_fields = ("created", "modified")
    ordering = ("-created",)
