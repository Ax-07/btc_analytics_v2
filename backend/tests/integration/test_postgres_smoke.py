"""Test smoke P1A de connectivité PostgreSQL."""

import os

import pytest
from sqlalchemy import text

from btc_analytics.storage.database import create_db_engine


@pytest.mark.integration
def test_postgres_connection() -> None:
    database_url = os.environ.get("BTC_ANALYTICS_DATABASE_URL")
    if database_url is None:
        pytest.skip("BTC_ANALYTICS_DATABASE_URL n’est pas configurée")

    engine = create_db_engine(database_url)
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT 1")) == 1
    finally:
        engine.dispose()
