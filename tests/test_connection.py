import os

import psycopg2
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.config import TestConfig


def test_connect_false_database():
    engine = create_engine(
        TestConfig.SQLALCHEMY_DATABASE_URI + "data_base_does_not_exist"
    )

    with pytest.raises(OperationalError):
        conn = engine.connect()


def test_connect_real_database():
    engine = create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
    conn = engine.connect()
    conn.close()
