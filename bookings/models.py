# bookings/models.py
import re
import time
from django.db import models, transaction, IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Status choices
class Status(models.TextChoices):
    BOOKED = "booked", "Booked"
    CANCELLED = "cancelled", "Cancelled"

class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    screen_name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.movie.title} — {self.screen_name} @ {self.date_time}"

    def seats_booked_count(self):
        return self.bookings.filter(status=Status.BOOKED).count()

# Booking model with robust create and cancel logic
SEAT_PATTERN = re.compile(r"^([A-Z])?(\d{1,4})$")  # adjust to your seat naming scheme

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="bookings")
    seat_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["show", "seat_number"],
                condition=Q(status=Status.BOOKED),
                name="unique_booked_seat"
            )
        ]

    def __str__(self):
        return f"{self.user} — {self.show} seat {self.seat_number} ({self.status})"

    def cancel(self):
        """
        Idempotent cancellation — safe to call multiple times.
        Returns True if status changed to CANCELLED, False if it was already cancelled.
        """
        with transaction.atomic():
            b = Booking.objects.select_for_update().get(pk=self.pk)
            if b.status == Status.CANCELLED:
                return False
            b.status = Status.CANCELLED
            b.save(update_fields=["status"])
            return True

    @staticmethod
    def _validate_seat_number(show: "Show", seat_number: str):
        m = SEAT_PATTERN.match(seat_number.strip().upper())
        if not m:
            raise ValidationError("seat_number must match pattern (optional letter + number), e.g. A12 or 12")

        num_part = int(m.group(2))
        if num_part < 1:
            raise ValidationError("seat number must be >= 1")

        if num_part > show.total_seats:
            raise ValidationError(f"seat number {num_part} exceeds capacity ({show.total_seats})")

        return seat_number.strip().upper()

    @staticmethod
    def create_booking(user, show, seat_number, max_retries=3, retry_delay=0.05):
        """
        Robust booking with retries on IntegrityError.
        - Validates seat format and range.
        - Uses select_for_update on the show row, checks counts, then attempts to create booking.
        - Catches IntegrityError and retries a few times (optimistic fallback).
        Raises ValueError for client-friendly errors.
        """
        # validate seat format / range before DB locking
        try:
            seat_number = Booking._validate_seat_number(show, seat_number)
        except ValidationError as e:
            raise ValueError(str(e))

        attempts = 0
        while True:
            attempts += 1
            try:
                with transaction.atomic():
                    locked_show = Show.objects.select_for_update().get(pk=show.pk)

                    # check if seat already booked (BOOKED)
                    exists = Booking.objects.filter(show=locked_show, seat_number=seat_number, status=Status.BOOKED).exists()
                    if exists:
                        raise ValueError("Seat already booked")

                    booked = Booking.objects.filter(show=locked_show, status=Status.BOOKED).count()
                    if booked >= locked_show.total_seats:
                        raise ValueError("Show is fully booked")

                    booking = Booking.objects.create(user=user, show=locked_show, seat_number=seat_number, status=Status.BOOKED)
                    return booking

            except IntegrityError:
                # likely unique constraint hit due to concurrent commit
                if attempts >= max_retries:
                    raise ValueError("Seat could not be reserved due to concurrent requests. Please try again.")
                time.sleep(retry_delay * attempts)
                continue
