"""
Authentication Utility Functions

Helper functions for authentication, password management, and security.
Reference: /backend/auth/README.md - Security Features
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from uuid import UUID

from models import User, RefreshToken, UserSession, PasswordReset, AuditLog, AuditEventType
from config import get_settings


settings = get_settings()


# Timezone-aware datetime helper
def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


# ============================================================================
# Token Generation Utilities
# ============================================================================

def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token

    Args:
        length: Token length in bytes (will be URL-safe base64 encoded)

    Returns:
        Secure random token string
    """
    return secrets.token_urlsafe(length)


def generate_verification_token() -> str:
    """
    Generate email verification token

    Returns:
        Verification token string
    """
    return generate_secure_token(32)


def generate_password_reset_token() -> str:
    """
    Generate password reset token

    Returns:
        Password reset token string
    """
    return generate_secure_token(32)


def hash_token(token: str) -> str:
    """
    Hash token for secure storage

    Args:
        token: Token to hash

    Returns:
        SHA256 hash of token
    """
    return hashlib.sha256(token.encode()).hexdigest()


# ============================================================================
# Password Utilities
# ============================================================================

def generate_random_password(length: int = 16) -> str:
    """
    Generate secure random password

    Args:
        length: Password length (min 8)

    Returns:
        Random password string meeting complexity requirements
    """
    if length < 8:
        length = 8

    # Ensure password has required character types
    password_chars = []

    # At least one uppercase
    password_chars.append(secrets.choice(string.ascii_uppercase))

    # At least one lowercase
    password_chars.append(secrets.choice(string.ascii_lowercase))

    # At least one digit
    password_chars.append(secrets.choice(string.digits))

    # At least one special character
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    password_chars.append(secrets.choice(special_chars))

    # Fill remaining length with random mix
    all_chars = string.ascii_letters + string.digits + special_chars
    for _ in range(length - 4):
        password_chars.append(secrets.choice(all_chars))

    # Shuffle to avoid predictable pattern
    secrets.SystemRandom().shuffle(password_chars)

    return ''.join(password_chars)


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets strength requirements

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long"

    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if settings.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    if settings.PASSWORD_REQUIRE_SPECIAL:
        special_chars = set("!@#$%^&*(),.?\":{}|<>")
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

    return True, None


# ============================================================================
# Session Utilities
# ============================================================================

def create_session_token() -> str:
    """
    Create secure session token

    Returns:
        Session token string
    """
    return generate_secure_token(32)


def get_session_expiry() -> datetime:
    """
    Get default session expiration time

    Returns:
        Session expiration datetime
    """
    return utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


# ============================================================================
# Audit Log Utilities
# ============================================================================

def create_audit_log(
    db,
    user_id: Optional[UUID],
    action_type: str,
    status: str = "SUCCESS",
    severity: str = "INFO",
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[UUID] = None,
    details: Optional[Dict] = None
) -> AuditLog:
    """
    Create audit log entry

    Args:
        db: Database session
        user_id: User ID (can be None for anonymous actions)
        action_type: Type of action performed
        status: Action status (SUCCESS, FAILURE)
        severity: Log severity (INFO, WARNING, ERROR, CRITICAL)
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        old_values: Previous values (for updates)
        new_values: New values (for updates)
        ip_address: Client IP address
        user_agent: Client user agent
        session_id: Session ID
        details: Additional structured details

    Returns:
        Created AuditLog object

    Reference: /backend/auth/README.md - Audit Logging
    """
    audit_log = AuditLog(
        user_id=user_id,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        severity=severity,
        status=status,
        session_id=session_id,
        details=details
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def log_login_success(
    db,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[UUID] = None
) -> AuditLog:
    """Log successful login"""
    return create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.LOGIN_SUCCESS,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )


def log_login_failure(
    db,
    username: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    reason: str = "Invalid credentials"
) -> AuditLog:
    """Log failed login attempt"""
    return create_audit_log(
        db=db,
        user_id=None,  # User not authenticated
        action_type=AuditEventType.LOGIN_FAILED,
        status="FAILURE",
        severity="WARNING",
        resource_type="USER",
        old_values={"username": username, "reason": reason},
        ip_address=ip_address,
        user_agent=user_agent
    )


def log_logout(
    db,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[UUID] = None
) -> AuditLog:
    """Log user logout"""
    return create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.LOGOUT,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )


def log_password_change(
    db,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Log password change"""
    return create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.PASSWORD_CHANGE,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )


def log_account_locked(
    db,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Log account locked due to failed attempts"""
    return create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.ACCOUNT_LOCKED,
        status="SUCCESS",
        severity="WARNING",
        resource_type="USER",
        resource_id=user.id,
        new_values={
            "locked_until": user.account_locked_until.isoformat() if user.account_locked_until else None
        },
        ip_address=ip_address,
        user_agent=user_agent
    )


# ============================================================================
# Email Utilities (Placeholders for actual email service)
# ============================================================================

def send_verification_email(email: str, token: str) -> bool:
    """
    Send email verification email

    Args:
        email: User email address
        token: Verification token

    Returns:
        True if email sent successfully

    TODO: Implement actual email sending
    """
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/verify-email?token={token}"
    print(f"[EMAIL] Verification email to {email}: {verification_link}")
    # TODO: Integrate with email service (SendGrid, AWS SES, etc.)
    return True


def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email

    Args:
        email: User email address
        token: Password reset token

    Returns:
        True if email sent successfully

    TODO: Implement actual email sending
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/reset-password?token={token}"
    print(f"[EMAIL] Password reset email to {email}: {reset_link}")
    # TODO: Integrate with email service
    return True


def send_welcome_email(user: User) -> bool:
    """
    Send welcome email to new user

    Args:
        user: User object

    Returns:
        True if email sent successfully
    """
    print(f"[EMAIL] Welcome email to {user.email}")
    # TODO: Implement actual email sending
    return True


def send_account_locked_email(user: User) -> bool:
    """
    Send account locked notification email

    Args:
        user: User object

    Returns:
        True if email sent successfully
    """
    print(f"[EMAIL] Account locked email to {user.email}")
    # TODO: Implement actual email sending
    return True


# ============================================================================
# MFA Utilities
# ============================================================================

def generate_mfa_secret() -> str:
    """
    Generate MFA secret for TOTP

    Returns:
        Base32 encoded secret string
    """
    import pyotp
    return pyotp.random_base32()


def generate_mfa_qr_uri(user: User, secret: str) -> str:
    """
    Generate MFA QR code provisioning URI

    Args:
        user: User object
        secret: MFA secret

    Returns:
        Provisioning URI for QR code generation
    """
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=user.email,
        issuer_name=settings.MFA_ISSUER_NAME
    )


def verify_mfa_code(secret: str, code: str) -> bool:
    """
    Verify MFA code

    Args:
        secret: MFA secret
        code: 6-digit code to verify

    Returns:
        True if code is valid
    """
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 10) -> list[str]:
    """
    Generate MFA backup recovery codes

    Args:
        count: Number of backup codes to generate

    Returns:
        List of backup codes
    """
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # Format as XXXX-XXXX for readability
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    return codes


# ============================================================================
# Device Info Parsing
# ============================================================================

def parse_user_agent(user_agent: str) -> dict:
    """
    Parse user agent string to extract device info

    Args:
        user_agent: User agent string

    Returns:
        Dictionary with parsed device information
    """
    # Simple parsing - in production, use a library like user-agents
    info = {
        "raw": user_agent,
        "browser": "Unknown",
        "os": "Unknown",
        "device_type": "Desktop"
    }

    user_agent_lower = user_agent.lower()

    # Detect browser
    if "chrome" in user_agent_lower:
        info["browser"] = "Chrome"
    elif "firefox" in user_agent_lower:
        info["browser"] = "Firefox"
    elif "safari" in user_agent_lower:
        info["browser"] = "Safari"
    elif "edge" in user_agent_lower:
        info["browser"] = "Edge"

    # Detect OS
    if "windows" in user_agent_lower:
        info["os"] = "Windows"
    elif "mac" in user_agent_lower:
        info["os"] = "MacOS"
    elif "linux" in user_agent_lower:
        info["os"] = "Linux"
    elif "android" in user_agent_lower:
        info["os"] = "Android"
        info["device_type"] = "Mobile"
    elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        info["os"] = "iOS"
        info["device_type"] = "Mobile" if "iphone" in user_agent_lower else "Tablet"

    return info


# ============================================================================
# Time Utilities
# ============================================================================

def get_token_expiry_datetime(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    """
    Get expiration datetime from now

    Args:
        days: Days to add
        hours: Hours to add
        minutes: Minutes to add

    Returns:
        Expiration datetime
    """
    return utcnow() + timedelta(days=days, hours=hours, minutes=minutes)


def is_expired(expiry_datetime: datetime) -> bool:
    """
    Check if datetime has expired

    Args:
        expiry_datetime: Expiration datetime

    Returns:
        True if expired
    """
    return utcnow() >= expiry_datetime


# ============================================================================
# Data Sanitization
# ============================================================================

def sanitize_user_data(data: dict) -> dict:
    """
    Sanitize user data by removing sensitive fields

    Args:
        data: User data dictionary

    Returns:
        Sanitized data dictionary
    """
    sensitive_fields = [
        "password",
        "password_hash",
        "mfa_secret",
        "token",
        "refresh_token",
        "access_token"
    ]

    return {k: v for k, v in data.items() if k not in sensitive_fields}
