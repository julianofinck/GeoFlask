import pytest

from app import create_app, db
from app.config import TestConfig

from .test_database import DatabaseForTesting


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)

    # With context because it must run when app is running
    with app.app_context():
        # Put all of my models into my database
        db.create_all()

    yield app

    # With context because it must run when app is running
    with app.app_context():
        print("cloased")
        # Drop all of my models from my database
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


def pytest_configure(config):
    config.addinivalue_line("markers", "coverage: mark test to run with coverage")


def pytest_sessionstart(session):
    # Create test database
    test_db = DatabaseForTesting()
    test_db.create_test_database()


def pytest_sessionfinish(session, exitstatus):
    # Close test database
    test_db = DatabaseForTesting()
    test_db.delete_test_database()
