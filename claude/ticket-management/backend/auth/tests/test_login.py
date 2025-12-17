"""
Login and Logout Tests

Tests for /api/v1/auth/login and /api/v1/auth/logout endpoints
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


class TestLogin:
    """Test user login functionality"""

    endpoint = "/api/v1/auth/login"

    def test_successful_login_with_username(self, client, user_end_user, password_plain):
        """✅ Test successful login using username"""
        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] == 900  # 15 minutes in seconds

        # Verify user data
        assert "user" in data
        assert data["user"]["username"] == user_end_user.username
        assert data["user"]["email"] == user_end_user.email
        assert data["user"]["role"] == user_end_user.role.value

    def test_successful_login_with_email(self, client, user_end_user, password_plain):
        """✅ Test successful login using email"""
        response = client.post(self.endpoint, json={
            "username": user_end_user.email,  # Can use email as username
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == user_end_user.email

    def test_login_with_invalid_credentials(self, client, user_end_user):
        """❌ Test login fails with wrong password"""
        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": "WrongPassword123!"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_login_with_nonexistent_user(self, client):
        """❌ Test login fails with non-existent user"""
        response = client.post(self.endpoint, json={
            "username": "nonexistent_user",
            "password": "AnyPassword123!"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_login_with_inactive_account(self, client, user_inactive, password_plain):
        """❌ Test login fails with inactive account"""
        response = client.post(self.endpoint, json={
            "username": user_inactive.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"].lower()

    def test_login_with_locked_account(self, client, user_locked, password_plain):
        """❌ Test login fails with locked account"""
        response = client.post(self.endpoint, json={
            "username": user_locked.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "locked" in response.json()["detail"].lower()

    def test_account_lockout_after_max_failed_attempts(self, client, user_end_user, db_session):
        """✅ Test account locks after 5 failed login attempts"""
        from config import get_settings
        settings = get_settings()

        max_attempts = settings.MAX_FAILED_LOGIN_ATTEMPTS  # Should be 5

        # Make max_attempts failed login attempts
        for i in range(max_attempts):
            response = client.post(self.endpoint, json={
                "username": user_end_user.username,
                "password": "WrongPassword123!"
            })
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Next attempt should result in locked account
        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": "WrongPassword123!"
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "locked" in response.json()["detail"].lower()

        # Refresh user from database
        db_session.refresh(user_end_user)
        assert user_end_user.is_account_locked()
        assert user_end_user.account_locked_until is not None

    def test_failed_login_attempt_counter(self, client, user_end_user, db_session):
        """✅ Test failed login attempts are counted"""
        # Make 3 failed attempts
        for i in range(3):
            client.post(self.endpoint, json={
                "username": user_end_user.username,
                "password": "WrongPassword123!"
            })

        # Refresh user from database
        db_session.refresh(user_end_user)
        assert user_end_user.failed_login_attempts == 3

    def test_token_generation_includes_user_info(self, client, user_admin, password_plain):
        """✅ Test generated tokens include user information"""
        from jwt import decode_access_token

        response = client.post(self.endpoint, json={
            "username": user_admin.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK
        access_token = response.json()["access_token"]

        # Decode token and verify claims
        payload = decode_access_token(access_token)
        assert payload["sub"] == str(user_admin.id)
        assert payload["username"] == user_admin.username
        assert payload["email"] == user_admin.email
        assert payload["role"] == user_admin.role.value
        assert payload["type"] == "access"

    def test_session_creation_on_login(self, client, db_session, user_end_user, password_plain):
        """✅ Test user session is created on login"""
        from models import UserSession

        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK

        # Check session exists in database
        session = db_session.query(UserSession).filter(
            UserSession.user_id == user_end_user.id,
            UserSession.is_active == True
        ).first()

        assert session is not None
        assert session.ip_address is not None
        assert session.user_agent is not None

    def test_audit_log_entries_on_login(self, client, db_session, user_end_user, password_plain):
        """✅ Test audit log is created for successful login"""
        from models import AuditLog, AuditEventType

        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK

        # Check audit log exists
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == user_end_user.id,
            AuditLog.action_type == AuditEventType.LOGIN_SUCCESS
        ).first()

        assert audit_log is not None
        assert audit_log.status == "SUCCESS"
        assert audit_log.ip_address is not None

    def test_timezone_aware_timestamps(self, client, user_end_user, password_plain):
        """✅ Test timestamps are timezone-aware"""
        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check timestamp format (should include timezone)
        assert "created_at" in data["user"]
        assert "+00:00" in data["user"]["created_at"] or "Z" in data["user"]["created_at"]

    def test_login_resets_failed_attempts_counter(self, client, user_end_user, password_plain, db_session):
        """✅ Test successful login resets failed attempts counter"""
        # Make some failed attempts
        for i in range(3):
            client.post(self.endpoint, json={
                "username": user_end_user.username,
                "password": "WrongPassword123!"
            })

        db_session.refresh(user_end_user)
        assert user_end_user.failed_login_attempts == 3

        # Successful login
        response = client.post(self.endpoint, json={
            "username": user_end_user.username,
            "password": password_plain
        })

        assert response.status_code == status.HTTP_200_OK

        # Counter should be reset
        db_session.refresh(user_end_user)
        assert user_end_user.failed_login_attempts == 0


class TestLogout:
    """Test user logout functionality"""

    endpoint = "/api/v1/auth/logout"

    def test_successful_logout(self, client, user_end_user, auth_headers_end_user, refresh_token_end_user):
        """✅ Test successful logout"""
        response = client.post(self.endpoint,
            headers=auth_headers_end_user,
            json={"refresh_token": refresh_token_end_user}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()["message"].lower()

    def test_logout_revokes_refresh_token(self, client, db_session, user_end_user, auth_headers_end_user, refresh_token_end_user):
        """✅ Test logout revokes refresh token"""
        from models import RefreshToken
        from utils import hash_token

        # Store refresh token in database first
        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1"
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        # Logout
        response = client.post(self.endpoint,
            headers=auth_headers_end_user,
            json={"refresh_token": refresh_token_end_user}
        )

        assert response.status_code == status.HTTP_200_OK

        # Check token is revoked
        db_session.refresh(refresh_token_obj)
        assert refresh_token_obj.is_revoked is True

    def test_logout_terminates_sessions(self, client, db_session, user_end_user, auth_headers_end_user):
        """✅ Test logout terminates user sessions"""
        from models import UserSession

        # Create active session
        session = UserSession(
            user_id=user_end_user.id,
            session_token="test-session-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        db_session.add(session)
        db_session.commit()

        # Logout
        response = client.post(self.endpoint, headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_200_OK

        # Check session is terminated
        db_session.refresh(session)
        assert session.is_active is False
        assert session.end_reason is not None

    def test_logout_without_token_fails(self, client):
        """❌ Test logout without authentication token fails"""
        response = client.post(self.endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_invalid_token_fails(self, client):
        """❌ Test logout with invalid token fails"""
        response = client.post(self.endpoint, headers={
            "Authorization": "Bearer invalid-token"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_audit_log_on_logout(self, client, db_session, user_end_user, auth_headers_end_user):
        """✅ Test audit log is created on logout"""
        from models import AuditLog, AuditEventType

        response = client.post(self.endpoint, headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_200_OK

        # Check audit log exists
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == user_end_user.id,
            AuditLog.action_type == AuditEventType.LOGOUT
        ).first()

        assert audit_log is not None
        assert audit_log.status == "SUCCESS"
