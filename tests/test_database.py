import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


class DatabaseForTesting:
    def __init__(self):
        self.db_user = os.getenv("FLASK_TEST_DB_USERNAME", None)
        self.db_password = os.getenv("FLASK_TEST_DB_PASSWORD", None)
        self.db_name = os.getenv("FLASK_TEST_DB_NAME", None)
        self.db_hostname = os.getenv("FLASK_TEST_DB_HOSTNAME", None)
        self.db_port = os.getenv("FLASK_TEST_DB_PORT", None)

    def __enter__(self):
        self.create_test_database()
        print("db created")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.delete_test_database()
        print("db deleted")

    def create_test_database(self):
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(
            host=self.db_hostname,
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASS"),
            port=self.db_port,
        )
        cursor = conn.cursor()

        # Prevent transactions
        conn.autocommit = True

        # Terminate connections
        cursor.execute(
            sql.SQL(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s"
            ),
            [self.db_name],
        )

        # Drop the database if it exists
        cursor.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.db_name))
        )

        # Create the database
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name))
        )

        # Drop the user if it exists
        cursor.execute(
            sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.db_user))
        )

        # Create the user and grant permissions on the database
        cursor.execute(
            f"CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}' SUPERUSER"
        )
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}"
        )

        self._enable_postgis()

        conn.commit()
        cursor.close()
        conn.close()

    def _enable_postgis(self):
        with psycopg2.connect(
            host=self.db_hostname,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            port=self.db_port,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    def delete_test_database(self):
        # Connect to PostgreSQL as postgres user
        conn = psycopg2.connect(
            host=self.db_hostname,
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASS"),
            port=self.db_port,
        )
        cursor = conn.cursor()
        conn.autocommit = True

        # Terminate connections
        cursor.execute(
            sql.SQL(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s"
            ),
            [self.db_name],
        )

        # Drop the database
        cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")

        # Drop the user
        cursor.execute(f"DROP USER IF EXISTS {self.db_user}")

        conn.commit()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    with DatabaseForTesting() as db_test:
        print("Breakpoint!")
