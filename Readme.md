
````markdown
# 🎟️ Ticket Booking API — Backend

**Project**: Movie Ticket Booking Backend  
**Stack**: Django + Django REST Framework + JWT (SimpleJWT)  
**Status**: ✅ Complete (Phases 1–7 implemented)

---

## 🧩 Features

- User registration and JWT authentication
- Movies & shows listing (with filters)
- Atomic seat booking with concurrency protection
- Booking cancellation (idempotent, owner-only)
- User's booking history
- Auto-generated API schema with Swagger & ReDoc (`drf-spectacular`)

---

## ⚙️ Getting Started (Windows / Linux / macOS)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
````

### 2. Create & activate virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. (Optional) Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run development server

```bash
python manage.py runserver
```

> The API will be available at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 📚 API Documentation

* **OpenAPI schema (JSON)**: [http://127.0.0.1:8000/schema/](http://127.0.0.1:8000/schema/)
* **Swagger UI**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
* **ReDoc**: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

## 🔐 Authentication (JWT)

### Signup

```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "pass123"}'
```

### Login (Get Tokens)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass123"}'
```

**Response:**

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

### Authenticated Request Example

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://127.0.0.1:8000/api/auth/me/
```

---

## 🔑 Key API Endpoints

| Method | Endpoint                        | Description                                                   |
| ------ | ------------------------------- | ------------------------------------------------------------- |
| `GET`  | `/api/movies/`                  | List all movies (paginated)                                   |
| `GET`  | `/api/movies/<movie_id>/shows/` | List shows for a movie (supports `?from=ISO_DATETIME` filter) |
| `POST` | `/api/shows/<id>/book/`         | Book a seat (body: `{ "seat_number": "A1" }`) — auth required |
| `GET`  | `/api/my-bookings/`             | List current user's bookings — auth required                  |
| `POST` | `/api/bookings/<id>/cancel/`    | Cancel a booking — auth required, owner-only                  |

---

## 🧠 Business Logic & Concurrency

* **Seat Booking**

  * Implemented using `select_for_update()` inside a DB transaction
  * Unique DB constraint on show + seat to prevent double booking
  * Custom retry logic in `Booking.create_booking()` handles race conditions (e.g., concurrent `IntegrityError`)
  * Validates seat format and ensures `seat_number <= total_seats`

* **Booking Cancellation**

  * Sets booking status to `CANCELLED`
  * Cancelling is **idempotent** — repeated requests won’t cause errors
  * Cancelled seats become available again

---

## 📝 License

This project is for educational/demo purposes. Please modify and use as needed for personal or commercial projects.

---

## 🙋‍♂️ Support or Questions?

Feel free to open an issue or contribute via pull requests.

```

