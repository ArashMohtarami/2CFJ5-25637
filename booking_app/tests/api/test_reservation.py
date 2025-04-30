from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from booking_app.models import Table, Reservation

User = get_user_model()


class ReservationViewSetTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="pass1234")
        cls.token = Token.objects.create(user=cls.user)

        cls.other_user = User.objects.create_user(
            username="otheruser", password="pass5678"
        )
        Token.objects.create(user=cls.other_user)

        Table.objects.create(seats=4, is_reserved=False)
        Table.objects.create(seats=4, is_reserved=False)
        Table.objects.create(seats=6, is_reserved=False)
        Table.objects.create(seats=5, is_reserved=False)
        Table.objects.create(seats=8, is_reserved=False)
        Table.objects.create(seats=9, is_reserved=False)
        Table.objects.create(seats=10, is_reserved=False)
        Table.objects.create(seats=6, is_reserved=False)
        Table.objects.create(seats=7, is_reserved=False)
        Table.objects.create(seats=10, is_reserved=False)

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_book_table_success(self):
        response = self.client.post("/api/reservations/book/", {"number_of_people": 3})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertTrue(
            Reservation.objects.filter(user=self.user).exists(),
            msg=f"Expected reservation to be created, but it was not.",
        )

    def test_book_table_no_table_available(self):
        Table.objects.all().update(is_reserved=True)

        response = self.client.post("/api/reservations/book/", {"number_of_people": 3})
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Expected 400, but got {response.status_code}",
        )
        self.assertIn(
            "No suitable table available.",
            response.json()["detail"],
            msg=f"Expected 'No suitable table available.' in response,"
            f" but got {response.json()['detail']}",
        )

    def test_book_best_table_choice(self):
        Table.objects.all().update(is_reserved=True)
        Table.objects.all().filter(seats__gt=7).update(is_reserved=False)
        response = self.client.post("/api/reservations/book/", {"number_of_people": 3})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            8,
            response.json()['table']['seats'],
            msg=f"Expected table with 8 seats, but got {response.json()['table']['seats']}",
        )

    def test_book_invalid_data(self):
        response = self.client.post(
            "/api/reservations/book/", {"number_of_people": "abc"}
        )
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Expected 400, but got {response.status_code}",
        )

    def test_list_user_reservations(self):
        table = Table.objects.first()
        reservation = Reservation.objects.create(
            user=self.user, table=table, number_of_seats=4, cost=300
        )
        table.is_reserved = True
        table.save()

        response = self.client.get("/api/reservations/")
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            len(response.json()),
            1,
            msg=f"Expected 1 reservation, but got {len(response.json())}",
        )
        self.assertEqual(
            response.json()[0]["id"],
            reservation.id,
            msg=f"Expected reservation ID {reservation.id}, but got {response.json()[0]['id']}",
        )

    def test_cancel_reservation_success(self):
        table = Table.objects.first()
        reservation = Reservation.objects.create(
            user=self.user, table=table, number_of_seats=4, cost=300
        )
        table.is_reserved = True
        table.save()

        response = self.client.post(
            "/api/reservations/cancel/", {"reservation_id": reservation.id}
        )
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["detail"],
            "Reservation cancelled successfully.",
            msg=f"Expected 'Reservation cancelled successfully.', but got {response.json()['detail']}",
        )
        self.assertFalse(
            Reservation.objects.filter(id=reservation.id).exists(),
            msg=f"Expected reservation to be deleted, but it still exists.",
        )
        self.assertFalse(
            Table.objects.get(id=table.id).is_reserved,
            msg=f"Expected table to be unreserved, but it is still reserved.",
        )

    def test_cancel_reservation_not_found(self):
        response = self.client.post(
            "/api/reservations/cancel/", {"reservation_id": 999}
        )
        self.assertEqual(
            response.status_code,
            404,
            msg=f"Expected 404, but got {response.status_code}",
        )

    def test_cancel_reservation_unauthorized_user(self):
        table = Table.objects.first()
        reservation = Reservation.objects.create(
            user=self.other_user, table=table, number_of_seats=4, cost=300
        )

        response = self.client.post(
            "/api/reservations/cancel/", {"reservation_id": reservation.id}
        )
        self.assertEqual(
            response.status_code,
            404,
            msg=f"Expected 404, but got {response.status_code}",
        )

    def test_cancel_reservation_missing_id(self):
        response = self.client.post("/api/reservations/cancel/", {})
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Expected 400, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["detail"],
            "Reservation ID is required.",
            msg=f"Expected 'Reservation ID is required.', but got {response.json()['detail']}",
        )

    def test_authentication_required(self):
        self.client.credentials()
        response = self.client.get("/api/reservations/")
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Expected 401, but got {response.status_code}",
        )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 2})
        self.assertEqual(
            response.status_code,
            401,
            msg=f"Expected 401, but got {response.status_code}",
        )
