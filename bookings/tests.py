from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Movie, Show, Booking, Status

User = get_user_model()

class BookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass123")
        self.movie = Movie.objects.create(title="M", duration_minutes=120)
        self.show = Show.objects.create(movie=self.movie, screen_name="A", date_time="2050-01-01T10:00Z", total_seats=2)

    def test_prevent_double_booking_same_seat(self):
        b1 = Booking.create_booking(self.user, self.show, "A1")
        with self.assertRaises(ValueError):
            Booking.create_booking(self.user, self.show, "A1")

    def test_prevent_overbooking(self):
        Booking.create_booking(self.user, self.show, "A1")
        Booking.create_booking(self.user, self.show, "A2")
        with self.assertRaises(ValueError):
            Booking.create_booking(self.user, self.show, "A3")
