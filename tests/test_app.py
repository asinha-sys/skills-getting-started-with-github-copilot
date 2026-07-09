import pytest
import copy
from fastapi.testclient import TestClient

from src.app import app, activities


# Test data constants
TEST_EMAIL_UNREGISTERED = "backend-test@mergington.edu"
TEST_EMAIL_OTHER = "another-test@mergington.edu"
VALID_ACTIVITY = "Chess Club"
INVALID_ACTIVITY = "Nonexistent Club"


@pytest.fixture
def clean_activities():
    """Fixture that provides clean activities state for each test."""
    # Save the original state
    original_activities = copy.deepcopy(activities)
    
    yield  # Test runs here
    
    # Restore original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client(clean_activities):
    """Fixture that provides a TestClient with clean activities state."""
    return TestClient(app)


# ===== GET /activities Tests =====

def test_get_activities_returns_all_activities(client):
    # Arrange
    # No setup needed for this endpoint.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()
    assert "Gym Class" in response.json()


def test_get_activities_contains_expected_data(client):
    # Arrange
    # No setup needed for this endpoint.

    # Act
    response = client.get("/activities")

    # Assert
    activities_data = response.json()
    assert activities_data["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]


# ===== POST /activities/{activity_name}/signup Tests =====

def test_signup_successful(client):
    # Arrange
    activity_name = VALID_ACTIVITY
    email = TEST_EMAIL_UNREGISTERED

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()

    # Assert
    assert response.status_code == 200
    assert email in activities_data[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_duplicate_email_returns_400(client):
    # Arrange
    activity_name = VALID_ACTIVITY
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_invalid_activity_returns_404(client):
    # Arrange
    activity_name = INVALID_ACTIVITY
    email = TEST_EMAIL_UNREGISTERED

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_two_different_users_succeeds(client):
    # Arrange
    activity_name = "Programming Class"
    email1 = "user1-test@mergington.edu"
    email2 = "user2-test@mergington.edu"

    # Act
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email1},
    )
    response2 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email2},
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert email1 in activities_data[activity_name]["participants"]
    assert email2 in activities_data[activity_name]["participants"]


# ===== DELETE /activities/{activity_name}/signup Tests =====

def test_unregister_successful(client):
    # Arrange
    activity_name = VALID_ACTIVITY
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()

    # Assert
    assert response.status_code == 200
    assert email not in activities_data[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_invalid_activity_returns_404(client):
    # Arrange
    activity_name = INVALID_ACTIVITY
    email = TEST_EMAIL_UNREGISTERED

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_non_participant_returns_404(client):
    # Arrange
    activity_name = VALID_ACTIVITY
    email = TEST_EMAIL_UNREGISTERED  # Not in participants

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_signup_and_unregister_flow(client):
    # Arrange
    activity_name = "Art Club"
    email = TEST_EMAIL_UNREGISTERED

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()

    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    refreshed_response = client.get("/activities")
    refreshed_activities = refreshed_response.json()

    # Assert
    assert signup_response.status_code == 200
    assert email in activities_data[activity_name]["participants"]
    assert unregister_response.status_code == 200
    assert email not in refreshed_activities[activity_name]["participants"]
