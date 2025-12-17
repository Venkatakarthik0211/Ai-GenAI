"""
User Registration Tests

Tests for /api/v1/auth/register endpoint
"""

import pytest
from fastapi import status


class TestRegistration:
    """Test user registration functionality"""

    endpoint = "/api/v1/auth/register"

    def test_successful_registration_with_valid_data(self, client, valid_registration_data, mock_email_service):
        """✅ Test successful registration with all valid data"""
        response = client.post(self.endpoint, json=valid_registration_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["username"] == valid_registration_data["username"]
        assert data["email"] == valid_registration_data["email"]
        assert data["first_name"] == valid_registration_data["first_name"]
        assert data["last_name"] == valid_registration_data["last_name"]
        assert data["role"] == "END_USER"  # Default role
        assert data["is_active"] is True
        assert "password" not in data  # Password should not be in response
        assert "created_at" in data

        # Verify welcome email was sent
        assert len(mock_email_service) > 0
        assert any("Welcome" in email["subject"] for email in mock_email_service)

    def test_duplicate_username_rejection(self, client, user_end_user, valid_registration_data):
        """❌ Test registration fails with duplicate username"""
        valid_registration_data["username"] = user_end_user.username
        valid_registration_data["email"] = "different@example.com"

        response = client.post(self.endpoint, json=valid_registration_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.json()["detail"].lower()

    def test_duplicate_email_rejection(self, client, user_end_user, valid_registration_data):
        """❌ Test registration fails with duplicate email"""
        valid_registration_data["username"] = "different_user"
        valid_registration_data["email"] = user_end_user.email

        response = client.post(self.endpoint, json=valid_registration_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()["detail"].lower()

    def test_invalid_email_format(self, client, valid_registration_data):
        """❌ Test registration fails with invalid email format"""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "double@@domain.com"
        ]

        for invalid_email in invalid_emails:
            valid_registration_data["email"] = invalid_email
            response = client.post(self.endpoint, json=valid_registration_data)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, \
                f"Email '{invalid_email}' should be rejected"

    def test_weak_password_rejection(self, client, valid_registration_data):
        """❌ Test registration fails with weak passwords"""
        weak_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoDigits!!",  # No digits
            "NoSpecial123",  # No special characters
            "simple",  # Too simple
        ]

        for weak_password in weak_passwords:
            valid_registration_data["password"] = weak_password
            response = client.post(self.endpoint, json=valid_registration_data)

            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ], f"Password '{weak_password}' should be rejected"

    def test_phone_number_format_validation(self, client, valid_registration_data):
        """✅ Test phone number format validation accepts international formats"""
        valid_phone_formats = [
            "+1-555-0100",
            "+44 20 1234 5678",
            "+1 (555) 123-4567",
            "+33 1 42 86 82 00",
            "555-0100",
            "(555) 123-4567"
        ]

        for idx, phone_number in enumerate(valid_phone_formats):
            valid_registration_data["username"] = f"user{idx}"
            valid_registration_data["email"] = f"user{idx}@example.com"
            valid_registration_data["phone_number"] = phone_number

            response = client.post(self.endpoint, json=valid_registration_data)

            assert response.status_code == status.HTTP_201_CREATED, \
                f"Phone format '{phone_number}' should be accepted"

    def test_default_role_assignment(self, client, valid_registration_data):
        """✅ Test new users get END_USER role by default"""
        response = client.post(self.endpoint, json=valid_registration_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["role"] == "END_USER"

    def test_email_verification_flow_when_required(self, client, valid_registration_data, mock_email_service, monkeypatch):
        """✅ Test email verification process when enabled"""
        # Enable email verification
        monkeypatch.setenv("EMAIL_VERIFICATION_REQUIRED", "true")

        response = client.post(self.endpoint, json=valid_registration_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify email sent
        assert len(mock_email_service) > 0
        assert any("Verify" in email["subject"] for email in mock_email_service)

        # Email should not be verified yet
        assert data["is_email_verified"] is False

    def test_audit_log_creation(self, client, db_session, valid_registration_data):
        """✅ Test audit log is created on registration"""
        from models import AuditLog, AuditEventType

        response = client.post(self.endpoint, json=valid_registration_data)
        assert response.status_code == status.HTTP_201_CREATED

        user_id = response.json()["id"]

        # Check audit log exists
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action_type == AuditEventType.ACCOUNT_CREATED
        ).first()

        assert audit_log is not None
        assert audit_log.status == "SUCCESS"
        assert audit_log.severity == "INFO"

    def test_registration_without_optional_fields(self, client):
        """✅ Test registration succeeds without optional fields"""
        minimal_data = {
            "username": "minimal_user",
            "email": "minimal@example.com",
            "password": "MinimalPass123!",
            "first_name": "Minimal",
            "last_name": "User"
            # No phone_number or department
        }

        response = client.post(self.endpoint, json=minimal_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == minimal_data["username"]
        assert data["phone_number"] is None
        assert data["department"] is None


class TestRegistrationEdgeCases:
    """Test edge cases and boundary conditions for registration"""

    endpoint = "/api/v1/auth/register"

    def test_username_length_boundaries(self, client, valid_registration_data):
        """Test username length validation"""
        # Too short
        valid_registration_data["username"] = "ab"
        response = client.post(self.endpoint, json=valid_registration_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Minimum valid length (3)
        valid_registration_data["username"] = "abc"
        response = client.post(self.endpoint, json=valid_registration_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Too long (>50)
        valid_registration_data["username"] = "a" * 51
        valid_registration_data["email"] = "different@example.com"
        response = client.post(self.endpoint, json=valid_registration_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_password_length_boundaries(self, client, valid_registration_data):
        """Test password length validation"""
        # Minimum valid length (8 characters with complexity)
        valid_registration_data["password"] = "Pass123!"
        response = client.post(self.endpoint, json=valid_registration_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Test very long password (should be truncated to 72 bytes for bcrypt)
        valid_registration_data["username"] = "longpass"
        valid_registration_data["email"] = "longpass@example.com"
        valid_registration_data["password"] = "A" * 100 + "a1!"  # Very long with complexity
        response = client.post(self.endpoint, json=valid_registration_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_special_characters_in_names(self, client, valid_registration_data):
        """Test names with special characters and unicode"""
        test_cases = [
            ("José", "García"),
            ("François", "Müller"),
            ("O'Brien", "O'Connor"),
            ("Mary-Jane", "Smith-Johnson"),
        ]

        for idx, (first_name, last_name) in enumerate(test_cases):
            valid_registration_data["username"] = f"special{idx}"
            valid_registration_data["email"] = f"special{idx}@example.com"
            valid_registration_data["first_name"] = first_name
            valid_registration_data["last_name"] = last_name

            response = client.post(self.endpoint, json=valid_registration_data)
            assert response.status_code == status.HTTP_201_CREATED

    def test_missing_required_fields(self, client):
        """Test registration fails when required fields are missing"""
        required_fields = ["username", "email", "password", "first_name", "last_name"]

        base_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }

        for field in required_fields:
            incomplete_data = base_data.copy()
            del incomplete_data[field]

            response = client.post(self.endpoint, json=incomplete_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, \
                f"Missing field '{field}' should cause validation error"
