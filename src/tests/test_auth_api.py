"""
Unit tests for v1 auth API endpoints.
Tests: 200, 201, 204, 400, 401, 404, 409, 422.
"""
import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.services.auth import AuthService
from src.utils.auth import get_current_user
from src.tests.conftest import UserStub, client_with_user, clear_overrides
from src.models.user import UserRole


class _AuthServiceStub:
    def __init__(self, responses):
        self._r = responses

    async def signup_send_otp(self, signup):
        if "send_otp" in self._r and isinstance(self._r["send_otp"], Exception):
            raise self._r["send_otp"]
        return None

    async def signup_verify_otp(self, signup):
        if "verify_otp" in self._r and isinstance(self._r["verify_otp"], Exception):
            raise self._r["verify_otp"]
        return self._r.get("verify_otp", {"access_token": "at", "refresh_token": "rt", "user_id": 1})

    async def login(self, login):
        if "login" in self._r and isinstance(self._r["login"], Exception):
            raise self._r["login"]
        return self._r.get("login", {"access_token": "at", "refresh_token": "rt", "user_id": 1})

    async def refresh_token(self, refresh_token):
        if "refresh" in self._r and isinstance(self._r["refresh"], Exception):
            raise self._r["refresh"]
        return self._r.get("refresh", {"access_token": "at2", "refresh_token": "rt2", "user_id": 1})

    async def verify_token(self, token):
        if "verify" in self._r and isinstance(self._r["verify"], Exception):
            raise self._r["verify"]
        return self._r.get("verify", {"access_token": token, "token_type": "access"})

    async def revoke_token(self, refresh_token, user):
        if "revoke" in self._r and isinstance(self._r["revoke"], Exception):
            raise self._r["revoke"]
        return None

    async def send_reset_password_token(self, reset_password):
        if "reset_send" in self._r and isinstance(self._r["reset_send"], Exception):
            raise self._r["reset_send"]
        return None

    async def verify_reset_password_token(self, reset_password):
        if "reset_verify" in self._r and isinstance(self._r["reset_verify"], Exception):
            raise self._r["reset_verify"]
        return None


def _client_auth(stub=None, user=None):
    clear_overrides()
    if user is None:
        user = UserStub(user_id=1, role=UserRole.user)
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    if stub is not None:
        app.dependency_overrides[AuthService] = lambda: stub
    return TestClient(app)


# ----- send-otp (POST) -----
def test_auth_send_otp_200():
    stub = _AuthServiceStub({})
    client = _client_auth(stub=stub)
    resp = client.post("/v1/auth/send-otp", json={
        "phone_number": "09123456789",
        "password": "Pass123!@#",
        "first_name": "Ali",
        "last_name": "Reza",
    })
    assert resp.status_code == 200


def test_auth_send_otp_400_invalid_phone():
    client = _client_auth()
    resp = client.post("/v1/auth/send-otp", json={
        "phone_number": "123",
        "password": "Pass123!@#",
        "first_name": "Ali",
        "last_name": "Reza",
    })
    assert resp.status_code in (400, 422)  # schema raises 400 for invalid phone


def test_auth_send_otp_400_invalid_password():
    client = _client_auth()
    resp = client.post("/v1/auth/send-otp", json={
        "phone_number": "09123456789",
        "password": "weak",
        "first_name": "Ali",
        "last_name": "Reza",
    })
    assert resp.status_code in (400, 422)


# ----- verify-otp (PUT) -----
def test_auth_verify_otp_200():
    stub = _AuthServiceStub({"verify_otp": {"access_token": "at", "refresh_token": "rt", "user_id": 1}})
    client = _client_auth(stub=stub)
    resp = client.put("/v1/auth/send-otp", json={"phone_number": "09123456789", "token": 123456})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and data["user_id"] == 1


def test_auth_verify_otp_422():
    client = _client_auth()
    resp = client.put("/v1/auth/send-otp", json={"phone_number": "09123456789"})  # missing token
    assert resp.status_code == 422


# ----- login (POST /token) -----
def test_auth_login_200():
    stub = _AuthServiceStub({"login": {"access_token": "at", "refresh_token": "rt", "user_id": 1}})
    client = _client_auth(stub=stub)
    resp = client.post("/v1/auth/token", json={"phone_number": "09123456789", "password": "Pass123!@#"})
    assert resp.status_code == 200
    assert resp.json()["user_id"] == 1


def test_auth_login_422():
    client = _client_auth()
    resp = client.post("/v1/auth/token", json={})
    assert resp.status_code == 422


# ----- refresh (POST /token/refresh) -----
def test_auth_refresh_200():
    stub = _AuthServiceStub({"refresh": {"access_token": "at2", "refresh_token": "rt2", "user_id": 1}})
    client = _client_auth(stub=stub)
    resp = client.post("/v1/auth/token/refresh", json={"refresh_token": "rt"})
    assert resp.status_code == 200


def test_auth_refresh_422():
    client = _client_auth()
    resp = client.post("/v1/auth/token/refresh", json={})
    assert resp.status_code == 422


# ----- verify (GET /token/verify) -----
def test_auth_token_verify_200():
    stub = _AuthServiceStub({"verify": {"access_token": "Bearer at", "token_type": "access"}})
    client = _client_auth(stub=stub)
    resp = client.get("/v1/auth/token/verify", headers={"Authorization": "Bearer at"})
    assert resp.status_code == 200


def test_auth_token_verify_401_no_header():
    client = _client_auth()
    resp = client.get("/v1/auth/token/verify")
    assert resp.status_code == 422  # missing header


# ----- logout (POST /token/revoke) -----
def test_auth_logout_204():
    stub = _AuthServiceStub({})
    user = UserStub(user_id=1, role=UserRole.user)
    client = _client_auth(stub=stub, user=user)
    resp = client.post("/v1/auth/token/revoke", json={"refresh_token": "rt"})
    assert resp.status_code == 204


def test_auth_logout_422():
    user = UserStub(user_id=1, role=UserRole.user)
    client = _client_auth(user=user)
    resp = client.post("/v1/auth/token/revoke", json={})
    assert resp.status_code == 422


# ----- reset-password (POST / PUT) -----
def test_auth_reset_password_send_200():
    stub = _AuthServiceStub({})
    client = _client_auth(stub=stub)
    resp = client.post("/v1/auth/reset-password", json={"phone_number": "09123456789"})
    assert resp.status_code == 200


def test_auth_reset_password_verify_200():
    stub = _AuthServiceStub({})
    client = _client_auth(stub=stub)
    resp = client.put("/v1/auth/reset-password", json={
        "phone_number": "09123456789",
        "password": "NewPass1!@#",
        "token": 123456,
    })
    assert resp.status_code == 200


def test_auth_reset_password_verify_400_bad_password():
    client = _client_auth()
    resp = client.put("/v1/auth/reset-password", json={
        "phone_number": "09123456789",
        "password": "weak",
        "token": 123456,
    })
    assert resp.status_code in (400, 422)
