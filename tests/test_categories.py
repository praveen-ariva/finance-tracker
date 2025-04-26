import json
import pytest
from app import create_app, db
from app.models.user import User
from app.models.category import Category

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

@pytest.fixture
def auth_token(client):
    # Register a user
    client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Login to get token
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    return data['access_token']

def test_create_category(client, auth_token):
    response = client.post(
        '/api/categories',
        data=json.dumps({
            'name': 'Groceries',
            'description': 'Food and household items',
            'color': '#00FF00'
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Category created successfully'
    assert data['category']['name'] == 'Groceries'
    assert data['category']['description'] == 'Food and household items'
    assert data['category']['color'] == '#00FF00'
    
    # Check that the category was actually stored in the database
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        category = Category.query.filter_by(user_id=user.id).first()
        assert category is not None
        assert category.name == 'Groceries'

def test_get_categories(client, auth_token):
    # First create a category
    client.post(
        '/api/categories',
        data=json.dumps({
            'name': 'Groceries',
            'description': 'Food and household items',
            'color': '#00FF00'
        }),
        headers={'Authorization': f'Bearer {auth_token}'},
        content_type='application/json'
    )
    
    # Get all categories
    response = client.get(
        '/api/categories',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'categories' in data
    assert len(data['categories']) == 1
    assert data['categories'][0]['name'] == 'Groceries'