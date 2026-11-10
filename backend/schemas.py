from typing import Optional, List
from pydantic import BaseModel
import datetime

# --- Authentication Schemas ---

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    identifier: str  # username or email

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- User Profile Schemas ---

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

    class Config:
        from_attributes = True

# --- Doctor Schemas ---

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    qualification: str
    experience_years: int
    available_days: str
    available_timings: str
    room_number: str
    max_slots_per_day: int
    current_slots_booked: int
    remaining_slots: int
    is_available: bool

    class Config:
        from_attributes = True

# --- Appointment Schemas ---

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_name: str
    contact_number: str
    appointment_date: str
    appointment_time: str
    reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    doctor_name: str
    specialty: str
    patient_name: str
    contact_number: str
    appointment_date: str
    appointment_time: str
    reason: Optional[str] = None
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Generic Response ---

class MessageResponse(BaseModel):
    message: str
    success: bool
    data: Optional[dict] = None
