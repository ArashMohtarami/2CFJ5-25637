from rest_framework import serializers

from booking_app.models import Reservation
from .table import TableSerializer


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for Reservation model.
    """

    table = TableSerializer(read_only=True, many=False)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user",
            "number_of_seats",
            "cost",
            "created",
            "modified",
            "table",
        ]
        read_only_fields = [
            "id",
            "user",
            "table",
            "number_of_seats",
            "cost",
            "created",
            "modified",
        ]


class BookSerializer(serializers.Serializer):
    """
    Serializer for booking a table.

    Fields:
        number_of_people (int): Number of individuals requesting a reservation.
    """

    number_of_people = serializers.IntegerField(min_value=1)



class CancelReservationSerializer(serializers.Serializer):
    """
    Serializer for reservation cancellation requests.
    """
    reservation_id = serializers.IntegerField()
