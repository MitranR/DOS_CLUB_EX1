import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User, Doctor, Appointment, PasswordResetToken
from .schemas import (
    UserRegister, UserLogin, UserProfileUpdate, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest, DoctorResponse,
    AppointmentCreate, AppointmentResponse, MessageResponse
)
from .auth import (
    hash_password, verify_password, create_session_token,
    get_current_user_id_from_token, invalidate_token, generate_reset_token
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hospital Management System API",
    description="Backend API for Hospital Management, User Auth, Profiles, and Doctor Appointments",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency for Authenticated User ---
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing"
        )
    token = authorization.replace("Bearer ", "").strip()
    user_id = get_current_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please log in again."
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# --- Seed Doctors Helper ---
def seed_default_doctors():
    db = next(get_db())
    try:
        if db.query(Doctor).count() == 0:
            sample_doctors = [
                Doctor(
                    name="Dr. Sarah Jenkins",
                    specialty="Cardiology",
                    qualification="MBBS, MD, FACC",
                    experience_years=12,
                    available_days="Monday - Friday",
                    available_timings="09:00 AM - 01:00 PM",
                    room_number="Room 101",
                    max_slots_per_day=30,  # Max slot limit (25-40)
                    current_slots_booked=4,
                    is_available=True
                ),
                Doctor(
                    name="Dr. Rajesh Sharma",
                    specialty="Neurology",
                    qualification="MBBS, DM (Neurology)",
                    experience_years=15,
                    available_days="Monday - Saturday",
                    available_timings="10:00 AM - 02:00 PM",
                    room_number="Room 204",
                    max_slots_per_day=25,
                    current_slots_booked=6,
                    is_available=True
                ),
                Doctor(
                    name="Dr. Emily Chen",
                    specialty="Pediatrics",
                    qualification="MBBS, MD (Pediatrics)",
                    experience_years=9,
                    available_days="Monday - Friday",
                    available_timings="08:30 AM - 12:30 PM",
                    room_number="Room 108",
                    max_slots_per_day=35,
                    current_slots_booked=8,
                    is_available=True
                ),
                Doctor(
                    name="Dr. Michael Torres",
                    specialty="Orthopedics",
                    qualification="MBBS, MS (Orthopedics)",
                    experience_years=14,
                    available_days="Tuesday - Saturday",
                    available_timings="11:00 AM - 04:00 PM",
                    room_number="Room 302",
                    max_slots_per_day=40,
                    current_slots_booked=12,
                    is_available=True
                ),
                Doctor(
                    name="Dr. Priya Patel",
                    specialty="Dermatology",
                    qualification="MBBS, DVD, MD",
                    experience_years=8,
                    available_days="Monday - Friday",
                    available_timings="02:00 PM - 06:00 PM",
                    room_number="Room 115",
                    max_slots_per_day=28,
                    current_slots_booked=5,
                    is_available=True
                ),
                Doctor(
                    name="Dr. David Kim",
                    specialty="General Medicine",
                    qualification="MBBS, MD (Internal Medicine)",
                    experience_years=11,
                    available_days="Monday - Sunday",
                    available_timings="09:00 AM - 05:00 PM",
                    room_number="Room 102",
                    max_slots_per_day=40,
                    current_slots_booked=15,
                    is_available=True
                ),
            ]
            db.add_all(sample_doctors)
            db.commit()
    finally:
        db.close()

# Auto-seed on load
seed_default_doctors()


# ==========================================
# 1. AUTHENTICATION ENDPOINTS
# ==========================================

@app.post("/api/auth/register", response_model=MessageResponse)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    # Check if username exists
    if db.query(User).filter(User.username == payload.username.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose a different one."
        )

    # Check if email exists
    if db.query(User).filter(User.email == payload.email.strip().lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered. Please log in or use forgot password."
        )

    # Create new user
    hashed = hash_password(payload.password)
    user = User(
        username=payload.username.strip(),
        email=payload.email.strip().lower(),
        password_hash=hashed,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        address=payload.address,
        blood_group=payload.blood_group,
        emergency_contact=payload.emergency_contact
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return MessageResponse(
        message="Account created successfully! You can now log in.",
        success=True,
        data={"user_id": user.id, "username": user.username}
    )


@app.post("/api/auth/login")
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    username_or_email = payload.username.strip().lower()
    user = db.query(User).filter(
        (User.username == payload.username.strip()) | (User.email == username_or_email)
    ).first()

    if not user or not verify_password(user.password_hash, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    token = create_session_token(user.id, user.username)
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "address": user.address,
            "blood_group": user.blood_group,
            "emergency_contact": user.emergency_contact
        }
    }


@app.post("/api/auth/logout", response_model=MessageResponse)
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        invalidate_token(token)
    return MessageResponse(message="Successfully logged out", success=True)


@app.post("/api/auth/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    identifier = payload.identifier.strip().lower()
    user = db.query(User).filter(
        (User.username == payload.identifier.strip()) | (User.email == identifier)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with that username or email address."
        )

    # Invalidate old unused tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})

    # Create new reset token valid for 1 hour
    token = generate_reset_token()
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        is_used=False
    )
    db.add(reset_entry)
    db.commit()

    return {
        "success": True,
        "message": "Password reset token generated successfully. In production, this would be sent to your email.",
        "reset_token": token,
        "username": user.username
    }


@app.post("/api/auth/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == payload.token.strip(),
        PasswordResetToken.is_used == False
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token."
        )

    if datetime.datetime.utcnow() > reset_record.expires_at:
        reset_record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired. Please request a new one."
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Update password and mark token as used
    user.password_hash = hash_password(payload.new_password)
    reset_record.is_used = True
    db.commit()

    return MessageResponse(
        message="Password has been reset successfully! You can now log in with your new password.",
        success=True
    )


# ==========================================
# 2. USER PROFILE ENDPOINTS
# ==========================================

@app.get("/api/user/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/api/user/profile", response_model=UserResponse)
def update_user_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.email is not None and payload.email != current_user.email:
        # Check uniqueness of new email
        existing = db.query(User).filter(User.email == payload.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already used by another account."
            )
        current_user.email = payload.email
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number
    if payload.address is not None:
        current_user.address = payload.address
    if payload.blood_group is not None:
        current_user.blood_group = payload.blood_group
    if payload.emergency_contact is not None:
        current_user.emergency_contact = payload.emergency_contact

    db.commit()
    db.refresh(current_user)
    return current_user


# ==========================================
# 3. DOCTOR & AVAILABILITY ENDPOINTS
# ==========================================

@app.get("/api/doctors", response_model=List[DoctorResponse])
def list_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    results = []
    for d in doctors:
        remaining = max(0, d.max_slots_per_day - d.current_slots_booked)
        results.append(
            DoctorResponse(
                id=d.id,
                name=d.name,
                specialty=d.specialty,
                qualification=d.qualification,
                experience_years=d.experience_years,
                available_days=d.available_days,
                available_timings=d.available_timings,
                room_number=d.room_number,
                max_slots_per_day=d.max_slots_per_day,
                current_slots_booked=d.current_slots_booked,
                remaining_slots=remaining,
                is_available=(d.is_available and remaining > 0)
            )
        )
    return results


# ==========================================
# 4. APPOINTMENT BOOKING ENDPOINTS
# ==========================================

@app.post("/api/appointments/book", response_model=MessageResponse)
def book_appointment(
    payload: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found."
        )

    if not doctor.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{doctor.name} is currently not available for bookings."
        )

    # Check slot limit constraint (between 25 and 40 per doctor per day)
    if doctor.current_slots_booked >= doctor.max_slots_per_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All {doctor.max_slots_per_day} booking slots for {doctor.name} are fully booked today."
        )

    # Increment booked slots
    doctor.current_slots_booked += 1

    # Create appointment
    appt = Appointment(
        user_id=current_user.id,
        doctor_id=doctor.id,
        patient_name=payload.patient_name,
        contact_number=payload.contact_number,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
        status="Confirmed"
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    remaining_slots = doctor.max_slots_per_day - doctor.current_slots_booked
    return MessageResponse(
        message=f"Appointment booked successfully with {doctor.name} for {payload.appointment_date} at {payload.appointment_time}!",
        success=True,
        data={
            "appointment_id": appt.id,
            "doctor_name": doctor.name,
            "remaining_slots": remaining_slots
        }
    )


@app.get("/api/appointments/my", response_model=List[AppointmentResponse])
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appts = db.query(Appointment).filter(Appointment.user_id == current_user.id).order_by(Appointment.created_at.desc()).all()
    results = []
    for a in appts:
        results.append(
            AppointmentResponse(
                id=a.id,
                doctor_id=a.doctor_id,
                doctor_name=a.doctor.name if a.doctor else "Unknown Doctor",
                specialty=a.doctor.specialty if a.doctor else "General",
                patient_name=a.patient_name,
                contact_number=a.contact_number,
                appointment_date=a.appointment_date,
                appointment_time=a.appointment_time,
                reason=a.reason,
                status=a.status,
                created_at=a.created_at
            )
        )
    return results


# ==========================================
# 5. STATIC FILES MOUNT (SERVE FRONTEND)
# ==========================================
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Hospital Management API is running."}

    @app.get("/{page_name}.html")
    def serve_html_pages(page_name: str):
        file_path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="Page not found")
else:
    @app.get("/")
    def serve_root():
        return {"message": "Hospital Management API is running. Check /docs for interactive Swagger API documentation."}

