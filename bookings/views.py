from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, pagination, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Movie, Show, Booking
from .serializers import (
    UserSignupSerializer,
    MovieSerializer,
    ShowSerializer,
    BookingSerializer,
)
from rest_framework import serializers


# Pagination
class DefaultPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


User = get_user_model()

# add this near other imports and serializer definitions
class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

# In MeView class definition
class MeView(generics.GenericAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    


@extend_schema(
    request=UserSignupSerializer,
    responses={201: UserSignupSerializer},
    examples=[
        OpenApiExample(
            "Signup Example",
            value={"username": "alice", "email": "alice@example.com", "password": "StrongPass!123"},
        )
    ],
    tags=["Auth"],
)
class SignupView(generics.CreateAPIView):
    """
    Public signup endpoint — returns created user (id, username, email).
    """
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Auth"])
class MeView(generics.GenericAPIView):
    """
    Simple protected endpoint to verify JWT; returns current user info.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username, "email": u.email})


@extend_schema(tags=["Movies"])
class MovieListView(generics.ListAPIView):
    """
    Public: list all movies (paginated, ordered by title).
    """
    queryset = Movie.objects.all().order_by("title")
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination


@extend_schema(
    tags=["Shows"],
    parameters=[
        OpenApiParameter(
            name="from",
            description="ISO datetime filter (>=). Example: 2025-10-06T00:00:00Z",
            required=False,
            type=str,
        ),
    ],
)
class ShowByMovieListView(generics.ListAPIView):
    """
    Public: list shows for a given movie, soonest first.
    Optional filter: ?from=<ISO datetime> to only return upcoming shows.
    """
    serializer_class = ShowSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination

    def get_queryset(self):
        movie_id = self.kwargs.get("movie_id")
        get_object_or_404(Movie, id=movie_id)  # ensures 404 if movie doesn't exist
        qs = Show.objects.filter(movie_id=movie_id)
        dt_from = self.request.query_params.get("from")
        if dt_from:
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(dt_from)
            if parsed:
                qs = qs.filter(date_time__gte=parsed)
        return qs.order_by("date_time")



class BookSeatRequestSerializer(serializers.Serializer):
    seat_number = serializers.CharField(max_length=10)

class BookSeatView(APIView):
    serializer_class = BookSeatRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        seat_number = request.data.get("seat_number")
        if not seat_number:
            return Response({"detail": "seat_number required"}, status=status.HTTP_400_BAD_REQUEST)

        show = get_object_or_404(Show, pk=id)

        # Basic validation: seat format/length
        if len(seat_number) > 10:
            return Response({"detail": "invalid seat_number"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.create_booking(user=request.user, show=show, seat_number=seat_number)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CancelBookingView(APIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        booking = get_object_or_404(Booking, pk=id)
        if booking.user != request.user:
            return Response({"detail": "not allowed"}, status=status.HTTP_403_FORBIDDEN)

        changed = booking.cancel()
        if not changed:
            return Response({"detail": "already cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "cancelled"}, status=status.HTTP_200_OK)


class MyBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("-created_at")
