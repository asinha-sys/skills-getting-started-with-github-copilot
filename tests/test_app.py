from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities_returns_data():
    # Arrange
    # No setup needed for this endpoint.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_and_unregister_flow():
    # Arrange
    activity_name = "Chess Club"
    email = "backend-test@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")
    activities = activities_response.json()

    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    refreshed_response = client.get("/activities")
    refreshed_activities = refreshed_response.json()

    # Assert
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert unregister_response.status_code == 200
    assert email not in refreshed_activities[activity_name]["participants"]
