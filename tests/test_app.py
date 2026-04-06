import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange - no special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on the in-memory data
    for name, activity in data.items():
        assert isinstance(activity, dict)
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


def test_signup_success(client):
    # Arrange
    email = "student@example.com"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up student@example.com for Chess Club"


def test_signup_activity_not_found(client):
    # Arrange
    email = "student@example.com"
    activity_name = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate(client):
    # Arrange
    email = "student@example.com"
    activity_name = "Chess Club"

    # Act - first signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Second signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_remove_participant_success(client):
    # Arrange
    email = "student@example.com"
    activity_name = "Chess Club"
    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Unregistered student@example.com from Chess Club"


def test_remove_participant_activity_not_found(client):
    # Arrange
    email = "student@example.com"
    activity_name = "NonExistent Activity"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_signed_up(client):
    # Arrange
    email = "student@example.com"
    activity_name = "Chess Club"
    # No signup

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]