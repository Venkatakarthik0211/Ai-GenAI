"""
Test Configuration and Fixtures

This module provides pytest fixtures for authentication testing.
"""

import os
import pytest
from datetime import datetime, timezone
from typing import Generator, Dict
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import application modules
import sys
from pathlib import Path
auth_path = Path(__file__).parent.parent
sys.path.insert(0, str(auth_path))

from models import Base, User, UserRole, UserStatus
from main import app
from dependencies import get_db
from config import get_settings
from jwt import create_access_token, create_refresh_token


# ============================================================================
# Test Database Configuration
# ============================================================================

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine with in-memory SQLite"""
    # Use in-memory SQLite for fast tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a new database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )

    session = TestingSessionLocal()

    yield session

    # Clear all tables after each test to prevent unique constraint errors
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def password_plain() -> str:
    """Standard test password"""
    return "TestPass123!"


@pytest.fixture
def user_end_user(db_session, password_plain) -> User:
    """Create END_USER test user"""
    user = User(
        id=uuid4(),
        username="enduser",
        email="enduser@example.com",
        first_name="End",
        last_name="User",
        phone_number="+1-555-0100",
        department="Support",
        role=UserRole.END_USER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_devops_engineer(db_session, password_plain) -> User:
    """Create DEVOPS_ENGINEER test user"""
    user = User(
        id=uuid4(),
        username="devops.engineer",
        email="devops.engineer@example.com",
        first_name="DevOps",
        last_name="Engineer",
        phone_number="+1-555-0101",
        department="Infrastructure",
        role=UserRole.DEVOPS_ENGINEER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_senior_engineer(db_session, password_plain) -> User:
    """Create SENIOR_ENGINEER test user"""
    user = User(
        id=uuid4(),
        username="senior.engineer",
        email="senior.engineer@example.com",
        first_name="Senior",
        last_name="Engineer",
        phone_number="+1-555-0102",
        department="Infrastructure",
        role=UserRole.SENIOR_ENGINEER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_team_lead(db_session, password_plain) -> User:
    """Create TEAM_LEAD test user"""
    user = User(
        id=uuid4(),
        username="team.lead",
        email="team.lead@example.com",
        first_name="Team",
        last_name="Lead",
        phone_number="+1-555-0103",
        department="Infrastructure",
        role=UserRole.TEAM_LEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_manager(db_session, password_plain) -> User:
    """Create MANAGER test user"""
    user = User(
        id=uuid4(),
        username="manager",
        email="manager@example.com",
        first_name="Manager",
        last_name="User",
        phone_number="+1-555-0104",
        department="IT",
        role=UserRole.MANAGER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_admin(db_session, password_plain) -> User:
    """Create ADMIN test user"""
    user = User(
        id=uuid4(),
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        phone_number="+1-555-0105",
        department="IT",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_inactive(db_session, password_plain) -> User:
    """Create inactive test user"""
    user = User(
        id=uuid4(),
        username="inactive.user",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        phone_number="+1-555-0106",
        department="Support",
        role=UserRole.END_USER,
        status=UserStatus.INACTIVE,
        is_active=False,
        is_email_verified=True,
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_locked(db_session, password_plain) -> User:
    """Create locked test user"""
    from datetime import timedelta
    user = User(
        id=uuid4(),
        username="locked.user",
        email="locked@example.com",
        first_name="Locked",
        last_name="User",
        phone_number="+1-555-0107",
        department="Support",
        role=UserRole.END_USER,
        status=UserStatus.LOCKED,
        is_active=True,
        is_email_verified=True,
        failed_login_attempts=5,
        account_locked_until=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    user.set_password(password_plain)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# Token Fixtures
# ============================================================================

@pytest.fixture
def access_token_end_user(user_end_user) -> str:
    """Generate access token for END_USER"""
    return create_access_token(user_end_user)


@pytest.fixture
def access_token_devops_engineer(user_devops_engineer) -> str:
    """Generate access token for DEVOPS_ENGINEER"""
    return create_access_token(user_devops_engineer)


@pytest.fixture
def access_token_team_lead(user_team_lead) -> str:
    """Generate access token for TEAM_LEAD"""
    return create_access_token(user_team_lead)


@pytest.fixture
def access_token_manager(user_manager) -> str:
    """Generate access token for MANAGER"""
    return create_access_token(user_manager)


@pytest.fixture
def access_token_admin(user_admin) -> str:
    """Generate access token for ADMIN"""
    return create_access_token(user_admin)


@pytest.fixture
def refresh_token_end_user(user_end_user) -> str:
    """Generate refresh token for END_USER"""
    return create_refresh_token(user_end_user)


@pytest.fixture
def auth_headers_end_user(access_token_end_user) -> Dict[str, str]:
    """Authorization headers for END_USER"""
    return {"Authorization": f"Bearer {access_token_end_user}"}


@pytest.fixture
def auth_headers_devops_engineer(access_token_devops_engineer) -> Dict[str, str]:
    """Authorization headers for DEVOPS_ENGINEER"""
    return {"Authorization": f"Bearer {access_token_devops_engineer}"}


@pytest.fixture
def auth_headers_team_lead(access_token_team_lead) -> Dict[str, str]:
    """Authorization headers for TEAM_LEAD"""
    return {"Authorization": f"Bearer {access_token_team_lead}"}


@pytest.fixture
def auth_headers_manager(access_token_manager) -> Dict[str, str]:
    """Authorization headers for MANAGER"""
    return {"Authorization": f"Bearer {access_token_manager}"}


@pytest.fixture
def auth_headers_admin(access_token_admin) -> Dict[str, str]:
    """Authorization headers for ADMIN"""
    return {"Authorization": f"Bearer {access_token_admin}"}


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service to prevent actual email sending"""
    sent_emails = []

    def mock_send_email(to_email, subject, body):
        sent_emails.append({
            "to": to_email,
            "subject": subject,
            "body": body
        })
        return True

    # Mock the email functions from utils
    monkeypatch.setattr("utils.send_verification_email", lambda email, token: mock_send_email(email, "Verify Email", token))
    monkeypatch.setattr("utils.send_welcome_email", lambda user: mock_send_email(user.email, "Welcome", "Welcome"))
    monkeypatch.setattr("utils.send_password_reset_email", lambda email, token: mock_send_email(email, "Reset Password", token))

    return sent_emails


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def valid_registration_data() -> Dict:
    """Valid registration data"""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewUser123!",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "+1-555-0200",
        "department": "Engineering"
    }


@pytest.fixture
def valid_login_data(user_end_user, password_plain) -> Dict:
    """Valid login credentials"""
    return {
        "username": user_end_user.username,
        "password": password_plain
    }


@pytest.fixture
def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-min-32-characters-long-for-testing"
    os.environ["EMAIL_VERIFICATION_REQUIRED"] = "false"
    yield
    # Cleanup not needed for environment variables
