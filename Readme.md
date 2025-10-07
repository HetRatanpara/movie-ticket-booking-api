# 🎟️ Movie Ticket Booking API (Backend Intern Assignment)

**Tech Stack:** Python · Django · Django REST Framework · JWT (SimpleJWT) · Swagger (drf-spectacular)

---

## 📌 Objective

A Movie Ticket Booking System backend built with Django and Django REST Framework.  
Implements authentication, movie/show management, seat booking with concurrency protection,  
and full Swagger documentation at `/swagger/`.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/hetratanpara/movie-ticket-booking-api.git
cd movie-ticket-booking-api
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```
Server runs at http://127.0.0.1:8000/

---

## 🔑 Authentication (JWT)

### Signup
```bash
POST /api/auth/signup/
Content-Type: application/json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "pass123"
}
```

### Login (Get JWT)
```bash
POST /api/auth/login/
Content-Type: application/json
{
  "username": "alice",
  "password": "pass123"
}
```

**Response:**
```json
{
  "refresh": "<REFRESH_TOKEN>",
  "access": "<ACCESS_TOKEN>"
}
```

Use the access token for all protected endpoints:

```
Authorization: Bearer <ACCESS_TOKEN>
```

---

## 🎬 API Endpoints

### ⚙️ Admin
- **[GET]** `/admin/` – Django Admin Portal (Superuser login required)  

### 🔑 Authentication
- **[POST]** `/api/auth/signup/` – Register a new user (No Auth)  
- **[POST]** `/api/auth/login/` – Obtain JWT tokens (No Auth)  
- **[GET]** `/api/auth/me/` – Get current user info (Requires Auth)  

### 🎥 Movies & Shows
- **[GET]** `/api/movies/` – List all movies (No Auth)  
- **[GET]** `/api/movies/{movie_id}/shows/` – List shows for a specific movie (No Auth)  

### 🎟️ Bookings
- **[POST]** `/api/shows/{id}/book/` – Book a seat (`seat_number`) (Requires Auth)  
- **[GET]** `/api/my-bookings/` – View logged-in user’s bookings (Requires Auth)  
- **[POST]** `/api/bookings/{id}/cancel/` – Cancel own booking (Requires Auth)  


---

## ⚙️ Business Logic

- **Prevent double booking**: Unique constraint on (show, seat_number) when status='booked'.  
- **Prevent overbooking**: Checks existing count vs. total_seats.  
- **Free seat after cancel**: Cancelling sets status to cancelled, freeing the seat.  
- **Concurrency safe**: Uses `transaction.atomic()` + `select_for_update()` + retry on `IntegrityError`.  

---

## 🧾 Swagger Documentation

- Swagger UI: http://127.0.0.1:8000/swagger/  
- Redoc: http://127.0.0.1:8000/redoc/  
- OpenAPI Schema: http://127.0.0.1:8000/schema/  

JWT authentication and all endpoints are documented automatically via drf-spectacular.

---

## 🧩 Admin Portal

Admin can manage Movies, Shows, Bookings, and Users.  

- URL: http://127.0.0.1:8000/admin/  
- Login: Use the superuser credentials created earlier.  

---

## 🧪 Testing

Run unit tests for booking logic:
```bash
python manage.py test bookings
```

Covers:
- Preventing duplicate bookings  
- Preventing overbooking  
- Ensuring cancel frees the seat  

---

## 🧠 Bonus Features Implemented

- Retry logic for concurrent booking attempts (IntegrityError handling)  
- Detailed validation for seat format & range  
- Clear, friendly error responses  
- Owner-only booking cancellation  
- Unit tests for booking logic  
- Comprehensive Swagger docs  

---

## 📦 Deliverables Summary

✅ Django project code  
✅ requirements.txt  
✅ Well-documented README.md (this file)  
✅ Swagger docs at /swagger/  

---

## 🚀 Expected API Flow

1. `POST /api/auth/signup/` → register user  
2. `POST /api/auth/login/` → obtain JWT  
3. `GET /api/movies/` → view all movies  
4. `GET /api/movies/<id>/shows/` → view shows for a movie  
5. `POST /api/shows/<id>/book/` → book seat  
6. `GET /api/my-bookings/` → view your bookings  
7. `POST /api/bookings/<id>/cancel/` → cancel a booking  

---

## 🧰 Requirements

```shell
asgiref==3.10.0
attrs==25.3.0
Django==5.2.7
django-cors-headers==4.9.0
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
drf-spectacular==0.27.2
inflection==0.5.1
jsonschema==4.25.1
jsonschema-specifications==2025.9.1
PyJWT==2.10.1
PyYAML==6.0.3
referencing==0.36.2
rpds-py==0.27.1
sqlparse==0.5.3
typing_extensions==4.15.0
tzdata==2025.2
uritemplate==4.2.0
```

---

## 👤 Author

**Het Ratanpara**  
Backend Developer Intern Candidate  
GitHub: https://github.com/HetRatanpara/movie-ticket-booking-api 
