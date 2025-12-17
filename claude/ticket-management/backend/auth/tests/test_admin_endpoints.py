"""
Admin Endpoints Tests

Tests for admin-only endpoints requiring ADMIN role
"""

import pytest
from fastapi import status


class TestAdminUserManagement:
    """Test admin user management endpoints"""

    base_endpoint = "/api/v1/auth/admin/users"

    def test_list_all_users(self, client, auth_headers_admin, user_end_user, user_devops_engineer):
        """✅ Test admin can list all users"""
        response = client.get(self.base_endpoint, headers=auth_headers_admin)

        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) >= 2

    def test_list_users_with_role_filter(self, client, auth_headers_admin, user_end_user, user_admin):
        """✅ Test filtering users by role"""
        response = client.get(
            f"{self.base_endpoint}?role=END_USER",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert all(user["role"] == "END_USER" for user in users)

    def test_list_users_with_active_filter(self, client, auth_headers_admin, user_inactive):
        """✅ Test filtering users by is_active status"""
        response = client.get(
            f"{self.base_endpoint}?is_active=false",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK

    def test_list_users_with_search(self, client, auth_headers_admin, user_end_user):
        """✅ Test searching users"""
        response = client.get(
            f"{self.base_endpoint}?search={user_end_user.username}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) >= 1
        assert any(user["username"] == user_end_user.username for user in users)

    def test_get_user_by_id(self, client, auth_headers_admin, user_end_user):
        """✅ Test admin can get user by ID"""
        response = client.get(
            f"{self.base_endpoint}/{user_end_user.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["id"] == str(user_end_user.id)
        assert user_data["username"] == user_end_user.username

    def test_update_user_profile(self, client, db_session, auth_headers_admin, user_end_user):
        """✅ Test admin can update user profile"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "department": "New Department"
        }

        response = client.put(
            f"{self.base_endpoint}/{user_end_user.id}",
            headers=auth_headers_admin,
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"

    def test_update_user_role(self, client, db_session, auth_headers_admin, user_end_user):
        """✅ Test admin can update user role"""
        response = client.patch(
            f"{self.base_endpoint}/{user_end_user.id}/role",
            headers=auth_headers_admin,
            json={"role": "DEVOPS_ENGINEER"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "DEVOPS_ENGINEER"

    def test_update_user_status(self, client, db_session, auth_headers_admin, user_end_user):
        """✅ Test admin can activate/deactivate user"""
        response = client.patch(
            f"{self.base_endpoint}/{user_end_user.id}/status",
            headers=auth_headers_admin,
            json={"is_active": False}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False

    def test_soft_delete_user(self, client, db_session, auth_headers_admin, user_end_user):
        """✅ Test admin can soft delete user"""
        response = client.delete(
            f"{self.base_endpoint}/{user_end_user.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify user is soft deleted
        db_session.refresh(user_end_user)
        assert user_end_user.deleted_at is not None
        assert user_end_user.is_active is False

    def test_cannot_delete_own_account(self, client, user_admin, auth_headers_admin):
        """❌ Test admin cannot delete their own account"""
        response = client.delete(
            f"{self.base_endpoint}/{user_admin.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "own account" in response.json()["detail"].lower()

    def test_non_admin_cannot_access(self, client, auth_headers_end_user):
        """❌ Test non-admin users cannot access admin endpoints"""
        response = client.get(self.base_endpoint, headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminTokenManagement:
    """Test admin token management endpoints"""

    def test_list_user_tokens(self, client, db_session, auth_headers_admin, user_end_user, refresh_token_end_user):
        """✅ Test admin can list user's tokens"""
        from models import RefreshToken
        from utils import hash_token
        from datetime import timedelta

        # Create token in database
        token_hash = hash_token(refresh_token_end_user)
        refresh_token_obj = RefreshToken(
            user_id=user_end_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            ip_address="127.0.0.1"
        )
        db_session.add(refresh_token_obj)
        db_session.commit()

        response = client.get(
            f"/api/v1/auth/admin/tokens/user/{user_end_user.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tokens" in data
        assert data["total"] >= 1

    def test_revoke_specific_token(self, client, db_session, auth_headers_admin, user_end_user, refresh_token_end_user):
        """✅ Test admin can revoke specific token"""
        from models import RefreshToken
        from utils import hash_token
        from datetime import timedelta, timezone

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

        response = client.delete(
            f"/api/v1/auth/admin/tokens/{refresh_token_obj.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify token is revoked
        db_session.refresh(refresh_token_obj)
        assert refresh_token_obj.is_revoked is True

    def test_revoke_all_user_tokens(self, client, db_session, auth_headers_admin, user_end_user):
        """✅ Test admin can revoke all user tokens"""
        from models import RefreshToken
        from datetime import timedelta, timezone

        # Create multiple tokens
        for i in range(3):
            token = RefreshToken(
                user_id=user_end_user.id,
                token_hash=f"hash{i}",
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                ip_address="127.0.0.1",
                is_revoked=False
            )
            db_session.add(token)
        db_session.commit()

        response = client.delete(
            f"/api/v1/auth/admin/tokens/user/{user_end_user.id}/revoke-all",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "revoked" in data["message"].lower()

    def test_non_admin_cannot_manage_tokens(self, client, auth_headers_end_user, user_admin):
        """❌ Test non-admin cannot manage tokens"""
        response = client.get(
            f"/api/v1/auth/admin/tokens/user/{user_admin.id}",
            headers=auth_headers_end_user
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminAuditLogs:
    """Test admin audit log endpoints"""

    endpoint = "/api/v1/auth/admin/audit-logs"

    def test_get_audit_logs(self, client, auth_headers_admin):
        """✅ Test admin can get audit logs"""
        response = client.get(self.endpoint, headers=auth_headers_admin)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "logs" in data
        assert "total" in data

    def test_filter_audit_logs_by_user(self, client, auth_headers_admin, user_end_user):
        """✅ Test filtering audit logs by user_id"""
        response = client.get(
            f"{self.endpoint}?user_id={user_end_user.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK

    def test_filter_audit_logs_by_action_type(self, client, auth_headers_admin):
        """✅ Test filtering audit logs by action_type"""
        response = client.get(
            f"{self.endpoint}?action_type=LOGIN_SUCCESS",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK

    def test_audit_logs_pagination(self, client, auth_headers_admin):
        """✅ Test audit logs pagination"""
        response = client.get(
            f"{self.endpoint}?limit=10&offset=0",
            headers=auth_headers_admin
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_non_admin_cannot_access_audit_logs(self, client, auth_headers_end_user):
        """❌ Test non-admin cannot access audit logs"""
        response = client.get(self.endpoint, headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_403_FORBIDDEN
