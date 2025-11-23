import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Preserve the in-memory activities state between tests
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_rejection():
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # sign up succeeds
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # signing up again should be rejected (duplicate)
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_existing_and_not_found():
    activity = "Chess Club"
    # use an existing participant
    existing = app_module.activities[activity]["participants"][0]

    resp = client.delete(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 200
    assert existing not in app_module.activities[activity]["participants"]

    # deleting again should return 404
    resp2 = client.delete(f"/activities/{activity}/signup?email={existing}")
    assert resp2.status_code == 404
