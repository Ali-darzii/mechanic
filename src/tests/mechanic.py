from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from src.app import app
from src.models.user import UserRole
from src.services.mechanic import MechanicService
from src.services.mechanic_comment import MechanicCommnetService
from src.utils.auth import get_current_user


class _UserStub:
    def __init__(self, user_id: int, role: UserRole):
        self.id = user_id
        self.role = role
        self.is_active = True
        self.is_delete = False


class _MechanicServiceStub:
    def __init__(self, responses):
        self._responses = responses

    async def create(self, mechanic, user):
        result = self._responses["create"]
        if isinstance(result, Exception):
            raise result
        return result

    async def update(self, mechanic, user, partial):
        result = self._responses["update"]
        if isinstance(result, Exception):
            raise result
        return result

    async def list_all(self, limit, offset):
        result = self._responses["list_all"]
        if isinstance(result, Exception):
            raise result
        return result

    async def delete(self, user):
        result = self._responses.get("delete")
        if isinstance(result, Exception):
            raise result
        self._responses["delete_called"] = True


class _MechanicCommentServiceStub:
    def __init__(self, responses):
        self._responses = responses

    async def create(self, comment, user):
        result = self._responses["create"]
        if isinstance(result, Exception):
            raise result
        return result

    async def list_mechanic_comments(self, mechanic_id, limit, offset):
        result = self._responses["list"]
        if isinstance(result, Exception):
            raise result
        return result

    async def delete(self, user, comment_id):
        result = self._responses.get("delete")
        if isinstance(result, Exception):
            raise result
        self._responses["delete_called"] = True


def _client_with_overrides(user, mechanic_service=None, comment_service=None):
    app.dependency_overrides = {}
    app.dependency_overrides[get_current_user] = lambda: user
    if mechanic_service is not None:
        app.dependency_overrides[MechanicService] = lambda: mechanic_service
    if comment_service is not None:
        app.dependency_overrides[MechanicCommnetService] = lambda: comment_service
    return TestClient(app)


def _geom(x=51.39, y=35.69):
    return from_shape(Point(x, y), srid=4326)


def test_create_mechanic_returns_201():
    user = _UserStub(user_id=1, role=UserRole.user)
    responses = {
        "create": {
            "id": 10,
            "name": "Ali Garage",
            "description": "General repairs",
            "geom": _geom(),
        }
    }
    client = _client_with_overrides(user, mechanic_service=_MechanicServiceStub(responses))

    payload = {
        "name": "Ali Garage",
        "description": "General repairs",
        "geom": [51.39, 35.69],
        "key": "perm-key",
    }
    resp = client.post("/v1/mechanic", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 10
    assert body["name"] == "Ali Garage"
    assert body["geom"] == [51.39, 35.69]


def test_partial_update_mechanic_returns_201():
    user = _UserStub(user_id=1, role=UserRole.mechanic)
    responses = {
        "update": {
            "id": 10,
            "name": "Ali Garage Updated",
            "description": "General repairs",
            "geom": _geom(50.0, 34.0),
        }
    }
    client = _client_with_overrides(user, mechanic_service=_MechanicServiceStub(responses))

    payload = {"name": "Ali Garage Updated", "geom": [50.0, 34.0]}
    resp = client.patch("/v1/mechanic", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Ali Garage Updated"
    assert body["geom"] == [50.0, 34.0]


def test_list_all_mechanic_returns_200():
    user = _UserStub(user_id=1, role=UserRole.user)
    responses = {
        "list_all": [
            {
                "id": 10,
                "name": "Ali Garage",
                "description": "General repairs",
                "geom": _geom(),
            }
        ]
    }
    client = _client_with_overrides(user, mechanic_service=_MechanicServiceStub(responses))

    resp = client.get("/v1/mechanic?limit=10&offset=0")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == 10


def test_delete_mechanic_returns_204():
    user = _UserStub(user_id=1, role=UserRole.mechanic)
    responses = {"delete_called": False}
    service = _MechanicServiceStub(responses)
    client = _client_with_overrides(user, mechanic_service=service)

    resp = client.delete("/v1/mechanic")
    assert resp.status_code == 204
    assert responses["delete_called"] is True


def test_create_mechanic_comment_returns_201():
    user = _UserStub(user_id=2, role=UserRole.user)
    now = datetime.now(timezone.utc)
    responses = {
        "create": {
            "id": 5,
            "comment": "Great work",
            "rate": 5,
            "user_id": 2,
            "mechanic_request_id": 7,
            "parent_id": None,
            "created_at": now,
        }
    }
    client = _client_with_overrides(user, comment_service=_MechanicCommentServiceStub(responses))

    payload = {
        "comment": "Great work",
        "rate": 5,
        "mechanic_request_id": 7,
        "parent_id": None,
        "anonymous": False,
    }
    resp = client.post("/v1/mechanic/comment", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 5
    assert body["rate"] == 5


def test_list_mechanic_comments_returns_200():
    user = _UserStub(user_id=2, role=UserRole.user)
    now = datetime.now(timezone.utc)
    responses = {
        "list": [
            {
                "id": 5,
                "comment": "Great work",
                "rate": 5,
                "user": {"first_name": "Ali"},
                "mechanic_request": {
                    "id": 7,
                    "status": "delivered",
                    "issue": "motor",
                    "description": "Noise",
                    "mechanic_id": 3,
                    "car_id": 4,
                    "created_at": now,
                    "updated_at": None,
                },
                "parent_id": None,
                "created_at": now,
            }
        ]
    }
    client = _client_with_overrides(user, comment_service=_MechanicCommentServiceStub(responses))

    resp = client.get("/v1/mechanic/comment/3?limit=10&offset=0")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["mechanic_request"]["status"] == "delivered"


def test_delete_mechanic_comment_returns_204():
    user = _UserStub(user_id=2, role=UserRole.user)
    responses = {"delete_called": False}
    service = _MechanicCommentServiceStub(responses)
    client = _client_with_overrides(user, comment_service=service)

    resp = client.delete("/v1/mechanic/comment/5")
    assert resp.status_code == 204
    assert responses["delete_called"] is True
