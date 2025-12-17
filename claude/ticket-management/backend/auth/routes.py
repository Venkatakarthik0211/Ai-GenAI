"""
Authentication API Routes

FastAPI routes for authentication endpoints.
Reference: /backend/auth/README.md - API Endpoints
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from models import User, UserRole, RefreshToken, UserSession, PasswordReset, AuditEventType, AuditLog
from schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    LogoutRequest,
    PasswordChangeRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
    SessionResponse,
    SessionListResponse,
)
from jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_access_token_expires_in,
    create_token_pair,
)
from dependencies import (
    get_db,
    get_current_user,
    get_current_active_user,
    get_client_ip,
    get_user_agent,
    require_admin,
)
from utils import (
    generate_password_reset_token,
    hash_token,
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
    generate_verification_token,
    create_session_token,
    get_session_expiry,
    log_login_success,
    log_login_failure,
    log_logout,
    log_password_change,
    log_account_locked,
    create_audit_log,
)
from config import get_settings


settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Timezone-aware datetime helper
def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


# ============================================================================
# User Registration
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - Creates new user account
    - Sends verification email if enabled
    - Returns user data (excluding password)

    Reference: /backend/auth/README.md - User Registration
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        department=user_data.department,
        role=UserRole.END_USER,  # Default role
    )
    user.set_password(user_data.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email if required
    if settings.EMAIL_VERIFICATION_REQUIRED:
        verification_token = generate_verification_token()
        # TODO: Store verification token in database
        send_verification_email(user.email, verification_token)
    else:
        user.is_email_verified = True
        db.commit()

    # Send welcome email
    send_welcome_email(user)

    # Log registration
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.ACCOUNT_CREATED,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return UserResponse.model_validate(user)


# ============================================================================
# User Login
# ============================================================================

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User login

    - Validates credentials
    - Returns access and refresh tokens
    - Creates user session

    Reference: /backend/auth/README.md - User Login
    """
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)

    # Find user by username or email
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()

    if not user:
        log_login_failure(db, login_data.username, ip_address, user_agent, "User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check if account is locked
    if user.is_account_locked():
        log_login_failure(db, login_data.username, ip_address, user_agent, "Account locked")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {user.account_locked_until.isoformat()}"
        )

    # Verify password
    if not user.verify_password(login_data.password):
        # Record failed attempt
        user.record_login_failure(
            max_attempts=settings.MAX_FAILED_LOGIN_ATTEMPTS,
            lockout_minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES
        )
        db.commit()

        if user.is_account_locked():
            log_account_locked(db, user, ip_address, user_agent)

        log_login_failure(db, login_data.username, ip_address, user_agent, "Invalid password")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check if user is active
    if not user.is_active:
        log_login_failure(db, login_data.username, ip_address, user_agent, "Account inactive")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create tokens
    access_token, refresh_token_str = create_token_pair(user)

    # Store refresh token in database
    refresh_token_expiry = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token_str),
        expires_at=refresh_token_expiry,
        user_agent=user_agent,
        ip_address=ip_address
    )
    db.add(refresh_token)

    # Create user session
    session = UserSession(
        user_id=user.id,
        session_token=create_session_token(),
        refresh_token_id=refresh_token.id,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=get_session_expiry()
    )
    db.add(session)

    # Update user login info
    user.record_login_success()
    db.commit()

    # Log successful login
    log_login_success(db, user, ip_address, user_agent, session.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=get_access_token_expires_in(),
        user=UserResponse.model_validate(user)
    )


# ============================================================================
# Token Refresh
# ============================================================================

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    - Validates refresh token
    - Issues new access token
    - Optionally rotates refresh token

    Reference: /backend/auth/README.md - Token Refresh
    """
    try:
        # Decode refresh token
        payload = decode_refresh_token(refresh_data.refresh_token)
        user_id = payload.get("sub")

        # Check token in database
        token_hash = hash_token(refresh_data.refresh_token)
        stored_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        ).first()

        if not stored_token or not stored_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Get user
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        new_access_token = create_access_token(user)

        # Update token last used time
        stored_token.update_last_used()
        db.commit()

        return TokenRefreshResponse(
            access_token=new_access_token,
            refresh_token=refresh_data.refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=get_access_token_expires_in()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        ) from e


# ============================================================================
# User Logout
# ============================================================================

@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    logout_data: Optional[LogoutRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User logout

    - Revokes refresh token
    - Terminates user session
    - Logs logout event

    Reference: /backend/auth/README.md - User Logout
    """
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)

    # Revoke refresh token if provided
    if logout_data and logout_data.refresh_token:
        token_hash = hash_token(logout_data.refresh_token)
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == current_user.id
        ).first()

        if refresh_token:
            refresh_token.revoke()

    # Terminate all active sessions for this user (or specific session)
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).all()

    for session in active_sessions:
        session.terminate()

    db.commit()

    # Log logout
    log_logout(db, current_user, ip_address, user_agent)

    return MessageResponse(message="Successfully logged out")


# ============================================================================
# Get Current User Profile
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile

    Requires: Valid access token
    """
    return UserResponse.model_validate(current_user)


# ============================================================================
# Update User Profile
# ============================================================================

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile

    Requires: Valid access token
    """
    # Update user fields
    if user_update.first_name:
        current_user.first_name = user_update.first_name
    if user_update.last_name:
        current_user.last_name = user_update.last_name
    if user_update.phone_number:
        current_user.phone_number = user_update.phone_number
    if user_update.department:
        current_user.department = user_update.department

    current_user.updated_at = utcnow()

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


# ============================================================================
# Change Password
# ============================================================================

@router.patch("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password

    - Requires old password verification
    - Updates password hash
    - Logs password change

    Requires: Valid access token
    """
    # Verify old password
    if not current_user.verify_password(password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )

    # Set new password
    current_user.set_password(password_data.new_password)
    current_user.updated_at = utcnow()

    db.commit()

    # Log password change
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    log_password_change(db, current_user, ip_address, user_agent)

    return MessageResponse(message="Password changed successfully")


# ============================================================================
# Forgot Password
# ============================================================================

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request password reset

    - Generates reset token
    - Sends reset email
    - Token expires in 1 hour

    Reference: /backend/auth/README.md - Password Reset
    """
    # Find user by email
    user = db.query(User).filter(User.email == forgot_data.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return MessageResponse(message="If the email exists, a password reset link has been sent")

    # Generate reset token
    reset_token = generate_password_reset_token()
    token_hash = hash_token(reset_token)

    # Store reset token
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)

    password_reset = PasswordReset(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(password_reset)
    db.commit()

    # Send reset email
    send_password_reset_email(user.email, reset_token)

    # Log password reset request
    create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.PASSWORD_RESET_REQUEST,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return MessageResponse(message="If the email exists, a password reset link has been sent")


# ============================================================================
# Reset Password
# ============================================================================

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Reset password with token

    - Validates reset token
    - Updates password
    - Invalidates token

    Reference: /backend/auth/README.md - Password Reset
    """
    # Find valid reset token
    token_hash = hash_token(reset_data.token)
    password_reset = db.query(PasswordReset).filter(
        PasswordReset.token_hash == token_hash,
        PasswordReset.is_used == False
    ).first()

    if not password_reset or not password_reset.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Get user
    user = db.query(User).filter(User.id == password_reset.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.set_password(reset_data.new_password)
    user.updated_at = utcnow()

    # Mark token as used
    password_reset.mark_as_used()

    db.commit()

    # Log password reset completion
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=user.id,
        action_type=AuditEventType.PASSWORD_RESET_COMPLETE,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return MessageResponse(message="Password reset successfully")


# ============================================================================
# List User Sessions
# ============================================================================

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all active sessions for current user

    Requires: Valid access token
    """
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).all()

    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=len(sessions)
    )


# ============================================================================
# Terminate Session
# ============================================================================

@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def terminate_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Terminate specific session

    Requires: Valid access token
    """
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session.terminate()
    db.commit()

    return MessageResponse(message="Session terminated successfully")


# ============================================================================
# Admin: User Management
# ============================================================================

@router.get("/admin/users", response_model=list[UserResponse])
async def list_all_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)

    Supports filtering by:
    - role: Filter by user role
    - is_active: Filter by active status
    - search: Search username, email, or name

    Requires: ADMIN role
    """
    query = db.query(User).filter(User.deleted_at == None)

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern))
        )

    users = query.order_by(User.created_at.desc()).all()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_admin(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only)

    Requires: ADMIN role
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at == None
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: UUID,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user (Admin only)

    Can update:
    - Profile information
    - Role
    - Active status

    Requires: ADMIN role
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at == None
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields
    if user_update.first_name:
        user.first_name = user_update.first_name
    if user_update.last_name:
        user.last_name = user_update.last_name
    if user_update.phone_number:
        user.phone_number = user_update.phone_number
    if user_update.department:
        user.department = user_update.department

    user.updated_at = utcnow()

    db.commit()
    db.refresh(user)

    # Log admin action
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=AuditEventType.USER_UPDATED,
        status="SUCCESS",
        severity="INFO",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"updated_user_id": str(user.id), "updated_by": "admin"}
    )

    return UserResponse.model_validate(user)


@router.patch("/admin/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    role_data: dict,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role (Admin only)

    Request body:
    {
        "role": "DEVOPS_ENGINEER" | "TEAM_LEAD" | "MANAGER" | etc.
    }

    Requires: ADMIN role
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at == None
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_role = role_data.get("role")
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role is required"
        )

    try:
        user.role = UserRole(new_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {new_role}"
        )

    user.updated_at = utcnow()
    db.commit()
    db.refresh(user)

    # Log role change
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=AuditEventType.ROLE_CHANGED,
        status="SUCCESS",
        severity="WARN",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"user_id": str(user.id), "new_role": new_role}
    )

    return UserResponse.model_validate(user)


@router.patch("/admin/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: UUID,
    status_data: dict,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user status (Admin only)

    Request body:
    {
        "is_active": true | false
    }

    Requires: ADMIN role
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at == None
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if "is_active" in status_data:
        user.is_active = status_data["is_active"]
        user.updated_at = utcnow()

        db.commit()
        db.refresh(user)

        # Log status change
        ip_address = await get_client_ip(request)
        user_agent = await get_user_agent(request)
        action_type = AuditEventType.ACCOUNT_ENABLED if user.is_active else AuditEventType.ACCOUNT_DISABLED
        create_audit_log(
            db=db,
            user_id=current_user.id,
            action_type=action_type,
            status="SUCCESS",
            severity="WARN",
            resource_type="USER",
            resource_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"user_id": str(user.id), "is_active": user.is_active}
        )

    return UserResponse.model_validate(user)


@router.delete("/admin/users/{user_id}", response_model=MessageResponse)
async def delete_user_admin(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Soft delete user (Admin only)

    Marks user as deleted without removing from database.

    Requires: ADMIN role
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at == None
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete
    user.deleted_at = utcnow()
    user.is_active = False

    # Revoke all refresh tokens
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id
    ).update({"is_revoked": True})

    # Terminate all sessions
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).update({"is_active": False, "ended_at": utcnow(), "end_reason": "revoked"})

    db.commit()

    # Log deletion
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=AuditEventType.ACCOUNT_DELETED,
        status="SUCCESS",
        severity="ERROR",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"deleted_user_id": str(user.id)}
    )

    return MessageResponse(message="User deleted successfully")


# ============================================================================
# Admin: Token Management
# ============================================================================

@router.get("/admin/tokens/user/{user_id}")
async def list_user_tokens(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all refresh tokens for a user (Admin only)

    Shows active and revoked tokens with device information.

    Requires: ADMIN role
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).order_by(RefreshToken.created_at.desc()).all()

    return {
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        },
        "tokens": [
            {
                "id": str(token.id),
                "created_at": token.created_at.isoformat(),
                "expires_at": token.expires_at.isoformat(),
                "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
                "is_revoked": token.is_revoked,
                "device_type": token.device_type,
                "device_name": token.device_name,
                "user_agent": token.user_agent,
                "ip_address": token.ip_address,
                "location": token.location,
                "is_valid": token.is_valid()
            }
            for token in tokens
        ],
        "total": len(tokens),
        "active_tokens": sum(1 for t in tokens if t.is_valid())
    }


@router.delete("/admin/tokens/{token_id}", response_model=MessageResponse)
async def revoke_token_admin(
    token_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Revoke a specific refresh token (Admin only)

    Requires: ADMIN role
    """
    token = db.query(RefreshToken).filter(RefreshToken.id == token_id).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )

    token.revoke()
    db.commit()

    # Log token revocation
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=AuditEventType.TOKEN_REVOKED,
        status="SUCCESS",
        severity="WARN",
        resource_type="TOKEN",
        resource_id=token.id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"token_user_id": str(token.user_id), "revoked_by": "admin"}
    )

    return MessageResponse(message="Token revoked successfully")


@router.delete("/admin/tokens/user/{user_id}/revoke-all", response_model=MessageResponse)
async def revoke_all_user_tokens(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Revoke all refresh tokens for a user (Admin only)

    Useful for security incidents or forcing user re-authentication.

    Requires: ADMIN role
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Revoke all tokens
    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})

    # Terminate all sessions
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).update({"is_active": False, "ended_at": utcnow(), "end_reason": "revoked"})

    db.commit()

    # Log bulk revocation
    ip_address = await get_client_ip(request)
    user_agent = await get_user_agent(request)
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=AuditEventType.TOKENS_REVOKED,
        status="SUCCESS",
        severity="ERROR",
        resource_type="USER",
        resource_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"target_user_id": str(user_id), "tokens_revoked": count}
    )

    return MessageResponse(message=f"Revoked {count} tokens and terminated all sessions")


# ============================================================================
# Admin: Audit Logs
# ============================================================================

@router.get("/admin/audit-logs")
async def get_audit_logs(
    user_id: Optional[UUID] = None,
    action_type: Optional[AuditEventType] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs (Admin only)

    Supports filtering by:
    - user_id: Filter by specific user
    - action_type: Filter by action type
    - from_date: Start date
    - to_date: End date

    Requires: ADMIN role
    """
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if action_type:
        query = query.filter(AuditLog.action_type == action_type)

    if from_date:
        query = query.filter(AuditLog.created_at >= from_date)

    if to_date:
        query = query.filter(AuditLog.created_at <= to_date)

    total = query.count()

    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "logs": [
            {
                "id": str(log.id),
                "user": {
                    "id": str(log.user.id),
                    "username": log.user.username,
                    "email": log.user.email
                } if log.user else None,
                "action_type": log.action_type,
                "status": log.status,
                "severity": log.severity,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }
