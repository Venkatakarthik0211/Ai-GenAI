"""
Role-Based Access Control (RBAC) Permissions

This module defines permissions and permission checking for different user roles.
Reference: /backend/auth/README.md - Authorization & Permissions
"""

from enum import Enum
from typing import List, Set

from fastapi import Depends, HTTPException, status

from models import User, UserRole
from dependencies import get_current_user


class Permission(str, Enum):
    """
    System permissions
    Reference: /backend/auth/README.md - Role Permissions Matrix
    """
    # Ticket Permissions
    CREATE_TICKET = "create_ticket"
    VIEW_OWN_TICKETS = "view_own_tickets"
    VIEW_ALL_TICKETS = "view_all_tickets"
    UPDATE_TICKET_STATUS = "update_ticket_status"
    ASSIGN_TICKET = "assign_ticket"
    ESCALATE_TICKET = "escalate_ticket"
    DELETE_TICKET = "delete_ticket"
    CLOSE_TICKET = "close_ticket"
    REOPEN_TICKET = "reopen_ticket"

    # Comment Permissions
    ADD_COMMENT = "add_comment"
    VIEW_INTERNAL_COMMENTS = "view_internal_comments"
    ADD_INTERNAL_COMMENT = "add_internal_comment"
    EDIT_OWN_COMMENT = "edit_own_comment"
    DELETE_COMMENT = "delete_comment"

    # Attachment Permissions
    UPLOAD_ATTACHMENT = "upload_attachment"
    DOWNLOAD_ATTACHMENT = "download_attachment"
    DELETE_ATTACHMENT = "delete_attachment"

    # User Management Permissions
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    MANAGE_ROLES = "manage_roles"
    LOCK_UNLOCK_USER = "lock_unlock_user"

    # Report Permissions
    VIEW_REPORTS = "view_reports"
    VIEW_TEAM_REPORTS = "view_team_reports"
    VIEW_ALL_REPORTS = "view_all_reports"
    EXPORT_REPORTS = "export_reports"

    # SLA & Escalation Permissions
    VIEW_SLA_POLICIES = "view_sla_policies"
    MANAGE_SLA_POLICIES = "manage_sla_policies"
    VIEW_ESCALATIONS = "view_escalations"
    CREATE_ESCALATION = "create_escalation"

    # Notification Permissions
    MANAGE_NOTIFICATIONS = "manage_notifications"
    SEND_BULK_NOTIFICATIONS = "send_bulk_notifications"

    # System Permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    ACCESS_ADMIN_PANEL = "access_admin_panel"


# ============================================================================
# Role Permission Mapping
# ============================================================================

ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    # END_USER - Level 0
    UserRole.END_USER: {
        Permission.CREATE_TICKET,
        Permission.VIEW_OWN_TICKETS,
        Permission.ADD_COMMENT,
        Permission.EDIT_OWN_COMMENT,
        Permission.UPLOAD_ATTACHMENT,
        Permission.DOWNLOAD_ATTACHMENT,
    },

    # DEVOPS_ENGINEER - Level 1
    UserRole.DEVOPS_ENGINEER: {
        Permission.CREATE_TICKET,
        Permission.VIEW_OWN_TICKETS,
        Permission.VIEW_ALL_TICKETS,
        Permission.UPDATE_TICKET_STATUS,
        Permission.ESCALATE_TICKET,
        Permission.CLOSE_TICKET,
        Permission.ADD_COMMENT,
        Permission.VIEW_INTERNAL_COMMENTS,
        Permission.EDIT_OWN_COMMENT,
        Permission.UPLOAD_ATTACHMENT,
        Permission.DOWNLOAD_ATTACHMENT,
        Permission.VIEW_SLA_POLICIES,
    },

    # SENIOR_ENGINEER - Level 2
    UserRole.SENIOR_ENGINEER: {
        Permission.CREATE_TICKET,
        Permission.VIEW_OWN_TICKETS,
        Permission.VIEW_ALL_TICKETS,
        Permission.UPDATE_TICKET_STATUS,
        Permission.ESCALATE_TICKET,
        Permission.CLOSE_TICKET,
        Permission.REOPEN_TICKET,
        Permission.ADD_COMMENT,
        Permission.VIEW_INTERNAL_COMMENTS,
        Permission.ADD_INTERNAL_COMMENT,
        Permission.EDIT_OWN_COMMENT,
        Permission.UPLOAD_ATTACHMENT,
        Permission.DOWNLOAD_ATTACHMENT,
        Permission.VIEW_SLA_POLICIES,
        Permission.VIEW_ESCALATIONS,
        Permission.VIEW_TEAM_REPORTS,
    },

    # TEAM_LEAD - Level 3
    UserRole.TEAM_LEAD: {
        Permission.CREATE_TICKET,
        Permission.VIEW_OWN_TICKETS,
        Permission.VIEW_ALL_TICKETS,
        Permission.UPDATE_TICKET_STATUS,
        Permission.ASSIGN_TICKET,
        Permission.ESCALATE_TICKET,
        Permission.CLOSE_TICKET,
        Permission.REOPEN_TICKET,
        Permission.ADD_COMMENT,
        Permission.VIEW_INTERNAL_COMMENTS,
        Permission.ADD_INTERNAL_COMMENT,
        Permission.EDIT_OWN_COMMENT,
        Permission.DELETE_COMMENT,
        Permission.UPLOAD_ATTACHMENT,
        Permission.DOWNLOAD_ATTACHMENT,
        Permission.DELETE_ATTACHMENT,
        Permission.VIEW_USERS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_TEAM_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_SLA_POLICIES,
        Permission.VIEW_ESCALATIONS,
        Permission.CREATE_ESCALATION,
    },

    # MANAGER - Level 4
    UserRole.MANAGER: {
        Permission.CREATE_TICKET,
        Permission.VIEW_OWN_TICKETS,
        Permission.VIEW_ALL_TICKETS,
        Permission.UPDATE_TICKET_STATUS,
        Permission.ASSIGN_TICKET,
        Permission.ESCALATE_TICKET,
        Permission.CLOSE_TICKET,
        Permission.REOPEN_TICKET,
        Permission.DELETE_TICKET,
        Permission.ADD_COMMENT,
        Permission.VIEW_INTERNAL_COMMENTS,
        Permission.ADD_INTERNAL_COMMENT,
        Permission.EDIT_OWN_COMMENT,
        Permission.DELETE_COMMENT,
        Permission.UPLOAD_ATTACHMENT,
        Permission.DOWNLOAD_ATTACHMENT,
        Permission.DELETE_ATTACHMENT,
        Permission.VIEW_USERS,
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.VIEW_REPORTS,
        Permission.VIEW_TEAM_REPORTS,
        Permission.VIEW_ALL_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_SLA_POLICIES,
        Permission.MANAGE_SLA_POLICIES,
        Permission.VIEW_ESCALATIONS,
        Permission.CREATE_ESCALATION,
        Permission.MANAGE_NOTIFICATIONS,
        Permission.VIEW_AUDIT_LOGS,
    },

    # ADMIN - Level 5 (All Permissions)
    UserRole.ADMIN: set(Permission),  # All permissions
}


# ============================================================================
# Permission Checking Functions
# ============================================================================

def get_user_permissions(user: User) -> Set[Permission]:
    """
    Get all permissions for a user based on their role

    Args:
        user: User object

    Returns:
        Set of permissions the user has
    """
    return ROLE_PERMISSIONS.get(user.role, set())


def user_has_permission(user: User, permission: Permission) -> bool:
    """
    Check if user has a specific permission

    Args:
        user: User object
        permission: Permission to check

    Returns:
        True if user has permission, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


def user_has_any_permission(user: User, permissions: List[Permission]) -> bool:
    """
    Check if user has any of the specified permissions

    Args:
        user: User object
        permissions: List of permissions to check

    Returns:
        True if user has at least one permission, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return any(p in user_permissions for p in permissions)


def user_has_all_permissions(user: User, permissions: List[Permission]) -> bool:
    """
    Check if user has all of the specified permissions

    Args:
        user: User object
        permissions: List of permissions to check

    Returns:
        True if user has all permissions, False otherwise
    """
    user_permissions = get_user_permissions(user)
    return all(p in user_permissions for p in permissions)


# ============================================================================
# Permission Dependencies (FastAPI)
# ============================================================================

def check_permission(permission: Permission):
    """
    Dependency factory to check if user has specific permission

    Args:
        permission: Required permission

    Returns:
        Dependency function that checks user permission

    Reference: /backend/auth/README.md - Permission-Based Access
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not user_has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission.value} required. Your role: {current_user.role.value}"
            )
        return current_user

    return permission_checker


def check_any_permission(permissions: List[Permission]):
    """
    Dependency factory to check if user has any of the specified permissions

    Args:
        permissions: List of permissions (user needs at least one)

    Returns:
        Dependency function that checks user permissions
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not user_has_any_permission(current_user, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: One of {permission_names} required"
            )
        return current_user

    return permission_checker


def check_all_permissions(permissions: List[Permission]):
    """
    Dependency factory to check if user has all of the specified permissions

    Args:
        permissions: List of permissions (user needs all)

    Returns:
        Dependency function that checks user permissions
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not user_has_all_permissions(current_user, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: All of {permission_names} required"
            )
        return current_user

    return permission_checker


# ============================================================================
# Resource Ownership Checking
# ============================================================================

def can_access_resource(user: User, resource_owner_id: str, required_permission: Permission) -> bool:
    """
    Check if user can access a resource based on ownership or permission

    Args:
        user: User object
        resource_owner_id: ID of the resource owner
        required_permission: Permission required for non-owners

    Returns:
        True if user can access resource, False otherwise
    """
    # User is the owner
    if str(user.id) == resource_owner_id:
        return True

    # User has required permission for all resources
    if user_has_permission(user, required_permission):
        return True

    return False


def check_resource_ownership(resource_owner_id: str):
    """
    Dependency factory to check if user owns resource or has permission

    Args:
        resource_owner_id: ID of the resource owner

    Returns:
        Dependency function that checks ownership or permission
    """
    async def ownership_checker(current_user: User = Depends(get_current_user)) -> User:
        # User is the owner
        if str(current_user.id) == resource_owner_id:
            return current_user

        # Check if user has permission to access all resources
        if not user_has_permission(current_user, Permission.VIEW_ALL_TICKETS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own resources"
            )

        return current_user

    return ownership_checker


# ============================================================================
# Convenience Permission Checkers
# ============================================================================

require_view_all_tickets = check_permission(Permission.VIEW_ALL_TICKETS)
require_assign_tickets = check_permission(Permission.ASSIGN_TICKET)
require_delete_tickets = check_permission(Permission.DELETE_TICKET)
require_manage_users = check_permission(Permission.MANAGE_ROLES)
require_view_reports = check_permission(Permission.VIEW_REPORTS)
require_manage_sla = check_permission(Permission.MANAGE_SLA_POLICIES)
require_system_settings = check_permission(Permission.MANAGE_SYSTEM_SETTINGS)
require_audit_logs = check_permission(Permission.VIEW_AUDIT_LOGS)


# ============================================================================
# Utility Functions
# ============================================================================

def get_permission_description(permission: Permission) -> str:
    """
    Get human-readable description of permission

    Args:
        permission: Permission enum

    Returns:
        Description string
    """
    descriptions = {
        Permission.CREATE_TICKET: "Create new support tickets",
        Permission.VIEW_ALL_TICKETS: "View all tickets in the system",
        Permission.ASSIGN_TICKET: "Assign tickets to users",
        Permission.DELETE_TICKET: "Delete tickets",
        Permission.MANAGE_ROLES: "Manage user roles and permissions",
        Permission.VIEW_REPORTS: "View reports and analytics",
        Permission.MANAGE_SLA_POLICIES: "Manage SLA policies",
        Permission.MANAGE_SYSTEM_SETTINGS: "Manage system configuration",
    }
    return descriptions.get(permission, permission.value.replace("_", " ").title())


def get_role_description(role: UserRole) -> str:
    """
    Get human-readable description of role

    Args:
        role: UserRole enum

    Returns:
        Description string
    """
    descriptions = {
        UserRole.END_USER: "Basic user who can create and view own tickets",
        UserRole.DEVOPS_ENGINEER: "Technical staff who can handle and update tickets",
        UserRole.SENIOR_ENGINEER: "Senior technical staff with escalation handling",
        UserRole.TEAM_LEAD: "Team supervisor with assignment and reporting access",
        UserRole.MANAGER: "Department manager with full team oversight",
        UserRole.ADMIN: "System administrator with full access",
    }
    return descriptions.get(role, role.value)
