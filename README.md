# CityCare Hospital Management System

A responsive Hospital Management web application featuring patient authentication, medical profile management, password recovery, and a landing page with real-time doctor availability and appointment booking.

---

## 🎨 Theme & Color Palette
* **Backgrounds**: Pure White (`#ffffff`) and Soft Slate (`#f8fafc`).
* **Medical Blues**: Clinical Sky Blue (`#0284c7`) and Deep Navy (`#0369a1`).
* **Pleasant Greens**: Emerald Health Green (`#059669`, `#10b981`) for available status & booking actions.
* **Typography**: Crisp Black text (`#111827`) for optimal legibility.

---

## 🚀 How to Run

### Option 1: Using Docker (Containerized)
Make sure Docker Desktop is running, then in the project root folder run:
```bash
docker compose up --build
```
Open your browser and navigate to:
```
http://localhost:8000
```

---

### Option 2: Using Python Directly (Local)
1. Install dependencies (if not already installed):
```bash
python -m pip install -r requirements.txt
```

2. Start the FastAPI server:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Open your browser and visit:
```
http://localhost:8000
```
*(Interactive API documentation is also available at `http://localhost:8000/docs`)*

---

## 📋 Features & Dedicated Pages

| Page | URL | Description |
| :--- | :--- | :--- |
| **Landing Page** | `http://localhost:8000/` or `index.html` | Welcoming hospital homepage, key statistics, and links to all dedicated sections. |
| **About Hospital** | `http://localhost:8000/about.html` | Dedicated page for hospital infrastructure, mission/vision, facilities, and quality accreditations. |
| **Doctors & Availability** | `http://localhost:8000/doctors.html` | Dedicated doctor directory, specialty filters, daily max slots (25–40 slots), and appointment booking modal. |
| **Patient Profile** | `http://localhost:8000/profile.html` | Dedicated patient profile form (name, contact, address, blood group, emergency details) saved to backend. |
| **My Appointments** | `http://localhost:8000/appointments.html` | Dedicated schedule page displaying all booked appointments and their real-time statuses. |
| **Contact & Emergency** | `http://localhost:8000/contact.html` | Dedicated 24/7 emergency hotlines, ambulance dispatch, visiting hours, and inquiry message form. |
| **Login** | `http://localhost:8000/login.html` | Secure patient and user login with username/email and password. |
| **Create Account** | `http://localhost:8000/register.html` | New user sign up with username, email, and password. |
| **Forgot Password** | `http://localhost:8000/forgot-password.html` | Dedicated two-step password recovery (generate security token, reset password). |

