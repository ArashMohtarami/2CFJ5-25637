from django.db import models

from shared.models.mixins import TimeStampMixin


class Table(TimeStampMixin):
    """
    Represents a table in the restaurant.

    Attributes:
        seats (int): Number of seats at the table (M between 4 and 10).
        is_reserved (bool): Status flag indicating if the table is currently reserved.
        created (datetime): Timestamp of creation.
        modified (datetime): Timestamp of modification.
    """

    seats = models.IntegerField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.id}, ({self.seats} seats)"

    def __repr__(self):
        return f"Table {self.id}, ({self.seats} seats)"
