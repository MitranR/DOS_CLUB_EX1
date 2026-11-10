import hashlib
import hmac
import secrets
import datetime
from typing import Optional, Dict

# In-memory session store: token -> {"user_id": int, "username": str, "expires_at": datetime}
ACTIVE_SESSIONS: Dict[str, dict] = {}
SESSION_DURATION_HOURS = 24

def hash_password(password: str) -> str:
    """Hash password using PBKDF2 HMAC SHA-256 with a unique random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against provided plaintext password."""
    try:
        salt, key_hex = stored_password.split('$')
        computed_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return hmac.compare_digest(computed_key.hex(), key_hex)
    except Exception:
        return False

def create_session_token(user_id: int, username: str) -> str:
    """Generate a cryptographically secure session token."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=SESSION_DURATION_HOURS)
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "username": username,
        "expires_at": expires_at
    }
    return token

def get_current_user_id_from_token(token: Optional[str]) -> Optional[int]:
    """Retrieve user_id from session token if valid and unexpired."""
    if not token or token not in ACTIVE_SESSIONS:
        return None
    session = ACTIVE_SESSIONS[token]
    if datetime.datetime.utcnow() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        return None
    return session["user_id"]

def invalidate_token(token: str):
    """Remove session token upon logout."""
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]

def generate_reset_token() -> str:
    """Generate a URL-safe password reset token."""
    return secrets.token_urlsafe(24)

