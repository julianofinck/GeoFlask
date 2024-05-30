import pytest
from app.models import GeoData
from app.config import TestConfig
from app import create_app, db
from app.routes.ping import ping_bp
from app.routes.upload import upload_bp
from app.routes.geojson import geojson_bp

@pytest.fixture
def app():
    app = create_app(TestConfig)

    # With context because it must run when app is running
    with app.app_context():
        # Put all of my models into my database
        #db.create_all()
        pass
    
    yield app
    
    #db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()