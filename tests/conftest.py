import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_state


@pytest.fixture
def client():
    original_activities = copy.deepcopy(activities_state)
    try:
        yield TestClient(app)
    finally:
        activities_state.clear()
        activities_state.update(copy.deepcopy(original_activities))
