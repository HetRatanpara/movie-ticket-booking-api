
# 📄`README.md`

````markdown
# Ticket Booking API — Backend

**Project**: Movie Ticket Booking backend (Django + DRF + JWT)  
**Status**: Complete

---

## Quick summary

This project provides:

- User signup and JWT login (simplejwt)
- Movie & Show listing
- Book a seat (atomic booking with concurrency protection)
- Cancel booking (owner-only, idempotent)
- My bookings (list user's bookings)
- Admin portal to manage Movies, Shows, Bookings, and Users
- OpenAPI schema and interactive docs (`drf-spectacular` + Swagger / Redoc)

---

## Run locally (Windows / Linux)

1. Create & activate virtualenv
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
````

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser (admin)

```bash
python manage.py createsuperuser
# follow prompts for username, email, password
```

5. Run dev server

```bash
python manage.py runserver
```

API will be available at `http://127.0.0.1:8000/`.

---

## Admin portal

* URL: `http://127.0.0.1:8000/admin/`
* Use the superuser credentials you created with `createsuperuser` to log in.
* Admin can manage:

  * **Users** — view and manage user accounts
  * **Movies** — create/update/delete movies
  * **Shows** — schedule shows (screen, date_time, total_seats)
  * **Bookings** — view bookings, cancel or inspect booking history

> Tip: Admin actions are useful for creating initial movies/shows for testing the booking flow.

---

## Swagger & Schema

* OpenAPI JSON: `http://127.0.0.1:8000/schema/`
* Swagger UI: `http://127.0.0.1:8000/swagger/`
* ReDoc: `http://127.0.0.1:8000/redoc/`

---

## Auth (JWT)

1. **Signup**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"pass123"}'
```

2. **Login** (get tokens)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}'
```

3. **Use access token**

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/auth/me/
```

---

## Key API endpoints

* `GET  /api/movies/` — list movies
* `GET  /api/movies/<movie_id>/shows/` — list shows for a movie
* `POST /api/shows/<id>/book/` — book a seat (auth required)
* `GET  /api/my-bookings/` — list my bookings (auth required)
* `POST /api/bookings/<id>/cancel/` — cancel booking (auth required)

---

## Concurrency & business rules

* Booking is performed inside a DB transaction using `select_for_update()`.
* Unique DB constraint prevents duplicate bookings.
* Retry logic for transient concurrency conflicts.
* Cancelling sets status to `CANCELLED` so seat becomes available again.

---

## Tests

Run unit tests:

```bash
python manage.py test bookings
```

Tests cover:

* Double-booking prevention
* Capacity enforcement (overbooking)
* Cancellation freeing seats

---

## Production notes

* Use PostgreSQL in production.
* Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
* Use environment variables (`django-environ`).
* Consider Sentry/logging and CI.

---

## Submission

* GitHub Repository: [https://github.com/HetRatanpara/movie-ticket-booking-api](https://github.com/HetRatanpara/movie-ticket-booking-api)

```
```
