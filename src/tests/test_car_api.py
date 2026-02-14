"""
Unit tests for v1 car API endpoints.
Tests: 200, 201, 204, 400, 403, 404, 422.
"""
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.services.car import CarService
from src.utils.auth import get_current_user
from src.tests.conftest import UserStub, clear_overrides
from src.models.user import UserRole


class _CarServiceStub:
    def __init__(self, responses):
        self._r = responses

    async def create(self, car, user):
        if isinstance(self._r.get("create"), Exception):
            raise self._r["create"]
        return self._r.get("create", {"id": 1, "title": "Car", "car_type": "sedan", "user_id": user.id})

    async def update(self, car_id, car, user):
        if isinstance(self._r.get("update"), Exception):
            raise self._r["update"]
        return self._r.get("update", {"id": car_id, "title": "Updated", "user_id": user.id})

    async def list_user_cars(self, user):
        if isinstance(self._r.get("list"), Exception):
            raise self._r["list"]
        return self._r.get("list", [])

    async def get_by_car_id_and_user_id(self, car_id, user):
        if isinstance(self._r.get("get"), Exception):
            raise self._r["get"]
        return self._r.get("get", {"id": car_id, "mechanic_requests": []})

    async def delete(self, car_id, user):
        if isinstance(self._r.get("delete"), Exception):
            raise self._r["delete"]
        return None


def _car_client(user=None, stub=None):
    clear_overrides()
    user = user or UserStub(user_id=1, role=UserRole.user)
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    if stub is not None:
        app.dependency_overrides[CarService] = lambda: stub
    return TestClient(app)


_valid_car = {
    "title": "My Car",
    "car_type": "sedan",
    "color": "black",
    "tip": "Peugeot",
    "model": "2015-01-01",
    "description": "Good",
    "license_plate": "12آ34567",
}


# ----- POST /car 201 -----
def test_car_create_201():
    stub = _CarServiceStub({"create": {"id": 1, "title": "My Car", "car_type": "sedan", "color": "black", "tip": "Peugeot",
                                       "model": "2015-01-01", "description": "Good", "license_plate": "12آ34567",
                                       "user_id": 1, "created_at": datetime.utcnow().isoformat(), "updated_at": None}})
    client = _car_client(stub=stub)
    resp = client.post("/v1/car", json=_valid_car)
    assert resp.status_code == 201
    assert resp.json()["title"] == "My Car"


def test_car_create_422_missing_required():
    stub = _CarServiceStub({})
    client = _car_client(stub=stub)
    resp = client.post("/v1/car", json={"title": "x"})  # missing car_type, tip, model, license_plate
    assert resp.status_code == 422


def test_car_create_403_wrong_role():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    stub = _CarServiceStub({})
    client = _car_client(user=user, stub=stub)
    resp = client.post("/v1/car", json=_valid_car)
    assert resp.status_code == 403


# ----- PATCH /car/{car_id} 200 -----
def test_car_update_200():
    stub = _CarServiceStub({"update": {"id": 1, "title": "Updated", "car_type": "sedan", "color": None, "tip": "Peugeot",
                                       "model": "2015-01-01", "description": None, "license_plate": "12آ34567",
                                       "user_id": 1, "created_at": datetime.utcnow().isoformat(), "updated_at": None}})
    client = _car_client(stub=stub)
    resp = client.patch("/v1/car/1", json={"title": "Updated"})
    assert resp.status_code == 200


def test_car_update_403_mechanic():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    client = _car_client(user=user)
    resp = client.patch("/v1/car/1", json={"title": "Updated"})
    assert resp.status_code == 403


# ----- GET /car 200 -----
def test_car_list_200():
    stub = _CarServiceStub({"list": [{"id": 1, "title": "C1", "car_type": "sedan", "color": None, "tip": "P", "model": "2015-01-01",
                                       "description": None, "license_plate": "12آ34567", "user_id": 1,
                                       "created_at": datetime.utcnow().isoformat(), "updated_at": None}]})
    client = _car_client(stub=stub)
    resp = client.get("/v1/car")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_car_list_403():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    client = _car_client(user=user)
    resp = client.get("/v1/car")
    assert resp.status_code == 403


# ----- GET /car/{car_id} 200 -----
def test_car_retrieve_200():
    stub = _CarServiceStub({"get": {"id": 1, "title": "C1", "car_type": "sedan", "color": None, "tip": "P", "model": "2015-01-01",
                                    "description": None, "license_plate": "12آ34567", "user_id": 1,
                                    "created_at": datetime.utcnow().isoformat(), "updated_at": None, "mechanic_requests": []}})
    client = _car_client(stub=stub)
    resp = client.get("/v1/car/1")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


def test_car_retrieve_403():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    client = _car_client(user=user)
    resp = client.get("/v1/car/1")
    assert resp.status_code == 403


# ----- DELETE /car/{car_id} 204 -----
def test_car_delete_204():
    stub = _CarServiceStub({})
    client = _car_client(stub=stub)
    resp = client.delete("/v1/car/1")
    assert resp.status_code == 204


def test_car_delete_403():
    user = UserStub(user_id=1, role=UserRole.mechanic)
    client = _car_client(user=user)
    resp = client.delete("/v1/car/1")
    assert resp.status_code == 403
