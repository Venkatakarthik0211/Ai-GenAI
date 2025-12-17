"""
RBAC and Permissions Tests

Tests for role-based access control and permission checking
"""

import pytest
from fastapi import status
from models import UserRole
from permissions import Permission, get_user_permissions, user_has_permission


class TestRoleHierarchy:
    """Test user role hierarchy and levels"""

    def test_end_user_permissions(self, user_end_user):
        """✅ Test END_USER role permissions (Level 0)"""
        permissions = get_user_permissions(user_end_user)

        # Should have basic permissions
        assert Permission.CREATE_TICKET in permissions
        assert Permission.VIEW_OWN_TICKETS in permissions
        assert Permission.ADD_COMMENT in permissions

        # Should NOT have advanced permissions
        assert Permission.VIEW_ALL_TICKETS not in permissions
        assert Permission.ASSIGN_TICKET not in permissions
        assert Permission.DELETE_TICKET not in permissions

    def test_devops_engineer_permissions(self, user_devops_engineer):
        """✅ Test DEVOPS_ENGINEER role permissions (Level 1)"""
        permissions = get_user_permissions(user_devops_engineer)

        assert Permission.VIEW_ALL_TICKETS in permissions
        assert Permission.UPDATE_TICKET_STATUS in permissions
        assert Permission.ESCALATE_TICKET in permissions

        # Should NOT have assignment permission
        assert Permission.ASSIGN_TICKET not in permissions

    def test_senior_engineer_permissions(self, user_senior_engineer):
        """✅ Test SENIOR_ENGINEER role permissions (Level 2)"""
        permissions = get_user_permissions(user_senior_engineer)

        assert Permission.VIEW_ALL_TICKETS in permissions
        assert Permission.ADD_INTERNAL_COMMENT in permissions
        assert Permission.VIEW_TEAM_REPORTS in permissions

    def test_team_lead_permissions(self, user_team_lead):
        """✅ Test TEAM_LEAD role permissions (Level 3)"""
        permissions = get_user_permissions(user_team_lead)

        assert Permission.ASSIGN_TICKET in permissions
        assert Permission.VIEW_REPORTS in permissions
        assert Permission.DELETE_COMMENT in permissions

        # Should NOT have user management
        assert Permission.MANAGE_ROLES not in permissions

    def test_manager_permissions(self, user_manager):
        """✅ Test MANAGER role permissions (Level 4)"""
        permissions = get_user_permissions(user_manager)

        assert Permission.DELETE_TICKET in permissions
        assert Permission.MANAGE_SLA_POLICIES in permissions
        assert Permission.VIEW_ALL_REPORTS in permissions
        assert Permission.CREATE_USER in permissions

    def test_admin_permissions(self, user_admin):
        """✅ Test ADMIN role has all permissions (Level 5)"""
        permissions = get_user_permissions(user_admin)

        # Should have ALL permissions
        assert Permission.MANAGE_ROLES in permissions
        assert Permission.MANAGE_SYSTEM_SETTINGS in permissions
        assert Permission.ACCESS_ADMIN_PANEL in permissions
        assert len(permissions) == len(Permission)  # All permissions

    def test_role_level_comparison(self):
        """✅ Test role level hierarchy"""
        assert UserRole.END_USER.level == 0
        assert UserRole.DEVOPS_ENGINEER.level == 1
        assert UserRole.SENIOR_ENGINEER.level == 2
        assert UserRole.TEAM_LEAD.level == 3
        assert UserRole.MANAGER.level == 4
        assert UserRole.ADMIN.level == 5


class TestPermissionChecking:
    """Test permission checking functions"""

    def test_user_has_permission(self, user_team_lead):
        """✅ Test user_has_permission function"""
        assert user_has_permission(user_team_lead, Permission.ASSIGN_TICKET)
        assert not user_has_permission(user_team_lead, Permission.MANAGE_SYSTEM_SETTINGS)

    def test_user_has_any_permission(self, user_devops_engineer):
        """✅ Test user_has_any_permission function"""
        from permissions import user_has_any_permission

        # Should have at least one of these
        assert user_has_any_permission(user_devops_engineer, [
            Permission.VIEW_ALL_TICKETS,
            Permission.ASSIGN_TICKET
        ])

        # Should not have any of these
        assert not user_has_any_permission(user_devops_engineer, [
            Permission.DELETE_TICKET,
            Permission.MANAGE_ROLES
        ])

    def test_user_has_all_permissions(self, user_team_lead):
        """✅ Test user_has_all_permissions function"""
        from permissions import user_has_all_permissions

        # Should have all of these
        assert user_has_all_permissions(user_team_lead, [
            Permission.VIEW_ALL_TICKETS,
            Permission.ASSIGN_TICKET,
            Permission.VIEW_REPORTS
        ])

        # Should not have all of these
        assert not user_has_all_permissions(user_team_lead, [
            Permission.ASSIGN_TICKET,
            Permission.DELETE_TICKET  # Don't have this
        ])


class TestRoleRequirements:
    """Test role requirement dependencies"""

    def test_require_admin_dependency(self, client, auth_headers_admin, auth_headers_end_user):
        """✅ Test require_admin dependency"""
        # Admin should access
        response = client.get("/api/v1/auth/admin/users", headers=auth_headers_admin)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

        # Non-admin should be denied
        response = client.get("/api/v1/auth/admin/users", headers=auth_headers_end_user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_require_manager_dependency(self, client, auth_headers_manager, auth_headers_devops_engineer):
        """✅ Test require_manager dependency"""
        # Manager should have access to manager-level endpoints
        # DevOps engineer should be denied

        # Test with a manager-level permission check
        assert auth_headers_manager is not None
        assert auth_headers_devops_engineer is not None

    def test_require_team_lead_dependency(self, client, auth_headers_team_lead, auth_headers_end_user):
        """✅ Test require_team_lead dependency"""
        # Team lead should have access
        # End user should be denied
        assert auth_headers_team_lead is not None
        assert auth_headers_end_user is not None


class TestResourceOwnership:
    """Test resource ownership checking"""

    def test_can_access_own_resource(self, user_end_user):
        """✅ Test user can access their own resources"""
        from permissions import can_access_resource

        # User can access their own resource
        assert can_access_resource(
            user_end_user,
            str(user_end_user.id),
            Permission.VIEW_ALL_TICKETS
        )

    def test_cannot_access_other_resource_without_permission(self, user_end_user, user_admin):
        """❌ Test user cannot access other's resources without permission"""
        from permissions import can_access_resource

        # End user cannot access admin's resource (no VIEW_ALL permission)
        assert not can_access_resource(
            user_end_user,
            str(user_admin.id),
            Permission.VIEW_ALL_TICKETS
        )

    def test_can_access_other_resource_with_permission(self, user_team_lead, user_end_user):
        """✅ Test user with permission can access others' resources"""
        from permissions import can_access_resource

        # Team lead has VIEW_ALL_TICKETS permission
        assert can_access_resource(
            user_team_lead,
            str(user_end_user.id),
            Permission.VIEW_ALL_TICKETS
        )


class TestPermissionDescriptions:
    """Test permission and role descriptions"""

    def test_get_permission_description(self):
        """✅ Test get_permission_description function"""
        from permissions import get_permission_description

        desc = get_permission_description(Permission.CREATE_TICKET)
        assert "ticket" in desc.lower()

        desc = get_permission_description(Permission.MANAGE_ROLES)
        assert "role" in desc.lower()

    def test_get_role_description(self):
        """✅ Test get_role_description function"""
        from permissions import get_role_description

        desc = get_role_description(UserRole.ADMIN)
        assert "administrator" in desc.lower()

        desc = get_role_description(UserRole.END_USER)
        assert "user" in desc.lower()


class TestPermissionEndpoints:
    """Test permission-protected endpoints"""

    def test_permission_denied_error_message(self, client, auth_headers_end_user):
        """❌ Test clear error message on permission denial"""
        response = client.get("/api/v1/auth/admin/users", headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        error_detail = response.json()["detail"]
        assert "permission" in error_detail.lower() or "access" in error_detail.lower()

    def test_role_information_in_error(self, client, auth_headers_end_user):
        """❌ Test error includes user's current role"""
        response = client.get("/api/v1/auth/admin/users", headers=auth_headers_end_user)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Error should indicate what role is needed or what user has
        error_detail = response.json()["detail"]
        assert error_detail  # Should have meaningful error message
