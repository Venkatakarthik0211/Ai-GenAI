"""
Session Management Tests

Tests for /api/v1/auth/sessions endpoints
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


class TestSessionManagement:
    """Test session management endpoints"""

    list_endpoint = "/api/v1/auth/sessions"

    def test_list_active_sessions(self, client, db_session, user_end_user, auth_headers_end_user):
        """✅ Test listing active sessions"""
        from models import UserSession

        # Create test sessions
        session1 = UserSession(
            user_id=user_end_user.id,
            session_token="token1",
            ip_address="192.168.1.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        session2 = UserSession(
            user_id=user_end_user.id,
            session_token="token2",
            ip_address="192.168.1.2",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        db_session.add_all([session1, session2])
        db_session.commit()

        response = client.get(self.list_endpoint, headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "sessions" in data
        assert data["total"] >= 2

    def test_session_creation_with_device_info(self, client, db_session, user_end_user, password_plain):
        """✅ Test session stores device information"""
        from models import UserSession

        # Login to create session
        response = client.post("/api/v1/auth/login",
            json={"username": user_end_user.username, "password": password_plain},
            headers={"User-Agent": "Test Browser/1.0"}
        )

        assert response.status_code == status.HTTP_200_OK

        # Check session has device info
        session = db_session.query(UserSession).filter(
            UserSession.user_id == user_end_user.id,
            UserSession.is_active == True
        ).first()

        assert session is not None
        assert session.user_agent is not None
        assert session.ip_address is not None

    def test_terminate_specific_session(self, client, db_session, user_end_user, auth_headers_end_user):
        """✅ Test terminating a specific session"""
        from models import UserSession

        session = UserSession(
            user_id=user_end_user.id,
            session_token="test-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        db_session.add(session)
        db_session.commit()

        response = client.delete(
            f"{self.list_endpoint}/{session.id}",
            headers=auth_headers_end_user
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify session is terminated
        db_session.refresh(session)
        assert session.is_active is False

    def test_session_expiry(self, client, db_session, user_end_user):
        """✅ Test expired sessions are not active"""
        from models import UserSession

        expired_session = UserSession(
            user_id=user_end_user.id,
            session_token="expired-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired
            is_active=True
        )
        db_session.add(expired_session)
        db_session.commit()

        # Check is_valid method returns False for expired
        assert not expired_session.is_valid()

    def test_max_sessions_per_user(self, client, db_session, user_end_user):
        """✅ Test maximum sessions per user limit (5)"""
        from models import UserSession
        from config import get_settings

        settings = get_settings()
        max_sessions = settings.MAX_SESSIONS_PER_USER

        # Create max + 1 sessions
        for i in range(max_sessions + 1):
            session = UserSession(
                user_id=user_end_user.id,
                session_token=f"token{i}",
                ip_address="127.0.0.1",
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                is_active=True
            )
            db_session.add(session)
            db_session.commit()

        # Count active sessions
        active_count = db_session.query(UserSession).filter(
            UserSession.user_id == user_end_user.id,
            UserSession.is_active == True
        ).count()

        # Should not exceed max (oldest should be terminated)
        assert active_count <= max_sessions

    def test_end_reason_tracking(self, client, db_session, user_end_user):
        """✅ Test session end_reason is tracked correctly"""
        from models import UserSession

        session = UserSession(
            user_id=user_end_user.id,
            session_token="test-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        db_session.add(session)
        db_session.commit()

        # Terminate with specific reason
        session.terminate(reason="logout")
        db_session.commit()

        db_session.refresh(session)
        assert session.end_reason == "logout"
        assert session.ended_at is not None

    def test_last_activity_tracking(self, client, db_session, user_end_user):
        """✅ Test last_activity_at is updated"""
        from models import UserSession

        session = UserSession(
            user_id=user_end_user.id,
            session_token="test-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True,
            last_activity_at=datetime.now(timezone.utc)
        )
        db_session.add(session)
        db_session.commit()

        old_activity = session.last_activity_at

        # Update activity
        session.update_activity()
        db_session.commit()

        db_session.refresh(session)
        assert session.last_activity_at > old_activity

    def test_terminate_other_user_session_fails(self, client, db_session, user_end_user, user_admin, auth_headers_end_user):
        """❌ Test cannot terminate another user's session (without admin permission)"""
        from models import UserSession

        # Create session for admin
        admin_session = UserSession(
            user_id=user_admin.id,
            session_token="admin-token",
            ip_address="127.0.0.1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            is_active=True
        )
        db_session.add(admin_session)
        db_session.commit()

        # Try to terminate admin's session as end_user
        response = client.delete(
            f"{self.list_endpoint}/{admin_session.id}",
            headers=auth_headers_end_user
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
