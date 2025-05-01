from django.db.models import Sum, When, Case, Q, FloatField, F, IntegerField
from django.db.models.functions import Coalesce
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from booking_app.models import Table, Reservation
from booking_app.api.serializers import (
    ReservationSerializer,
    BookSerializer,
    CancelReservationSerializer,
)

# cost per seat
SEAT_COST = 100


class ReservationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    ViewSet for managing restaurant reservations.

    - Authenticated users can:
        - Book a table using `/book/`
        - cancel a reservation using `/cancel/`
        - View their reservations with `GET /`
    """

    queryset = Reservation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related(
            "user", "table"
        )

    @action(
        detail=False, methods=["post"], serializer_class=BookSerializer, url_path="book"
    )
    def book(self, request):
        """
        Book a table based on the number of people.

        Rules:
        - Round up odd numbers (unless they match table size).
        - Find the cheapest fitting table.
        - Calculate cost: seat-based or full table cost.

        Returns:
            200 OK with Reservation details.
            400 Bad Request if no table is available.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        people = serializer.validated_data["number_of_people"]

        if people % 2 == 1:
            adjusted_seats = people + 1
        else:
            adjusted_seats = people

        cost_conditions = Case(
            When(Q(seats=people), then=(people - 1) * SEAT_COST),
            When(Q(available_seats=people), then=people * SEAT_COST),
            When(Q(seats=adjusted_seats), then=(adjusted_seats - 1) * SEAT_COST),
            When(
                Q(available_seats__gte=adjusted_seats),
                then=adjusted_seats * SEAT_COST,
            ),
            default=0,
            output_field=FloatField(),
        )

        number_of_seats_conditions = Case(
            When(Q(seats=people), then=people),
            When(Q(available_seats=people), then=people),
            When(Q(seats=adjusted_seats), then=adjusted_seats),
            When(
                Q(available_seats__gte=adjusted_seats),
                then=adjusted_seats,
            ),
            default=0,
            output_field=IntegerField(),
        )

        table = (
            Table.objects.annotate(
                available_seats=F("seats")
                - Coalesce(Sum("reservations__number_of_seats"), 0)
            )
            .filter(available_seats__gte=people)
            .annotate(
                calculated_cost=cost_conditions,
                calculated_number_of_seats=number_of_seats_conditions,
            )
            .exclude(calculated_cost=0.0)
            .order_by("calculated_cost", "available_seats")
            .first()
        )
        if not table:
            return Response(
                {"detail": "No suitable table available."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation = Reservation.objects.create(
            user=request.user,
            table=table,
            number_of_seats=table.calculated_number_of_seats,
            cost=table.calculated_cost,
        )
        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        serializer_class=CancelReservationSerializer,
        url_path="cancel",
    )
    def cancel(self, request):
        """
        Cancel an existing reservation for the user.

        Request body:
            - reservation_id (int): ID of the reservation to cancel.

        Returns:
            200 OK on successful cancellation.
            404 Not Found if reservation does not exist or does not belong to the user.
        """
        reservation_id = request.data.get("reservation_id")
        if not reservation_id:
            return Response(
                {"detail": "Reservation ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reservation = Reservation.objects.get(id=reservation_id, user=request.user)
        except Reservation.DoesNotExist:
            return Response(
                {"detail": "Reservation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        reservation.delete()

        return Response(
            {"detail": "Reservation cancelled successfully."}, status=status.HTTP_200_OK
        )
