"""
Unit tests for v1 mechanic/car/request API endpoints.
Tests: 200, 201, 204, 403, 422.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.services.mechanic_car_reqquest import MechanicCarRequstService
from src.utils.auth import get_current_user
from src.tests.conftest import UserStub, clear_overrides
from src.models.user import UserRole


class _MechanicCarRequestServiceStub:
    def __init__(self, responses):
        self._r = responses

    async def create(self, req, user):
        if isinstance(self._r.get("create"), Exception):
            raise self._r["create"]
        return self._r.get("create", {"id": 1, "status": "pending", "issue": "motor", "description": "Noise", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow(), "updated_at": None})

    async def update_by_user(self, req_id, req, user):
        if isinstance(self._r.get("update_user"), Exception):
            raise self._r["update_user"]
        return self._r.get("update_user", {"id": req_id, "status": "pending", "issue": "motor", "description": "Fixed", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow(), "updated_at": None})

    async def update_by_mechanic(self, req_id, req, user):
        if isinstance(self._r.get("update_mechanic"), Exception):
            raise self._r["update_mechanic"]
        return self._r.get("update_mechanic", {"id": req_id, "status": "confirmed", "issue": "motor", "description": "x", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow(), "updated_at": None})

    async def list_mechanic_reqeusts(self, user, limit, offset):
        if isinstance(self._r.get("list"), Exception):
            raise self._r["list"]
        return self._r.get("list", [])


def _mcr_client(user=None, stub=None):
    clear_overrides()
    user = user or UserStub(user_id=1, role=UserRole.user)
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    if stub is not None:
        app.dependency_overrides[MechanicCarRequstService] = lambda: stub
    return TestClient(app)


_valid_request = {"issue": "motor", "description": "Engine noise", "mechanic_id": 1, "car_id": 1}


def test_mechanic_car_request_create_201():
    stub = _MechanicCarRequestServiceStub({"create": {"id": 1, "status": "pending", "issue": "motor", "description": "Engine noise", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow().isoformat(), "updated_at": None}})
    client = _mcr_client(stub=stub)
    resp = client.post("/v1/mechanic/car/request", json=_valid_request)
    assert resp.status_code == 201
    assert resp.json()["issue"] == "motor"


def test_mechanic_car_request_create_403_mechanic():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    client = _mcr_client(user=user)
    resp = client.post("/v1/mechanic/car/request", json=_valid_request)
    assert resp.status_code == 403


def test_mechanic_car_request_create_422():
    client = _mcr_client()
    resp = client.post("/v1/mechanic/car/request", json={"issue": "motor", "description": "x"})  # missing mechanic_id, car_id
    assert resp.status_code == 422


def test_mechanic_car_request_update_by_user_200():
    stub = _MechanicCarRequestServiceStub({"update_user": {"id": 1, "status": "pending", "issue": "gear box", "description": "Fixed", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow().isoformat(), "updated_at": None}})
    client = _mcr_client(stub=stub)
    resp = client.patch("/v1/mechanic/car/request/user/1", json={"issue": "gear box", "description": "Fixed"})
    assert resp.status_code == 200


def test_mechanic_car_request_update_by_user_403():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    client = _mcr_client(user=user)
    resp = client.patch("/v1/mechanic/car/request/user/1", json={"issue": "motor", "description": "x"})
    assert resp.status_code == 403


def test_mechanic_car_request_update_by_mechanic_200():
    stub = _MechanicCarRequestServiceStub({"update_mechanic": {"id": 1, "status": "confirmed", "issue": "motor", "description": "x", "mechanic_id": 1, "car_id": 1, "created_at": datetime.utcnow().isoformat(), "updated_at": None}})
    client = _mcr_client(user=UserStub(user_id=1, role=UserRole.mechanic), stub=stub)
    resp = client.patch("/v1/mechanic/car/request/mechanic-user/1", json={"status": "confirmed"})
    assert resp.status_code == 200


def test_mechanic_car_request_update_by_mechanic_403():
    user = UserStub(user_id=1, role=UserRole.user)
    client = _mcr_client(user=user)
    resp = client.patch("/v1/mechanic/car/request/mechanic-user/1", json={"status": "confirmed"})
    assert resp.status_code == 403


def test_mechanic_car_request_list_200():
    stub = _MechanicCarRequestServiceStub({"list": []})
    client = _mcr_client(stub=stub)
    resp = client.get("/v1/mechanic/car/request?limit=10&offset=0")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
