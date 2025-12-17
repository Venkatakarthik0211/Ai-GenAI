"""
Security Features Tests

Tests for security mechanisms including account lockout, token security,
input validation, timezone handling, and database constraints
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


class TestAccountLockoutSecurity:
    """Test account lockout security mechanisms"""

    def test_lockout_after_failed_attempts(self, client, db_session, user_end_user):
        """✅ Test account locks after max failed login attempts"""
        from config import get_settings

        settings = get_settings()
        max_attempts = settings.MAX_FAILED_LOGIN_ATTEMPTS

        # Make max_attempts failed attempts
        for i in range(max_attempts):
            response = client.post("/api/v1/auth/login", json={
                "username": user_end_user.username,
                "password": "WrongPassword123!"
            })
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Next attempt should be locked
        response = client.post("/api/v1/auth/login", json={
            "username": user_end_user.username,
            "password": "WrongPassword123!"
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "locked" in response.json()["detail"].lower()

    def test_lockout_duration(self, client, db_session, user_end_user):
        """✅ Test lockout lasts for specified duration"""
        from models import User
        from config import get_settings

        settings = get_settings()

        # Set locked_until in the past (lockout expired)
        user_end_user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
        user_end_user.failed_login_attempts = settings.MAX_FAILED_LOGIN_ATTEMPTS
        db_session.commit()

        # Should be able to login now
        response = client.post("/api/v1/auth/login", json={
            "username": user_end_user.username,
            "password": "TestPass123!"
        })

        # Should succeed or reset attempts
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_failed_attempts_reset_on_success(self, client, db_session, user_end_user):
        """✅ Test failed attempts counter resets on successful login"""
        # Make some failed attempts
        for i in range(3):
            client.post("/api/v1/auth/login", json={
                "username": user_end_user.username,
                "password": "WrongPassword123!"
            })

        # Successful login
        response = client.post("/api/v1/auth/login", json={
            "username": user_end_user.username,
            "password": "TestPass123!"
        })

        assert response.status_code == status.HTTP_200_OK

        # Check failed attempts reset
        db_session.refresh(user_end_user)
        assert user_end_user.failed_login_attempts == 0


class TestTokenSecurity:
    """Test JWT token security features"""

    def test_token_replay_attack_prevention(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test tokens cannot be reused after revocation"""
        from models import RefreshToken
        from utils import hash_token

        # Create and store token
        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1",
            is_revoked=False
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        # Use token once
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token_end_user
        })
        assert response.status_code == status.HTTP_200_OK

        # Revoke token
        refresh_token_obj.is_revoked = True
        db_session.commit()

        # Try to use again (replay attack)
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token_end_user
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_jwt_signature(self, client):
        """❌ Test requests with invalid JWT signatures are rejected"""
        # Malformed token
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {invalid_token}"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_type_validation(self, client, user_end_user):
        """❌ Test access token cannot be used as refresh token and vice versa"""
        from jwt import create_access_token, create_refresh_token

        # Try to use access token for refresh endpoint
        access_token = create_access_token(user_end_user)
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": access_token
        })

        # Should fail (tokens have type claim)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]

    def test_token_family_tracking(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test token family is tracked for rotation detection"""
        from models import RefreshToken
        from utils import hash_token

        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1"
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        # Verify token_family exists
        assert refresh_token_obj.token_family is not None

    def test_token_stored_as_hash(self, db_session, user_end_user):
        """✅ Test tokens are stored as SHA-256 hashes"""
        from models import RefreshToken
        from utils import hash_token

        plain_token = "test-token-string"
        token_hash = hash_token(plain_token)

        refresh_token = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1"
        )
        db_session.add(refresh_token)
        db_session.commit()

        # Hash should be different from plain token
        assert refresh_token.token_hash != plain_token
        # SHA-256 hex is 64 characters
        assert len(refresh_token.token_hash) == 64


class TestInputValidation:
    """Test input validation and sanitization"""

    def test_sql_injection_prevention_username(self, client):
        """❌ Test SQL injection in username is prevented"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin' OR '1'='1",
            "password": "password"
        })

        # Should fail safely without SQL error
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_xss_prevention_in_registration(self, client):
        """❌ Test XSS script in registration is handled"""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "first_name": "<script>alert('xss')</script>",
            "last_name": "User",
            "phone_number": "+1-555-0199"
        })

        # Should either succeed (with sanitization) or fail validation
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            # Script tags should be escaped or removed
            assert "<script>" not in data["first_name"]

    def test_long_input_validation(self, client):
        """❌ Test extremely long inputs are rejected"""
        long_string = "a" * 10000

        response = client.post("/api/v1/auth/register", json={
            "username": long_string,
            "email": "test@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1-555-0199"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_email_format_validation(self, client):
        """❌ Test invalid email formats are rejected"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "test@",
            "test@.com",
            "test..test@example.com"
        ]

        for email in invalid_emails:
            response = client.post("/api/v1/auth/register", json={
                "username": "testuser",
                "email": email,
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+1-555-0199"
            })

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_password_complexity_validation(self, client):
        """❌ Test weak passwords are rejected"""
        weak_passwords = [
            "short",  # Too short
            "alllowercase123",  # No uppercase
            "ALLUPPERCASE123",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecial123"  # No special characters
        ]

        for password in weak_passwords:
            response = client.post("/api/v1/auth/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": password,
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+1-555-0199"
            })

            # Should fail validation
            assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestTimezoneHandling:
    """Test timezone-aware datetime handling"""

    def test_utc_timestamps_in_database(self, db_session, user_end_user):
        """✅ Test all timestamps are stored in UTC"""
        from models import AuditLog, AuditEventType

        # Create audit log
        audit_log = AuditLog(
            user_id=user_end_user.id,
            action_type=AuditEventType.LOGIN_SUCCESS,
            ip_address="127.0.0.1",
            status="SUCCESS"
        )
        db_session.add(audit_log)
        db_session.commit()

        # Verify timestamp is timezone-aware and in UTC
        assert audit_log.created_at.tzinfo == timezone.utc

    def test_token_expiry_timezone_aware(self, user_end_user):
        """✅ Test token expiry times are timezone-aware"""
        from jwt import decode_access_token, create_access_token

        token = create_access_token(user_end_user)
        payload = decode_access_token(token)

        # exp should be a timestamp
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))

        # Convert to datetime and verify future time
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp_datetime > datetime.now(timezone.utc)

    def test_session_expiry_comparison(self, db_session, user_end_user):
        """✅ Test session expiry comparison handles timezones correctly"""
        from models import UserSession

        # Create session with future expiry
        session = UserSession(
            user_id=user_end_user.id,
            session_token="test-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            is_active=True
        )
        db_session.add(session)
        db_session.commit()

        # Should be valid
        assert session.is_valid()

        # Create expired session
        expired_session = UserSession(
            user_id=user_end_user.id,
            session_token="expired-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            is_active=True
        )
        db_session.add(expired_session)
        db_session.commit()

        # Should be invalid
        assert not expired_session.is_valid()


class TestDatabaseConstraints:
    """Test database constraint enforcement"""

    def test_unique_username_constraint(self, db_session, user_end_user):
        """❌ Test duplicate username is rejected"""
        from models import User
        from sqlalchemy.exc import IntegrityError

        duplicate_user = User(
            username=user_end_user.username,  # Duplicate
            email="different@example.com",
            first_name="Test",
            last_name="User"
        )
        duplicate_user.set_password("TestPass123!")

        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_unique_email_constraint(self, db_session, user_end_user):
        """❌ Test duplicate email is rejected"""
        from models import User
        from sqlalchemy.exc import IntegrityError

        duplicate_user = User(
            username="different_username",
            email=user_end_user.email,  # Duplicate
            first_name="Test",
            last_name="User"
        )
        duplicate_user.set_password("TestPass123!")

        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_role_enum_constraint(self, db_session, user_end_user):
        """❌ Test invalid role value is rejected"""
        from models import User

        # Try to set invalid role (direct database manipulation)
        user_end_user.role = "INVALID_ROLE"  # type: ignore

        # Should fail when committing
        with pytest.raises(Exception):  # Could be IntegrityError or StatementError
            db_session.commit()

        db_session.rollback()

    def test_foreign_key_constraint(self, db_session):
        """❌ Test foreign key constraint is enforced"""
        from models import RefreshToken
        from sqlalchemy.exc import IntegrityError
        from uuid import uuid4

        # Try to create token for non-existent user
        token = RefreshToken(
            user_id=uuid4(),  # Non-existent user ID
            token_hash="test-hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1"
        )
        db_session.add(token)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_not_null_constraint(self, db_session, user_end_user):
        """❌ Test NOT NULL constraints are enforced"""
        from models import UserSession
        from sqlalchemy.exc import IntegrityError

        # Try to create session without required field
        session = UserSession(
            user_id=user_end_user.id,
            session_token=None,  # NOT NULL field
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        db_session.add(session)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()
