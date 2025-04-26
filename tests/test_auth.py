import json
import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully'
    assert 'user' in data
    assert data['user']['username'] == 'testuser'
    
    # Check that the user was actually stored in the database
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'

def test_login(client):
    # First register a user
    client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Then login
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Login successful'
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data
    assert data['user']['username'] == 'testuser'

def test_login_invalid_credentials(client):
    # First register a user
    client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Then try to login with wrong password
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid username or password'