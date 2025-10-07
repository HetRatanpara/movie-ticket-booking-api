from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from .models import Movie, Show, Booking, Status

User = get_user_model()


class BookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="Str0ngPass!123")
        self.movie = Movie.objects.create(title="Model Test Movie", duration_minutes=120)
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=timezone.now() + timedelta(days=1),
            total_seats=2,
        )

    def test_prevent_double_booking_same_seat(self):
        b1 = Booking.create_booking(self.user, self.show, "1")
        self.assertEqual(b1.status, Status.BOOKED)
        with self.assertRaises(ValueError):
            Booking.create_booking(self.user, self.show, "1")

    def test_prevent_overbooking(self):
        Booking.create_booking(self.user, self.show, "1")
        Booking.create_booking(self.user, self.show, "2")
        with self.assertRaises(ValueError):
            Booking.create_booking(self.user, self.show, "3")

    def test_cancel_frees_seat(self):
        b = Booking.create_booking(self.user, self.show, "1")
        self.assertEqual(b.status, Status.BOOKED)
        # cancel
        changed = b.cancel()
        self.assertTrue(changed)
        b.refresh_from_db()
        self.assertEqual(b.status, Status.CANCELLED)
        # now the same seat should be re-bookable
        b2 = Booking.create_booking(self.user, self.show, "1")
        self.assertEqual(b2.status, Status.BOOKED)


class BookingApiTests(TestCase):
    def setUp(self):
        # Use DRF APIClient for auth convenience
        self.client = APIClient()
        # Create a movie+show to use in API tests
        self.movie = Movie.objects.create(title="API Test Movie", duration_minutes=100)
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen A",
            date_time=timezone.now() + timedelta(days=2),
            total_seats=2,
        )
        # credentials for test user
        self.username = "apitestuser"
        self.password = "Str0ngPass!123"

    def test_signup_login_and_booking_flow(self):
        # 1) Signup
        signup_resp = self.client.post(
            "/api/auth/signup/",
            {"username": self.username, "email": "a@a.com", "password": self.password},
            format="json",
        )
        self.assertIn(signup_resp.status_code, (200, 201), msg=f"Signup failed: {signup_resp.content}")

        # 2) Login to get JWT tokens
        login_resp = self.client.post(
            "/api/auth/login/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(login_resp.status_code, 200, msg=f"Login failed: {login_resp.content}")
        self.assertIn("access", login_resp.data)
        access = login_resp.data["access"]

        # attach token for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # 3) Book a seat (should succeed)
        book_url = f"/api/shows/{self.show.id}/book/"
        book_resp = self.client.post(book_url, {"seat_number": "1"}, format="json")
        self.assertEqual(book_resp.status_code, 201, msg=f"Booking failed: {book_resp.content}")
        booking_id = book_resp.data.get("id")
        self.assertIsNotNone(booking_id)

        # 4) Booking same seat again should fail
        book_resp2 = self.client.post(book_url, {"seat_number": "1"}, format="json")
        self.assertIn(book_resp2.status_code, (400, 409), msg=f"Double booking allowed: {book_resp2.content}")

        # 5) My bookings returns at least the created booking
        my_bookings_resp = self.client.get("/api/my-bookings/")
        self.assertEqual(my_bookings_resp.status_code, 200)
        found_ids = [b.get("id") for b in my_bookings_resp.data.get("results", my_bookings_resp.data)]
        self.assertIn(booking_id, found_ids)

        # 6) Cancel booking (owner)
        cancel_resp = self.client.post(f"/api/bookings/{booking_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, 200, msg=f"Cancel failed: {cancel_resp.content}")

        # 7) After cancel, seat should be rebookable
        # create second booking on same seat
        book_resp3 = self.client.post(book_url, {"seat_number": "1"}, format="json")
        self.assertEqual(book_resp3.status_code, 201, msg=f"Rebooking after cancel failed: {book_resp3.content}")

    def test_cannot_cancel_other_users_booking(self):
        # signup user1 and book
        user1_pw = "Uniqu3User1!@#"
        resp1 = self.client.post("/api/auth/signup/", {"username": "user1", "email": "u1@a.com", "password": user1_pw}, format="json")
        self.assertIn(resp1.status_code, (200, 201), msg=f"Signup user1 failed: {resp1.content}")
        login1 = self.client.post("/api/auth/login/", {"username": "user1", "password": user1_pw}, format="json")
        self.assertEqual(login1.status_code, 200, msg=f"Login user1 failed: {login1.content}")
        token1 = login1.data["access"]
        client1 = APIClient()
        client1.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        book_resp = client1.post(f"/api/shows/{self.show.id}/book/", {"seat_number": "2"}, format="json")
        self.assertEqual(book_resp.status_code, 201, msg=f"Booking by user1 failed: {book_resp.content}")
        booking_id = book_resp.data.get("id")

        # signup user2 and try to cancel booking1
        user2_pw = "Uniqu3User2!@#"
        resp2 = self.client.post("/api/auth/signup/", {"username": "user2", "email": "u2@a.com", "password": user2_pw}, format="json")
        self.assertIn(resp2.status_code, (200, 201), msg=f"Signup user2 failed: {resp2.content}")
        login2 = self.client.post("/api/auth/login/", {"username": "user2", "password": user2_pw}, format="json")
        self.assertEqual(login2.status_code, 200, msg=f"Login user2 failed: {login2.content}")
        token2 = login2.data["access"]
        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

        cancel_resp = client2.post(f"/api/bookings/{booking_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, 403, msg=f"Other user could cancel booking: {cancel_resp.content}")
