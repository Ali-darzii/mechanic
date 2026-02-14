"""
Shared pytest fixtures for API unit and E2E tests.
"""
import os
import pytest

# Set test env before any config/app import so tests run without a real .env
_env = {
    "APP_HOST": "127.0.0.1",
    "APP_PORT": "8000",
    "DEBUG": "true",
    "SSL": "0",
    "SSL_CERT": "",
    "SSL_KEY": "",
    "SECRET_KEY": "test-secret-key-for-pytest",
    "JWT_ALGORITHM": "HS256",
    "ACCESS_EXPIRE": "1",
    "REFRESH_EXPIRE": "7",
    "OTP_EXPIRE": "300",
    "SMS_PANEL": "test",
    "SMS_ENDPOINT": "http://test",
    "SMS_USER": "test",
    "SMS_PASSWORD": "test",
    "SMS_ORIGINATOR": "test",
    "POSTGRE_HOST": "localhost",
    "POSTGRE_PORT": "5432",
    "POSTGRE_USER": "test",
    "POSTGRE_PASS": "test",
    "POSTGRE_DB": "test_db",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_BROKER_DB": "0",
    "REDIS_CACHE_DB": "1",
}
for k, v in _env.items():
    os.environ.setdefault(k, v)

from fastapi.testclient import TestClient
from src.app import app
from src.models.user import User as UserModel, UserRole
from src.utils.auth import get_current_user, get_current_user_with_permission


class UserStub:
    """Stub user for overriding get_current_user in tests."""
    def __init__(self, user_id: int = 1, role: UserRole = UserRole.user, phone_number: str = "09123456789"):
        self.id = user_id
        self.role = role
        self.phone_number = phone_number
        self.is_active = True
        self.is_delete = False
        self.first_name = "Test"
        self.last_name = "User"


@pytest.fixture
def client():
    """TestClient with no overrides (for E2E or auth tests)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def user_role():
    """Default user with role=user."""
    return UserStub(user_id=1, role=UserRole.user)


@pytest.fixture
def mechanic_role():
    """User with role=mechanic."""
    return UserStub(user_id=2, role=UserRole.mechanic)


@pytest.fixture
def admin_role():
    """User with role=admin."""
    return UserStub(user_id=3, role=UserRole.admin)


def client_with_user(user: UserStub):
    """Return TestClient with get_current_user overridden to return the given user."""
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    return TestClient(app)


def client_with_permission(role: UserRole, user_id: int = 1):
    """Return TestClient with user of given role (and get_current_user override)."""
    user = UserStub(user_id=user_id, role=role)
    return client_with_user(user)


def clear_overrides():
    """Clear all dependency overrides on app."""
    app.dependency_overrides.clear()
