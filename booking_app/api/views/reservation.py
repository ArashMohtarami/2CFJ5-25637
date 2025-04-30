from django.db import transaction
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from booking_app.models import Table, Reservation
from booking_app.api.serializers import ReservationSerializer, BookSerializer, CancelReservationSerializer

# cost per seat
SEAT_COST = 100


class ReservationViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin
):
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
        return (
            self.queryset.filter(user=self.request.user).select_related('user', 'table')
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

        adjusted_seats = people
        if 4 <= people:
            adjusted_seats = people
        elif people % 2 == 1:
            adjusted_seats = 4

        with transaction.atomic():
            table = (
                Table.objects.select_for_update(skip_locked=True)
                .filter(is_reserved=False, seats__gte=adjusted_seats)
                .order_by("seats")
                .first()
            )

            if not table:
                return Response(
                    {"detail": "No suitable table available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            table.is_reserved = True
            table.save()

            if adjusted_seats == table.seats:
                cost = (table.seats - 1) * SEAT_COST
            else:
                cost = adjusted_seats * SEAT_COST

            reservation = Reservation.objects.create(
                user=request.user,
                table=table,
                number_of_seats=adjusted_seats,
                cost=cost,
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
            reservation = Reservation.objects.get(
                id=reservation_id, user=request.user
            )
        except Reservation.DoesNotExist:
            return Response(
                {"detail": "Reservation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        reservation.table.is_reserved = False
        reservation.table.save()
        reservation.delete()

        return Response(
            {"detail": "Reservation cancelled successfully."}, status=status.HTTP_200_OK
        )
