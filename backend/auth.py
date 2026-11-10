import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional, Set

SESSION_DURATION_SECONDS = 24 * 60 * 60
SECRET_KEY = os.environ.get("SECRET_KEY", "citycare-hospital-secret-key-2026").encode("utf-8")
REVOKED_TOKENS: Set[str] = set()


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
    """Generate a stateless HMAC-SHA256 signed session token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": int(time.time()) + SESSION_DURATION_SECONDS
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
    signature = hmac.new(SECRET_KEY, payload_b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def get_current_user_id_from_token(token: Optional[str]) -> Optional[int]:
    """Verify signed session token and retrieve user_id if valid and unexpired."""
    if not token or token in REVOKED_TOKENS:
        return None
    try:
        payload_b64, signature = token.split(".", 1)
        expected_sig = hmac.new(SECRET_KEY, payload_b64.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None

        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8"))
        if int(time.time()) > payload.get("exp", 0):
            return None
        return payload.get("user_id")
    except Exception:
        return None


def invalidate_token(token: str):
    """Record token revocation upon logout."""
    if token:
        REVOKED_TOKENS.add(token)


def generate_reset_token() -> str:
    """Generate a URL-safe password reset token."""
    return secrets.token_urlsafe(24)
