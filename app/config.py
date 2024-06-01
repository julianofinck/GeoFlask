import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database configuration
    DB_ENGINE = os.getenv("DB_ENGINE")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_HOSTNAME = os.getenv("DB_HOSTNAME")
    DB_NAME = os.getenv("DB_NAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")

    # SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = (
        f"{DB_ENGINE}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
    )

    # Flask configuration
    DEBUG = True
    ENV = "development"  # "development" OR "production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    def __init__(self):
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = (
            "sqlite://"  # /:memory:'  # In-memory SQLite database for testing
        )
        self.create_test_database()

    def __del__(self):
        self.delete_test_database()
