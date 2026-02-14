"""
End-to-end API tests.
Exercises all v1 endpoints with auth and service overrides to assert status codes
and response shapes without requiring a real DB/Redis.
"""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from src.app import app
from src.utils.auth import get_current_user
from src.services.auth import AuthService
from src.services.car import CarService
from src.services.mechanic import MechanicService
from src.services.permission import MechanicPermissionService
from src.services.mechanic_car_reqquest import MechanicCarRequstService
from src.services.mechanic_comment import MechanicCommnetService
from src.tests.conftest import UserStub, clear_overrides
from src.models.user import UserRole


# ---------- Fixtures: stub services that return valid shapes ----------
@pytest.fixture
def auth_stub():
    class Stub:
        async def signup_send_otp(self, s): pass
        async def signup_verify_otp(self, s): return {"access_token": "at", "refresh_token": "rt", "user_id": 1}
        async def login(self, l): return {"access_token": "at", "refresh_token": "rt", "user_id": 1}
        async def refresh_token(self, rt): return {"access_token": "at2", "refresh_token": "rt2", "user_id": 1}
        async def verify_token(self, t): return {"access_token": t, "token_type": "access"}
        async def revoke_token(self, rt, u): pass
        async def send_reset_password_token(self, r): pass
        async def verify_reset_password_token(self, r): pass
    return Stub()


@pytest.fixture
def car_stub():
    from src.schemas.car import CarOut
    d = {"id": 1, "title": "C", "car_type": "sedan", "color": None, "tip": "P", "model": "2015-01-01", "description": None, "license_plate": "12آ34567", "user_id": 1, "created_at": datetime.utcnow(), "updated_at": None}
    class Stub:
        async def create(self, c, u): return d
        async def update(self, i, c, u): return {**d, "id": i}
        async def list_user_cars(self, u): return [d]
        async def get_by_car_id_and_user_id(self, i, u): return {**d, "id": i, "mechanic_requests": []}
        async def delete(self, i, u): pass
    return Stub()


@pytest.fixture
def mechanic_stub():
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point
    _geom = from_shape(Point(51.39, 35.69), srid=4326)
    _row = {"id": 1, "name": "G", "description": "d", "geom": _geom}
    class Stub:
        async def create(self, m, u): return _row
        async def update(self, m, u, partial): return _row
        async def list_all(self, limit, offset): return [_row]
        async def delete(self, u): pass
    return Stub()


@pytest.fixture
def permission_stub():
    now = datetime.now(timezone.utc)
    class Stub:
        async def create(self, p): return {"id": 1, "key": "k", "user_id": 1, "created_at": now, "used_at": None, "expires_at": now}
        async def list_all(self, limit, offset): return []
        async def get_by_key(self, key): return {"id": 1, "key": key, "user_id": 1, "created_at": now, "used_at": None, "expires_at": now}
    return Stub()


@pytest.fixture
def mechanic_car_request_stub():
    class Stub:
        async def create(self, r, u): return {"id": 1, "status": "pending", "issue": "motor", "description": "d", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow(), "updated_at": None}
        async def update_by_user(self, i, r, u): return {"id": i, "status": "pending", "issue": "motor", "description": "d", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow(), "updated_at": None}
        async def update_by_mechanic(self, i, r, u): return {"id": i, "status": "confirmed", "issue": "motor", "description": "d", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow(), "updated_at": None}
        async def list_mechanic_reqeusts(self, u, limit, offset): return []
    return Stub()


@pytest.fixture
def mechanic_comment_stub():
    class Stub:
        async def create(self, c, u): return {"id": 1, "comment": "x", "rate": 5, "user_id": 1, "mechanic_request_id": 1, "parent_id": None, "created_at": datetime.utcnow()}
        async def list_mechanic_comments(self, mid, limit, offset): return []
        async def delete(self, u, cid): pass
    return Stub()


def _e2e_client(user=None, auth=None, car=None, mechanic=None, permission=None, mcr=None, comment=None):
    clear_overrides()
    user = user or UserStub(user_id=1, role=UserRole.user)
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    if auth is not None: app.dependency_overrides[AuthService] = lambda: auth
    if car is not None: app.dependency_overrides[CarService] = lambda: car
    if mechanic is not None: app.dependency_overrides[MechanicService] = lambda: mechanic
    if permission is not None: app.dependency_overrides[MechanicPermissionService] = lambda: permission
    if mcr is not None: app.dependency_overrides[MechanicCarRequstService] = lambda: mcr
    if comment is not None: app.dependency_overrides[MechanicCommnetService] = lambda: comment
    return TestClient(app)


# ---------- E2E: Auth ----------
def test_e2e_auth_send_otp_200(auth_stub):
    c = _e2e_client(auth=auth_stub)
    r = c.post("/v1/auth/send-otp", json={"phone_number": "09123456789", "password": "Pass123!@#", "first_name": "A", "last_name": "B"})
    assert r.status_code == 200


def test_e2e_auth_send_otp_400_or_422(auth_stub):
    c = _e2e_client(auth=auth_stub)
    r = c.post("/v1/auth/send-otp", json={"phone_number": "invalid", "password": "Pass123!@#", "first_name": "A", "last_name": "B"})
    assert r.status_code in (400, 422)


def test_e2e_auth_login_200(auth_stub):
    c = _e2e_client(auth=auth_stub)
    r = c.post("/v1/auth/token", json={"phone_number": "09123456789", "password": "Pass123!@#"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_e2e_auth_login_422(auth_stub):
    c = _e2e_client(auth=auth_stub)
    r = c.post("/v1/auth/token", json={})
    assert r.status_code == 422


def test_e2e_auth_token_verify_200(auth_stub):
    c = _e2e_client(auth=auth_stub)
    r = c.get("/v1/auth/token/verify", headers={"Authorization": "Bearer x"})
    assert r.status_code == 200


def test_e2e_auth_token_revoke_204(auth_stub):
    c = _e2e_client(auth=auth_stub)
    r = c.post("/v1/auth/token/revoke", json={"refresh_token": "rt"})
    assert r.status_code == 204


# ---------- E2E: Car ----------
def test_e2e_car_create_201(car_stub):
    c = _e2e_client(car=car_stub)
    r = c.post("/v1/car", json={"title": "C", "car_type": "sedan", "tip": "P", "model": "2015-01-01", "license_plate": "12آ34567"})
    assert r.status_code == 201


def test_e2e_car_list_200(car_stub):
    c = _e2e_client(car=car_stub)
    r = c.get("/v1/car")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_e2e_car_get_200(car_stub):
    c = _e2e_client(car=car_stub)
    r = c.get("/v1/car/1")
    assert r.status_code == 200


def test_e2e_car_update_200(car_stub):
    c = _e2e_client(car=car_stub)
    r = c.patch("/v1/car/1", json={"title": "Updated"})
    assert r.status_code == 200


def test_e2e_car_delete_204(car_stub):
    c = _e2e_client(car=car_stub)
    r = c.delete("/v1/car/1")
    assert r.status_code == 204


def test_e2e_car_403_mechanic(car_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.mechanic), car=car_stub)
    r = c.post("/v1/car", json={"title": "C", "car_type": "sedan", "tip": "P", "model": "2015-01-01", "license_plate": "12آ34567"})
    assert r.status_code == 403


# ---------- E2E: Mechanic ----------
def test_e2e_mechanic_create_201(mechanic_stub):
    c = _e2e_client(mechanic=mechanic_stub)
    r = c.post("/v1/mechanic", json={"name": "G", "description": "d", "geom": [51.39, 35.69], "key": "perm-key"})
    assert r.status_code == 201


def test_e2e_mechanic_list_200(mechanic_stub):
    c = _e2e_client(mechanic=mechanic_stub)
    r = c.get("/v1/mechanic?limit=10&offset=0")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_e2e_mechanic_patch_201(mechanic_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.mechanic), mechanic=mechanic_stub)
    r = c.patch("/v1/mechanic", json={"name": "Updated"})
    assert r.status_code == 201


def test_e2e_mechanic_delete_204(mechanic_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.mechanic), mechanic=mechanic_stub)
    r = c.delete("/v1/mechanic")
    assert r.status_code == 204


def test_e2e_mechanic_create_422(mechanic_stub):
    c = _e2e_client(mechanic=mechanic_stub)
    r = c.post("/v1/mechanic", json={"name": "G", "geom": [51], "key": "k"})  # geom length must be 2
    assert r.status_code == 422


# ---------- E2E: Permission ----------
def test_e2e_permission_create_201(permission_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.admin), permission=permission_stub)
    expire = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
    r = c.post("/v1/permission/mechanic", json={"user_id": 1, "expire_at": expire})
    assert r.status_code == 201


def test_e2e_permission_list_200(permission_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.admin), permission=permission_stub)
    r = c.get("/v1/permission/mechanic")
    assert r.status_code == 200


def test_e2e_permission_get_200(permission_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.admin), permission=permission_stub)
    r = c.get("/v1/permission/mechanic/somekey")
    assert r.status_code == 200


def test_e2e_permission_403(permission_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.user), permission=permission_stub)
    r = c.get("/v1/permission/mechanic/somekey")
    assert r.status_code == 403


# ---------- E2E: Mechanic car request ----------
def test_e2e_mcr_create_201(mechanic_car_request_stub):
    c = _e2e_client(mcr=mechanic_car_request_stub)
    r = c.post("/v1/mechanic/car/request", json={"issue": "motor", "description": "d", "mechanic_id": 1, "car_id": 1})
    assert r.status_code == 201


def test_e2e_mcr_list_200(mechanic_car_request_stub):
    c = _e2e_client(mcr=mechanic_car_request_stub)
    r = c.get("/v1/mechanic/car/request")
    assert r.status_code == 200


def test_e2e_mcr_update_user_200(mechanic_car_request_stub):
    c = _e2e_client(mcr=mechanic_car_request_stub)
    r = c.patch("/v1/mechanic/car/request/user/1", json={"issue": "motor", "description": "d"})
    assert r.status_code == 200


def test_e2e_mcr_update_mechanic_200(mechanic_car_request_stub):
    c = _e2e_client(user=UserStub(user_id=1, role=UserRole.mechanic), mcr=mechanic_car_request_stub)
    r = c.patch("/v1/mechanic/car/request/mechanic-user/1", json={"status": "confirmed"})
    assert r.status_code == 200


def test_e2e_mcr_create_422(mechanic_car_request_stub):
    c = _e2e_client(mcr=mechanic_car_request_stub)
    r = c.post("/v1/mechanic/car/request", json={"issue": "motor", "description": "d"})
    assert r.status_code == 422


# ---------- E2E: Mechanic comment ----------
def test_e2e_comment_create_201(mechanic_comment_stub):
    c = _e2e_client(comment=mechanic_comment_stub)
    r = c.post("/v1/mechanic/comment", json={"comment": "x", "rate": 5, "mechanic_request_id": 1})
    assert r.status_code == 201


def test_e2e_comment_list_200(mechanic_comment_stub):
    c = _e2e_client(comment=mechanic_comment_stub)
    r = c.get("/v1/mechanic/comment/1")
    assert r.status_code == 200


def test_e2e_comment_delete_204(mechanic_comment_stub):
    c = _e2e_client(comment=mechanic_comment_stub)
    r = c.delete("/v1/mechanic/comment/1")
    assert r.status_code == 204


def test_e2e_comment_create_422(mechanic_comment_stub):
    c = _e2e_client(comment=mechanic_comment_stub)
    r = c.post("/v1/mechanic/comment", json={"comment": "x", "rate": 10, "mechanic_request_id": 1})
    assert r.status_code == 422


# ---------- E2E: 401 Unauthorized (no/invalid token) ----------
def test_e2e_car_list_401_no_auth():
    """Protected endpoint without Authorization header returns 401 or 403."""
    clear_overrides()
    with TestClient(app) as c:
        r = c.get("/v1/car")
    assert r.status_code in (401, 403, 422)


def test_e2e_mechanic_list_401_invalid_token():
    """Invalid Bearer token returns 401."""
    clear_overrides()
    with TestClient(app) as c:
        r = c.get("/v1/mechanic", headers={"Authorization": "Bearer invalid-token"})
    assert r.status_code == 401
