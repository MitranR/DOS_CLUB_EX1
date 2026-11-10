from fastapi import FastAPI
from backend.main import configure_app

app = FastAPI(
    title="Hospital Management System API",
    description="Backend API for Hospital Management, User Auth, Profiles, and Doctor Appointments",
    version="1.0.0"
)
configure_app(app)
