"""
Password Management Tests

Tests for password change, forgot password, and reset password endpoints
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


class TestPasswordChange:
    """Test /api/v1/auth/change-password endpoint"""

    endpoint = "/api/v1/auth/change-password"

    def test_successful_password_change(self, client, user_end_user, auth_headers_end_user, password_plain, db_session):
        """✅ Test successful password change"""
        new_password = "NewTestPass123!"

        response = client.patch(self.endpoint,
            headers=auth_headers_end_user,
            json={
                "old_password": password_plain,
                "new_password": new_password
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()["message"].lower()

        # Verify password was actually changed
        db_session.refresh(user_end_user)
        assert user_end_user.verify_password(new_password)

    def test_change_password_wrong_old_password(self, client, auth_headers_end_user):
        """❌ Test password change fails with wrong old password"""
        response = client.patch(self.endpoint,
            headers=auth_headers_end_user,
            json={
                "old_password": "WrongOldPassword123!",
                "new_password": "NewTestPass123!"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in response.json()["detail"].lower()

    def test_change_password_same_as_old(self, client, auth_headers_end_user, password_plain):
        """❌ Test password change fails when new password equals old"""
        response = client.patch(self.endpoint,
            headers=auth_headers_end_user,
            json={
                "old_password": password_plain,
                "new_password": password_plain
            }
        )

        # Should fail (implementation dependent)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_change_password_weak_new_password(self, client, auth_headers_end_user, password_plain):
        """❌ Test password change fails with weak new password"""
        response = client.patch(self.endpoint,
            headers=auth_headers_end_user,
            json={
                "old_password": password_plain,
                "new_password": "weak"
            }
        )

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_change_password_audit_log(self, client, db_session, user_end_user, auth_headers_end_user, password_plain):
        """✅ Test audit log is created on password change"""
        from models import AuditLog, AuditEventType

        response = client.patch(self.endpoint,
            headers=auth_headers_end_user,
            json={
                "old_password": password_plain,
                "new_password": "NewTestPass123!"
            }
        )

        assert response.status_code == status.HTTP_200_OK

        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == user_end_user.id,
            AuditLog.action_type == AuditEventType.PASSWORD_CHANGE
        ).first()

        assert audit_log is not None
        assert audit_log.status == "SUCCESS"


class TestForgotPassword:
    """Test /api/v1/auth/forgot-password endpoint"""

    endpoint = "/api/v1/auth/forgot-password"

    def test_forgot_password_valid_email(self, client, db_session, user_end_user, mock_email_service):
        """✅ Test forgot password with valid email"""
        response = client.post(self.endpoint, json={
            "email": user_end_user.email
        })

        assert response.status_code == status.HTTP_200_OK
        assert "sent" in response.json()["message"].lower()

        # Verify email was sent
        assert len(mock_email_service) > 0
        assert any("Reset" in email["subject"] for email in mock_email_service)

    def test_forgot_password_nonexistent_email(self, client, mock_email_service):
        """✅ Test forgot password with non-existent email (should still return success to prevent enumeration)"""
        response = client.post(self.endpoint, json={
            "email": "nonexistent@example.com"
        })

        # Should return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
        assert "sent" in response.json()["message"].lower() or "exists" in response.json()["message"].lower()

        # But no email should actually be sent
        # (Implementation may vary - some might still send to prevent timing attacks)

    def test_forgot_password_token_generation(self, client, db_session, user_end_user):
        """✅ Test reset token is generated and stored"""
        from models import PasswordReset

        response = client.post(self.endpoint, json={
            "email": user_end_user.email
        })

        assert response.status_code == status.HTTP_200_OK

        # Check token exists in database
        password_reset = db_session.query(PasswordReset).filter(
            PasswordReset.user_id == user_end_user.id,
            PasswordReset.is_used == False
        ).first()

        assert password_reset is not None
        assert password_reset.token_hash is not None

    def test_forgot_password_token_expiry(self, client, db_session, user_end_user):
        """✅ Test reset token has correct expiry (1 hour)"""
        from models import PasswordReset
        from config import get_settings

        settings = get_settings()
        response = client.post(self.endpoint, json={
            "email": user_end_user.email
        })

        assert response.status_code == status.HTTP_200_OK

        password_reset = db_session.query(PasswordReset).filter(
            PasswordReset.user_id == user_end_user.id
        ).first()

        expected_expiry = datetime.now(timezone.utc) + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        assert abs((password_reset.expires_at - expected_expiry).total_seconds()) < 5


class TestResetPassword:
    """Test /api/v1/auth/reset-password endpoint"""

    endpoint = "/api/v1/auth/reset-password"

    def test_successful_password_reset(self, client, db_session, user_end_user):
        """✅ Test successful password reset with valid token"""
        from models import PasswordReset
        from utils import generate_password_reset_token, hash_token

        # Create reset token
        reset_token = generate_password_reset_token()
        token_hash = hash_token(reset_token)

        password_reset = PasswordReset(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            ip_address="127.0.0.1"
        )
        db_session.add(password_reset)
        db_session.commit()

        new_password = "NewResetPass123!"
        response = client.post(self.endpoint, json={
            "token": reset_token,
            "new_password": new_password
        })

        assert response.status_code == status.HTTP_200_OK

        # Verify password was changed
        db_session.refresh(user_end_user)
        assert user_end_user.verify_password(new_password)

    def test_reset_password_expired_token(self, client, db_session, user_end_user):
        """❌ Test reset fails with expired token"""
        from models import PasswordReset
        from utils import generate_password_reset_token, hash_token

        reset_token = generate_password_reset_token()
        token_hash = hash_token(reset_token)

        password_reset = PasswordReset(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            ip_address="127.0.0.1"
        )
        db_session.add(password_reset)
        db_session.commit()

        response = client.post(self.endpoint, json={
            "token": reset_token,
            "new_password": "NewResetPass123!"
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "expired" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()

    def test_reset_password_already_used_token(self, client, db_session, user_end_user):
        """❌ Test reset fails with already used token"""
        from models import PasswordReset
        from utils import generate_password_reset_token, hash_token

        reset_token = generate_password_reset_token()
        token_hash = hash_token(reset_token)

        password_reset = PasswordReset(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            ip_address="127.0.0.1",
            is_used=True  # Already used
        )
        db_session.add(password_reset)
        db_session.commit()

        response = client.post(self.endpoint, json={
            "token": reset_token,
            "new_password": "NewResetPass123!"
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in response.json()["detail"].lower()

    def test_reset_password_invalid_token(self, client):
        """❌ Test reset fails with invalid token"""
        response = client.post(self.endpoint, json={
            "token": "invalid-token",
            "new_password": "NewResetPass123!"
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_audit_log(self, client, db_session, user_end_user):
        """✅ Test audit log is created on password reset"""
        from models import PasswordReset, AuditLog, AuditEventType
        from utils import generate_password_reset_token, hash_token

        reset_token = generate_password_reset_token()
        token_hash = hash_token(reset_token)

        password_reset = PasswordReset(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            ip_address="127.0.0.1"
        )
        db_session.add(password_reset)
        db_session.commit()

        response = client.post(self.endpoint, json={
            "token": reset_token,
            "new_password": "NewResetPass123!"
        })

        assert response.status_code == status.HTTP_200_OK

        # Check audit log
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == user_end_user.id,
            AuditLog.action_type == AuditEventType.PASSWORD_RESET_COMPLETE
        ).first()

        assert audit_log is not None
        assert audit_log.status == "SUCCESS"
