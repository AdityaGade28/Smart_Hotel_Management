# 🏨 Smart Hotel Management System

A full-stack Django + MySQL web application with map-based hotel discovery, smart recommendations, bookings, food/services, and mock payments.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL 8.0+ (MySQL Workbench)
- pip

---

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Note on `mysqlclient`**: If it fails on Windows, install Visual C++ Build Tools first or use:
> ```bash
> pip install mysqlclient
> # OR alternative:
> pip install PyMySQL
> ```
> If using PyMySQL, add to `hotel_project/__init__.py`:
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

---

### Step 2: Create MySQL Database

Open **MySQL Workbench** and run:

```sql
CREATE DATABASE hotel_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 3: Configure Environment Variables

Edit `.env` file with your MySQL credentials:

```env
SECRET_KEY=django-insecure-hotel-management-secret-key-change-in-production-2024
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=hotel_management
DB_USER=root          # Your MySQL username
DB_PASSWORD=root      # Your MySQL password
DB_HOST=localhost
DB_PORT=3306
```

---

### Step 4: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Step 5: Seed Sample Data

```bash
python manage.py seed_data
```

This creates:
- **6 Indian hotels** (Mumbai, Jaipur, Delhi, Goa, Bengaluru, Shimla)
- **36 rooms** across all hotels (Single, Double, Deluxe, Suite)
- **15 menu items** (Breakfast, Lunch, Dinner, Snacks, Desserts)
- **3 discount coupons**: `WELCOME10`, `FLAT500`, `SUMMER20`
- **Demo users**:

| Username | Password | Role |
|---|---|---|
| admin | Admin@1234 | Admin / Hotel Manager |
| rahul | Customer@123 | Customer / Guest |
| priya | Customer@123 | Customer / Guest |
| amit | Customer@123 | Customer / Guest |

---

### Step 6: Create Django Superuser (if not using seed data)

```bash
python manage.py createsuperuser
```

---

### Step 7: Run the Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 🌐 URL Map

| URL | Description |
|---|---|
| `/` | Home page |
| `/hotels/` | Browse hotels with filters |
| `/hotels/map/` | Interactive Leaflet map |
| `/hotels/<id>/` | Hotel detail page |
| `/users/login/` | Login |
| `/users/register/` | Register |
| `/users/dashboard/` | Customer dashboard |
| `/users/admin-dashboard/` | Admin dashboard |
| `/bookings/hotel/<id>/rooms/` | Browse rooms for booking |
| `/bookings/book/<room_id>/` | Book a room |
| `/bookings/my-bookings/` | Booking history |
| `/payments/checkout/<id>/` | Mock payment |
| `/payments/history/` | Payment history |
| `/food/<booking_id>/menu/` | Food order menu |
| `/food/<booking_id>/services/` | Request services |
| `/admin-hotels/` | Admin: manage hotels |
| `/admin-rooms/` | Admin: manage rooms |
| `/admin/` | Django admin panel |
| `/api/hotels/` | JSON API: hotel list for map |
| `/api/hotels/recommend/` | JSON API: recommended hotel |

---

## 🗂 Project Structure

```
HotelManagement/
├── manage.py
├── .env
├── requirements.txt
├── hotel_project/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                  # Auth + profiles + dashboards
├── hotels/                 # Hotels, rooms, map, recommendation
│   ├── management/commands/seed_data.py
│   └── recommendation.py
├── bookings/               # Booking system + coupons
├── food_services/          # Food menu + service requests
├── payments/               # Mock payment system
├── static/css/style.css    # Custom CSS
└── templates/              # All HTML templates
```

---

## 🗄 Database Schema

| Table | Key Fields |
|---|---|
| `users_customuser` | id, username, email, role, phone |
| `users_profile` | user_id, address, city, photo |
| `hotels_hotel` | id, name, city, latitude, longitude, rating |
| `hotels_room` | id, hotel_id, room_number, type, price, capacity, is_available |
| `bookings_booking` | id, booking_id(UUID), customer, room, check_in, check_out, status, total |
| `bookings_coupon` | code, discount_type, discount_value, valid_until |
| `payments_payment` | id, booking, transaction_id(UUID), amount, method, status |
| `food_services_menuitem` | id, name, category, price, is_veg |
| `food_services_order` | id, booking, status, total |
| `food_services_orderitem` | order, menu_item, quantity |
| `food_services_servicerequest` | id, booking, service_type, status |

---

## ⭐ Smart Recommendation Formula

```
score = (rating × 0.5) + (availability_score × 0.3) + (price_score × 0.2)
```

- `rating` = hotel rating / 5 (normalized 0-1)
- `availability_score` = available_rooms / total_rooms
- `price_score` = 1 - (min_price / 20000) (lower price = higher score)

The hotel with the highest score is automatically highlighted as **⭐ Best Choice** on the home page, hotel list, and map.

---

## 🎫 Discount Coupons (Pre-seeded)

| Code | Type | Value |
|---|---|---|
| WELCOME10 | 10% off | Percentage |
| FLAT500 | ₹500 off | Flat discount |
| SUMMER20 | 20% off | Percentage |

Enter coupon during booking → discount auto-applied.

---

## 🗺 Map Features (Leaflet.js)

- All hotels shown as markers including recommended hotel (gold ⭐ marker)
- Click marker → popup with hotel name, rating, available rooms, price, Book Now button
- **Geolocation**: detects your position and shows nearby hotels
- Filters: city search, min rating, "Show Best Only" toggle
- Sidebar list sorted by recommendation score

---

## 📧 Email Notifications

By default uses **console backend** (printouts in terminal).

To enable real SMTP (Gmail):
1. Update `.env`:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=your@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   ```

---

## 🔒 Security Notes

- All views protected with `@login_required`
- Role-based access: Admin routes check `user.is_admin_user()`
- CSRF protection on all forms
- Passwords hashed with Django's PBKDF2
- Change `SECRET_KEY` and set `DEBUG=False` before deploying

---

## 🧪 Testing Workflow

1. Register as **customer** → browse hotels → view map → book room
2. Enter coupon code (e.g., `WELCOME10`) → see discount
3. Complete mock payment → see confirmation
4. From booking detail → order food, request service
5. Login as **admin** → dashboard → update booking status, food orders
6. Add hotels/rooms from admin panel → see them on map instantly
