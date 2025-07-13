import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db, Base


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "EcoRewards API" in response.json()["message"]


def test_register_user():
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


def test_register_duplicate_email():
    """Test registration with duplicate email"""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # First registration should succeed
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 200
    
    # Second registration with same email should fail
    response2 = client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400


def test_login():
    """Test user login"""
    # First register a user
    user_data = {
        "email": "login_test@example.com",
        "password": "TestPassword123",
        "first_name": "Login",
        "last_name": "Test"
    }
    
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    # Now test login
    login_data = {
        "email": "login_test@example.com",
        "password": "TestPassword123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_get_user_profile_without_auth():
    """Test getting user profile without authentication"""
    response = client.get("/api/v1/users/profile")
    assert response.status_code == 403  # Unauthorized


def test_get_user_profile_with_auth():
    """Test getting user profile with authentication"""
    # Register and login to get token
    user_data = {
        "email": "profile_test@example.com",
        "password": "TestPassword123",
        "first_name": "Profile",
        "last_name": "Test"
    }
    
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "profile_test@example.com",
        "password": "TestPassword123"
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "profile_test@example.com"


def test_get_branches():
    """Test getting branches list"""
    response = client.get("/api/v1/branches/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_rewards_catalog():
    """Test getting rewards catalog"""
    response = client.get("/api/v1/rewards/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ai_health_check():
    """Test AI service health check"""
    response = client.get("/api/v1/ai/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_password_validation():
    """Test password validation rules"""
    # Test weak password
    weak_password_data = {
        "email": "weak@example.com",
        "password": "weak",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=weak_password_data)
    assert response.status_code == 422  # Validation error


def test_invalid_email_format():
    """Test registration with invalid email format"""
    invalid_email_data = {
        "email": "invalid-email",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=invalid_email_data)
    assert response.status_code == 422  # Validation error
