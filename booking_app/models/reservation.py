from django.db import models
from django.contrib.auth import get_user_model

from shared.models.mixins import TimeStampMixin

User = get_user_model()


class Reservation(TimeStampMixin):
    """
    Represents a reservation made by a user.

    Attributes:
        user (User): The user who made the reservation.
        table (Table): The reserved table.
        number_of_seats (int): Number of seats reserved.
        cost (int): Calculated reservation cost.
        created (datetime): Timestamp of creation.
        modified (datetime): Timestamp of modification.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey("Table", on_delete=models.CASCADE, related_name="reservations")
    number_of_seats = models.IntegerField()
    cost = models.IntegerField()


    def __str__(self):
        return f"Reservation {self.id}."

    def __repr__(self):
        return f"Reservation {self.id}."
