import pytest
import uuid
from fastapi import status
from traceapi.crud import crud_user
from traceapi.schemas.user import UserCreate


class TestUserRegistration:
    """Test user registration endpoint"""

    def test_register_new_user_success(self, client, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/users/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["phone_number"] == sample_user_data["phone_number"]
        assert data["tier"] == "TIER_0"
        assert data["is_active"] is True
        assert "id" in data

    def test_register_duplicate_phone_number(self, client, db, sample_user_data):
        """Test registration with existing phone number"""
        # Create user first
        user_create = UserCreate(**sample_user_data)
        crud_user.create_user(db=db, user_in=user_create)
        
        # Try to register again
        response = client.post("/api/v1/users/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_register_invalid_phone_number(self, client):
        """Test registration with invalid phone number"""
        invalid_data = {"phone_number": "123456789", "pin": "1234"}
        response = client.post("/api/v1/users/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_pin(self, client):
        """Test registration with invalid PIN"""
        invalid_data = {"phone_number": "+2348012345678", "pin": "12"}
        response = client.post("/api/v1/users/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoint"""

    def test_login_success(self, client, db, sample_user_data):
        """Test successful login"""
        # Create user first
        user_create = UserCreate(**sample_user_data)
        crud_user.create_user(db=db, user_in=user_create)
        
        # Login
        response = client.post("/api/v1/users/login/token", json=sample_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_phone(self, client, db, sample_user_data):
        """Test login with wrong phone number"""
        # Create user first
        user_create = UserCreate(**sample_user_data)
        crud_user.create_user(db=db, user_in=user_create)
        
        # Login with wrong phone
        wrong_data = {"phone_number": "+2348087654321", "pin": "1234"}
        response = client.post("/api/v1/users/login/token", json=wrong_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_wrong_pin(self, client, db, sample_user_data):
        """Test login with wrong PIN"""
        # Create user first
        user_create = UserCreate(**sample_user_data)
        crud_user.create_user(db=db, user_in=user_create)
        
        # Login with wrong PIN
        wrong_data = {"phone_number": "+2348012345678", "pin": "9999"}
        response = client.post("/api/v1/users/login/token", json=wrong_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserProfile:
    """Test user profile endpoint"""

    def test_get_profile_success(self, client, db, sample_user_data):
        """Test getting user profile with valid token"""
        # Create user and login
        user_create = UserCreate(**sample_user_data)
        user = crud_user.create_user(db=db, user_in=user_create)
        
        login_response = client.post("/api/v1/users/login/token", json=sample_user_data)
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/profile", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone_number"] == sample_user_data["phone_number"]
        assert data["id"] == str(user.id)

    def test_get_profile_no_token(self, client):
        """Test getting profile without token"""
        response = client.get("/api/v1/users/profile")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/profile", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserById:
    """Test get user by ID endpoint"""

    def test_get_user_by_id_success(self, client, db, sample_user_data):
        """Test getting user by valid ID"""
        # Create user
        user_create = UserCreate(**sample_user_data)
        user = crud_user.create_user(db=db, user_in=user_create)
        
        # Get user by ID
        response = client.get(f"/api/v1/users/{user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(user.id)
        assert data["phone_number"] == sample_user_data["phone_number"]

    def test_get_user_by_id_not_found(self, client):
        """Test getting user by non-existent ID"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/users/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_get_user_by_invalid_id(self, client):
        """Test getting user by invalid UUID format"""
        response = client.get("/api/v1/users/invalid-uuid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY