"""
Token Management Tests

Tests for /api/v1/auth/refresh endpoint and token operations
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


class TestTokenRefresh:
    """Test token refresh functionality"""

    endpoint = "/api/v1/auth/refresh"

    def test_successful_token_refresh(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test successful token refresh with valid refresh token"""
        from models import RefreshToken
        from utils import hash_token

        # Store refresh token in database
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

        response = client.post(self.endpoint, json={
            "refresh_token": refresh_token_end_user
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify new tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_refresh_with_expired_token(self, client, db_session, user_end_user):
        """❌ Test refresh fails with expired refresh token"""
        from models import RefreshToken
        from jwt import create_refresh_token
        from utils import hash_token

        # Create expired refresh token
        expired_token = create_refresh_token(user_end_user)
        token_hash = hash_token(expired_token)

        # Store with past expiry date
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired
            ip_address="127.0.0.1",
            is_revoked=False
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        response = client.post(self.endpoint, json={
            "refresh_token": expired_token
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()

    def test_refresh_with_revoked_token(self, client, db_session, user_end_user, refresh_token_end_user):
        """❌ Test refresh fails with revoked refresh token"""
        from models import RefreshToken
        from utils import hash_token

        # Store revoked refresh token
        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1",
            is_revoked=True  # Revoked
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        response = client.post(self.endpoint, json={
            "refresh_token": refresh_token_end_user
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_refresh_with_invalid_token(self, client):
        """❌ Test refresh fails with invalid/malformed token"""
        response = client.post(self.endpoint, json={
            "refresh_token": "invalid-token-string"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_hash_storage(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test tokens are stored as hashes, not plain text"""
        from models import RefreshToken
        from utils import hash_token

        # Store token
        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1"
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        # Verify stored value is hash, not plain token
        assert refresh_token_obj.token_hash != refresh_token_end_user
        assert len(refresh_token_obj.token_hash) == 64  # SHA-256 hex length

    def test_token_family_tracking(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test token family tracking for token rotation"""
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

        # Verify token_family is set
        assert refresh_token_obj.token_family is not None

    def test_last_used_timestamp_update(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test last_used_at timestamp is updated on token use"""
        from models import RefreshToken
        from utils import hash_token

        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1",
            last_used_at=None
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        # Use token
        response = client.post(self.endpoint, json={
            "refresh_token": refresh_token_end_user
        })

        assert response.status_code == status.HTTP_200_OK

        # Check last_used_at was updated
        db_session.refresh(refresh_token_obj)
        assert refresh_token_obj.last_used_at is not None

    def test_device_and_ip_tracking(self, client, db_session, user_end_user, refresh_token_end_user):
        """✅ Test device info and IP address are tracked"""
        from models import RefreshToken
        from utils import hash_token

        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 Test Browser"
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        # Verify tracking data
        assert refresh_token_obj.ip_address == "192.168.1.100"
        assert refresh_token_obj.user_agent == "Mozilla/5.0 Test Browser"

    def test_refresh_with_inactive_user(self, client, db_session, user_inactive):
        """❌ Test refresh fails when user is inactive"""
        from models import RefreshToken
        from jwt import create_refresh_token
        from utils import hash_token

        # Create token for inactive user
        refresh_token = create_refresh_token(user_inactive)
        token_hash = hash_token(refresh_token)

        refresh_token_obj = RefreshToken(
            user_id=user_inactive.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1",
            is_revoked=False
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        response = client.post(self.endpoint, json={
            "refresh_token": refresh_token
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "inactive" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


class TestTokenValidation:
    """Test token validation and security"""

    def test_access_token_expiry(self, client, user_end_user):
        """✅ Test access token has correct expiry time"""
        from jwt import decode_access_token, create_access_token
        from config import get_settings

        settings = get_settings()
        token = create_access_token(user_end_user)
        payload = decode_access_token(token)

        # Calculate expected expiry
        expected_expiry = datetime.now(timezone.utc).timestamp() + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        # Allow 5 second tolerance for test execution time
        assert abs(payload["exp"] - expected_expiry) < 5

    def test_refresh_token_expiry(self, client, user_end_user):
        """✅ Test refresh token has correct expiry time"""
        from jwt import decode_refresh_token, create_refresh_token
        from config import get_settings

        settings = get_settings()
        token = create_refresh_token(user_end_user)
        payload = decode_refresh_token(token)

        # Calculate expected expiry
        expected_expiry = datetime.now(timezone.utc).timestamp() + (settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

        # Allow 5 second tolerance for test execution time
        assert abs(payload["exp"] - expected_expiry) < 5

    def test_token_contains_user_id(self, user_end_user):
        """✅ Test tokens contain user ID in 'sub' claim"""
        from jwt import decode_access_token, create_access_token

        token = create_access_token(user_end_user)
        payload = decode_access_token(token)

        assert payload["sub"] == str(user_end_user.id)

    def test_access_token_type_claim(self, user_end_user):
        """✅ Test access token has correct 'type' claim"""
        from jwt import decode_access_token, create_access_token

        token = create_access_token(user_end_user)
        payload = decode_access_token(token)

        assert payload["type"] == "access"

    def test_refresh_token_type_claim(self, user_end_user):
        """✅ Test refresh token has correct 'type' claim"""
        from jwt import decode_refresh_token, create_refresh_token

        token = create_refresh_token(user_end_user)
        payload = decode_refresh_token(token)

        assert payload["type"] == "refresh"
