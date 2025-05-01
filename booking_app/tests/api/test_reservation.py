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

        Table.objects.create(seats=4)
        Table.objects.create(seats=4)
        Table.objects.create(seats=6)
        Table.objects.create(seats=5)
        Table.objects.create(seats=8)
        Table.objects.create(seats=9)
        Table.objects.create(seats=10)
        Table.objects.create(seats=6)
        Table.objects.create(seats=7)
        Table.objects.create(seats=10)

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
        for table in Table.objects.all():
            Reservation.objects.create(
                user=self.other_user, table=table, number_of_seats=table.seats, cost=100
            )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 3})
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Expected 400, but got {response.status_code}",
        )
        self.assertIn(
            "No suitable table available.",
            response.json()["detail"],
            msg=f"Expected 'No suitable table available.', but got {response.json()['detail']}",
        )

    def test_book_table_over_capacity(self):
        Reservation.objects.all().delete()
        response = self.client.post("/api/reservations/book/", {"number_of_people": 11})
        self.assertEqual(
            response.status_code,
            400,
            msg=f"Expected 400, but got {response.status_code}",
        )
        self.assertIn(
            "No suitable table available.",
            response.json()["detail"],
            msg=f"Expected 'No suitable table available.', but got {response.json()['detail']}",
        )

    def test_book_cheapest_table_choice(self):
        # assume the price is 100 for each seat
        # find cheapest one between 300 and 400
        for table in Table.objects.all():
            if table.seats <= 7:
                if table.seats == 7:
                    Reservation.objects.create(
                        user=self.other_user,
                        table=table,
                        number_of_seats=4,
                        cost=100,
                    )
                else:
                    Reservation.objects.create(
                        user=self.other_user,
                        table=table,
                        number_of_seats=table.seats,
                        cost=100,
                    )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 3})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["table"]["seats"],
            7,
            msg=f"Expected table with 8 seats, but got {response.json()['table']['seats']}",
        )
        self.assertEqual(
            response.json()["cost"],
            300,
            msg=f"Expected table with 300 cost, but got {response.json()["cost"]}",
        )

        Reservation.objects.all().delete()

        # find cheapest one between 300 and 400
        for table in Table.objects.all():
            if table.seats <= 5:
                pass
            else:
                Reservation.objects.create(
                    user=self.other_user,
                    table=table,
                    number_of_seats=table.seats,
                    cost=100,
                )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 3})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["table"]["seats"],
            4,
            msg=f"Expected table with 8 seats, but got {response.json()['table']['seats']}",
        )
        self.assertEqual(
            response.json()["cost"],
            300,
            msg=f"Expected table with 300 cost, but got {response.json()["cost"]}",
        )

        Reservation.objects.all().delete()

        # find cheapest one 500
        for table in Table.objects.all():
            if table.seats == 6:
                pass
            else:
                Reservation.objects.create(
                    user=self.other_user,
                    table=table,
                    number_of_seats=table.seats,
                    cost=100,
                )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 5})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["table"]["seats"],
            6,
            msg=f"Expected table with 8 seats, but got {response.json()['table']['seats']}",
        )
        self.assertEqual(
            response.json()["cost"],
            500,
            msg=f"Expected table with 500 cost, but got {response.json()["cost"]}",
        )

        Reservation.objects.all().delete()

        # find cheapest one between 500 and 400
        for table in Table.objects.all():
            if table.seats <= 5:
                pass
            else:
                Reservation.objects.create(
                    user=self.other_user,
                    table=table,
                    number_of_seats=table.seats,
                    cost=100,
                )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 5})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["table"]["seats"],
            5,
            msg=f"Expected table with 8 seats, but got {response.json()['table']['seats']}",
        )
        self.assertEqual(
            response.json()["cost"],
            400,
            msg=f"Expected table with 400 cost, but got {response.json()["cost"]}",
        )

        Reservation.objects.all().delete()
        # find cheapest one 600
        for table in Table.objects.all():
            if 7 <= table.seats <= 8:
                pass
            else:
                Reservation.objects.create(
                    user=self.other_user,
                    table=table,
                    number_of_seats=table.seats,
                    cost=100,
                )

        response = self.client.post("/api/reservations/book/", {"number_of_people": 5})
        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected 200, but got {response.status_code}",
        )
        self.assertEqual(
            response.json()["table"]["seats"],
            7,
            msg=f"Expected table with 8 seats, but got {response.json()['table']['seats']}",
        )
        self.assertEqual(
            response.json()["cost"],
            600,
            msg=f"Expected table with 600 cost, but got {response.json()["cost"]}",
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
