# bookings/serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Movie, Show, Booking

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # ensure proper hashing
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Read-only serializers for later use (no write logic here yet)
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "duration_minutes"]


class ShowSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Show
        fields = ["id", "movie", "screen_name", "date_time", "total_seats"]




class BookingSerializer(serializers.ModelSerializer):
    show = ShowSerializer(read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Booking
        fields = ("id", "show", "seat_number", "status", "created_at")