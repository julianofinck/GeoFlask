import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DatabaseForTesting:
    def __init__(self):
        self.db_user = os.getenv("FLASK_TEST_DB_USERNAME", None)
        self.db_password = os.getenv("FLASK_TEST_DB_PASSWORD", None)
        self.db_name = os.getenv("FLASK_TEST_DB_NAME", None)
        self.db_hostname = os.getenv("FLASK_TEST_DB_HOSTNAME", None)
        self.db_port = os.getenv("FLASK_TEST_DB_PORT", None)

        self.create_test_database()

    def __del__(self):
        self.delete_test_database()

    def create_test_database(self):
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(
            host=self.db_hostname,
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASS"),
            port=self.db_port,
        )
        cursor = conn.cursor()

        # Create the database
        cursor.execute(f"CREATE DATABASE {self.db_name};")

        # Create the user and grant permissions on the database
        cursor.execute(
            f"CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}' SUPERUSER"
        )
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}"
        )

        # Enable PostGIS on the database
        cursor.execute(rf"\c {self.db_name}; CREATE EXTENSION IF NOT EXISTS postgis;")

        conn.commit()
        cursor.close()
        conn.close()

    def delete_test_database(self):
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(
            host=self.db_hostname,
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASS"),
            port=self.db_port,
        )
        cursor = conn.cursor()

        # Drop the user
        cursor.execute(f"DROP USER IF EXISTS {self.db_user}")

        # Drop the database
        cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")

        conn.commit()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    db_test = DatabaseForTesting()
    print(123)
