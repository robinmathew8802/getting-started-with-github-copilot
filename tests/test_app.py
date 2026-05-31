from urllib.parse import quote

from fastapi import status


def test_root_redirects_to_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_catalogue(client):
    response = client.get("/activities")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success(client):
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_email_returns_400(client):
    email = "dupstudent@mergington.edu"
    client.post("/activities/Chess Club/signup", params={"email": email})

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Activity/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success(client):
    activity_name = "Drama Club"
    email = "sophia@mergington.edu"
    path = f"/activities/{quote(activity_name)}/participants/{quote(email)}"

    response = client.delete(path)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    activity_name = "Chess Club"
    email = "unknownstudent@mergington.edu"
    path = f"/activities/{quote(activity_name)}/participants/{quote(email)}"

    response = client.delete(path)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Participant not found"


def test_unregister_missing_activity_returns_404(client):
    path = "/activities/Unknown%20Activity/participants/test%40mergington.edu"

    response = client.delete(path)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"
