"""
Unit tests for v1 permission API endpoints.
Tests: 200, 201, 403, 422.
"""
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.services.permission import MechanicPermissionService
from src.utils.auth import get_current_user
from src.tests.conftest import UserStub, clear_overrides
from src.models.user import UserRole


class _PermissionServiceStub:
    def __init__(self, responses):
        self._r = responses

    async def create(self, perm):
        if isinstance(self._r.get("create"), Exception):
            raise self._r["create"]
        return self._r.get("create", {"id": 1, "key": "key1", "user_id": 1, "created_at": datetime.now(timezone.utc), "used_at": None, "expires_at": datetime.now(timezone.utc)})

    async def list_all(self, limit, offset):
        if isinstance(self._r.get("list"), Exception):
            raise self._r["list"]
        return self._r.get("list", [])

    async def get_by_key(self, key):
        if isinstance(self._r.get("get"), Exception):
            raise self._r["get"]
        return self._r.get("get", {"id": 1, "key": key, "user_id": 1, "created_at": datetime.now(timezone.utc), "used_at": None, "expires_at": datetime.now(timezone.utc)})


def _perm_client(user=None, stub=None):
    clear_overrides()
    user = user or UserStub(user_id=1, role=UserRole.admin)
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    if stub is not None:
        app.dependency_overrides[MechanicPermissionService] = lambda: stub
    return TestClient(app)


def test_permission_create_mechanic_201():
    from datetime import timedelta
    expire = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
    stub = _PermissionServiceStub({"create": {"id": 1, "key": "k1", "user_id": 1, "created_at": datetime.now(timezone.utc).isoformat(), "used_at": None, "expires_at": expire}})
    client = _perm_client(stub=stub)
    resp = client.post("/v1/permission/mechanic", json={"user_id": 1, "expire_at": expire})
    assert resp.status_code == 201


def test_permission_create_400_expire_past():
    client = _perm_client()
    resp = client.post("/v1/permission/mechanic", json={"user_id": 1, "expire_at": "2020-01-01T00:00:00Z"})
    assert resp.status_code == 400


def test_permission_create_403_user_role():
    user = UserStub(user_id=1, role=UserRole.user)
    client = _perm_client(user=user)
    resp = client.post("/v1/permission/mechanic", json={"user_id": 1, "expire_at": "2030-01-01T00:00:00Z"})
    assert resp.status_code == 403


def test_permission_list_200():
    stub = _PermissionServiceStub({"list": []})
    client = _perm_client(stub=stub)
    resp = client.get("/v1/permission/mechanic?limit=10&offset=0")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_permission_list_403():
    user = UserStub(user_id=1, role=UserRole.user)
    client = _perm_client(user=user)
    resp = client.get("/v1/permission/mechanic")
    assert resp.status_code == 403


def test_permission_get_by_key_200():
    stub = _PermissionServiceStub({"get": {"id": 1, "key": "abc", "user_id": 1, "created_at": datetime.now(timezone.utc).isoformat(), "used_at": None, "expires_at": datetime.now(timezone.utc).isoformat()}})
    client = _perm_client(stub=stub)
    resp = client.get("/v1/permission/mechanic/abc")
    assert resp.status_code == 200
    assert resp.json()["key"] == "abc"


def test_permission_get_by_key_403():
    user = UserStub(user_id=1, role=UserRole.user)
    client = _perm_client(user=user)
    resp = client.get("/v1/permission/mechanic/somekey")
    assert resp.status_code == 403
