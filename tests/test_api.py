"""
Tests for the FastAPI application endpoints
"""
import pytest
from src.app import activities


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test the structure of returned activities data"""
        response = client.get("/activities")
        data = response.json()
        
        # Test a specific activity structure
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Ensure student is not already registered
        assert email not in activities[activity_name]["participants"]
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student is now in participants list
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_registration(self, client, reset_activities):
        """Test signup when student is already registered"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_url_encoded_activity_name(self, client, reset_activities):
        """Test signup with URL-encoded activity name"""
        activity_name = "Programming Class"
        email = "newcoder@mergington.edu"
        
        # URL encode the activity name
        encoded_name = "Programming%20Class"
        
        response = client.post(f"/activities/{encoded_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student is registered
        assert email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Verify student is currently registered
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student is no longer in participants list
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister when student is not registered"""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Ensure student is not registered
        assert email not in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_url_encoded_activity_name(self, client, reset_activities):
        """Test unregister with URL-encoded activity name"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already registered
        
        # Verify student is currently registered
        assert email in activities[activity_name]["participants"]
        
        # URL encode the activity name
        encoded_name = "Programming%20Class"
        
        response = client.delete(f"/activities/{encoded_name}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student is no longer registered
        assert email not in activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete signup and unregister workflow"""
        activity_name = "Science Club"
        email = "workflow@mergington.edu"
        
        # Step 1: Verify initial state
        initial_participants = activities[activity_name]["participants"].copy()
        assert email not in initial_participants
        
        # Step 2: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Step 3: Verify signup reflected in activities endpoint
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        
        # Step 4: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Step 5: Verify unregistration reflected in activities endpoint
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
    
    def test_multiple_signups_different_activities(self, client, reset_activities):
        """Test student signing up for multiple activities"""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Science Club"]
        
        for activity_name in activities_to_join:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity_name in activities_to_join:
            assert email in activities_data[activity_name]["participants"]
    
    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that participant counts are tracked correctly"""
        activity_name = "Mathletes"  # Has max_participants: 10
        
        # Get initial state
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        initial_count = len(initial_data[activity_name]["participants"])
        max_participants = initial_data[activity_name]["max_participants"]
        
        # Add a new participant
        new_email = "mathwhiz@mergington.edu"
        signup_response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
        assert signup_response.status_code == 200
        
        # Verify count increased
        activities_response = client.get("/activities")
        updated_data = activities_response.json()
        new_count = len(updated_data[activity_name]["participants"])
        assert new_count == initial_count + 1
        assert new_count <= max_participants