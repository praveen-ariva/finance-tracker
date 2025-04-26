from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Finance Tracker API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.transactions import transactions_bp
    from app.api.categories import categories_bp
    from app.api.budgets import budgets_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(budgets_bp, url_prefix='/api/budgets')
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app