"""
Test configuration and fixtures for FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test"""
    # Save original state
    original_activities = copy.deepcopy(activities)
    yield
    # Restore original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing"""
    return {
        "Test Activity": {
            "description": "A test activity for unit testing",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        }
    }