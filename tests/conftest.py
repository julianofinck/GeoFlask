import pytest

from app import create_app, db
from app.config import TestConfig

from .test_database import DatabaseForTesting


@pytest.fixture
def app():
    # Create test database
    with DatabaseForTesting() as test_db:
        app = create_app(TestConfig)

        # With context because it must run when app is running
        with app.app_context():
            # Put all of my models into my database
            db.create_all()

        yield app

        # With context because it must run when app is running
        with app.app_context():
            # Drop all of my models from my database
            db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def pytest_configure(config):
    config.addinivalue_line("markers", "coverage: mark test to run with coverage")
