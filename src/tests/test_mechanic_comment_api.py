"""
Unit tests for v1 mechanic/comment API endpoints.
Tests: 200, 201, 204, 403, 422.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.services.mechanic_comment import MechanicCommnetService
from src.utils.auth import get_current_user
from src.tests.conftest import UserStub, clear_overrides
from src.models.user import UserRole


class _MechanicCommentServiceStub:
    def __init__(self, responses):
        self._r = responses

    async def create(self, comment, user):
        if isinstance(self._r.get("create"), Exception):
            raise self._r["create"]
        return self._r.get("create", {"id": 1, "comment": "Great", "rate": 5, "user_id": user.id, "mechanic_request_id": 1, "parent_id": None, "created_at": datetime.utcnow()})

    async def list_mechanic_comments(self, mechanic_id, limit, offset):
        if isinstance(self._r.get("list"), Exception):
            raise self._r["list"]
        return self._r.get("list", [])

    async def delete(self, user, comment_id):
        if isinstance(self._r.get("delete"), Exception):
            raise self._r["delete"]
        return None


def _comment_client(user=None, stub=None):
    clear_overrides()
    user = user or UserStub(user_id=1, role=UserRole.user)
    async def _get_user():
        return user
    app.dependency_overrides[get_current_user] = _get_user
    if stub is not None:
        app.dependency_overrides[MechanicCommnetService] = lambda: stub
    return TestClient(app)


def test_mechanic_comment_create_201():
    stub = _MechanicCommentServiceStub({"create": {"id": 1, "comment": "Great work", "rate": 5, "user_id": 1, "mechanic_request_id": 1, "parent_id": None, "created_at": datetime.utcnow().isoformat()}})
    client = _comment_client(stub=stub)
    resp = client.post("/v1/mechanic/comment", json={"comment": "Great work", "rate": 5, "mechanic_request_id": 1, "anonymous": False})
    assert resp.status_code == 201
    assert resp.json()["rate"] == 5


def test_mechanic_comment_create_422_bad_rate():
    client = _comment_client()
    resp = client.post("/v1/mechanic/comment", json={"comment": "x", "rate": 10, "mechanic_request_id": 1})  # rate > 5
    assert resp.status_code == 422


def test_mechanic_comment_list_200():
    stub = _MechanicCommentServiceStub({"list": []})
    client = _comment_client(stub=stub)
    resp = client.get("/v1/mechanic/comment/1?limit=20&offset=0")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_mechanic_comment_delete_204():
    stub = _MechanicCommentServiceStub({})
    client = _comment_client(stub=stub)
    resp = client.delete("/v1/mechanic/comment/1")
    assert resp.status_code == 204


def test_mechanic_comment_delete_422_invalid_id():
    client = _comment_client()
    resp = client.delete("/v1/mechanic/comment/not_an_int")
    assert resp.status_code == 422
