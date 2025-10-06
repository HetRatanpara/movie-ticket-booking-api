# bookings/urls.py
from django.urls import path
from .views import (
    MovieListView,
    ShowByMovieListView,
    BookSeatView,
    CancelBookingView,
    MyBookingsView,
    SignupView,
    MeView,
)

urlpatterns = [
    # Movies & shows
    path("movies/", MovieListView.as_view(), name="movies-list"),
    path("movies/<int:movie_id>/shows/", ShowByMovieListView.as_view(), name="movie-shows"),

    # Booking actions
    path("shows/<int:id>/book/", BookSeatView.as_view(), name="book-seat"),
    path("bookings/<int:id>/cancel/", CancelBookingView.as_view(), name="cancel-booking"),
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),

    # Auth endpoints (served from bookings app)
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/me/", MeView.as_view(), name="me"),
]
