from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from datetime import timedelta
from flasgger import Swagger
import os 
from .swagger_config import swagger_template

from dotenv import load_dotenv
load_dotenv() # This loads the variables


# Global extension instances; initialized later inside the factory via init_app.
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name):
    # Create the Flask application instance (application factory pattern).
    app = Flask(__name__)

    # Enable CORS for local frontends, allowing cookies via supports_credentials.
    CORS(app, supports_credentials=True, origins=["http://localhost:3000", "https://localhost:3000"])

    # Core security and session settings; consider loading SECRET_KEY from env in production.
    app.config['SECRET_KEY'] = 'faedda1dcedc8a54042c86aaa6caf6b8'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)

    # Basic DB credentials (consider env vars or a config object per environment).
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    host = os.getenv('DB_HOST', 'localhost')


    # Environment-specific database URIs; testing enables Flask’s TESTING flag.
    if config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{user}:{password}@{host}/movie_munchers_prod'
    elif config_name == 'development':
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{user}:{password}@{host}/movie_munchers_dev'
    elif config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{user}:{password}@{host}/movie_munchers_test'
        app.config['TESTING'] = True

    # Disable event system overhead in SQLAlchemy.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the created app instance.
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = None  
    login_manager.session_protection = None  

    # Reload the user object from the stored session id for authenticated requests.
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Users
        return Users.query.filter_by(id=int(user_id)).first()

    # Standard unauthorized handler returning JSON 401 for API clients.
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Unauthorized - login required'}), 401

    # Initialize Swagger UI/OpenAPI using a shared template configuration.
    Swagger(app, template=swagger_template)

    # Import and register Blueprints after app creation to avoid circular imports.
    from app.routes.customer_routes import customer_bp
    from app.routes.user_routes import user_bp
    from app.routes.staff_routes import staff_bp
    from app.routes.supplier_routes import supplier_bp
    from app.routes.driver_routes import driver_bp
    from app.routes.coupon_routes import coupon_bp
    from app.routes.bundle_routes import bundle_bp

    # Attach blueprints; url_prefix is defined inside each blueprint.
    app.register_blueprint(customer_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(coupon_bp)
    app.register_blueprint(bundle_bp)

    # Create all database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Return the configured application instance.
    return app
