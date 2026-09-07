"""Tests d'intégration PostgreSQL du schéma canonique P1D."""

import os
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import IntegrityError

from btc_analytics.storage.database import create_db_engine
from btc_analytics.storage.schema import candle_revisions, candles, markets


def _database_url() -> str:
    database_url = os.environ.get("BTC_ANALYTICS_DATABASE_URL")
    if database_url is None:
        pytest.skip("BTC_ANALYTICS_DATABASE_URL n’est pas configurée")
    return database_url


@pytest.mark.integration
def test_market_data_schema_exists_after_alembic_upgrade() -> None:
    engine = create_db_engine(_database_url())
    try:
        inspector = inspect(engine)
        assert {"markets", "candles", "candle_revisions"} <= set(inspector.get_table_names())
    finally:
        engine.dispose()


@pytest.mark.integration
def test_initial_accepted_revision_and_current_candle_can_be_written_atomically() -> None:
    engine = create_db_engine(_database_url())
    open_time = datetime(2026, 9, 1, 0, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 1, 0, tzinfo=UTC)
    observed_at = datetime(2026, 9, 7, 12, 0, tzinfo=UTC)
    accepted_at = datetime(2026, 9, 7, 12, 0, 1, tzinfo=UTC)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                market_id = connection.execute(
                    markets.insert()
                    .values(
                        venue="binance",
                        base_asset="BTC",
                        quote_asset="USDC",
                        market_type="spot",
                        canonical_symbol="test:binance:BTC-USDC",
                    )
                    .returning(markets.c.market_id)
                ).scalar_one()

                connection.execute(
                    candles.insert().values(
                        market_id=market_id,
                        timeframe="1h",
                        open_time=open_time,
                        end_time=end_time,
                        available_at=end_time,
                        ingested_at=accepted_at,
                        current_revision_seq=1,
                    )
                )
                connection.execute(
                    candle_revisions.insert().values(
                        market_id=market_id,
                        timeframe="1h",
                        open_time=open_time,
                        revision_seq=1,
                        open=Decimal("62000"),
                        high=Decimal("62500"),
                        low=Decimal("61800"),
                        close=Decimal("62300"),
                        base_volume=Decimal("123.45"),
                        quote_volume=None,
                        trade_count=100,
                        source="ccxt.binance",
                        source_symbol="BTC/USDC",
                        observed_at=observed_at,
                        accepted_at=accepted_at,
                        revision_status="accepted_current",
                        before_values_fingerprint=None,
                        after_values_fingerprint="sha256:test",
                        confirmation_source=None,
                        audit_reason="initial_ingestion",
                    )
                )

                connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
                row = connection.execute(
                    select(
                        candles.c.current_revision_seq,
                        candle_revisions.c.revision_status,
                        candle_revisions.c.close,
                    ).join(
                        candle_revisions,
                        (candles.c.market_id == candle_revisions.c.market_id)
                        & (candles.c.timeframe == candle_revisions.c.timeframe)
                        & (candles.c.open_time == candle_revisions.c.open_time)
                        & (candles.c.current_revision_seq == candle_revisions.c.revision_seq),
                    )
                ).one()
                assert row.current_revision_seq == 1
                assert row.revision_status == "accepted_current"
                assert row.close == Decimal("62300")
            finally:
                transaction.rollback()
    finally:
        engine.dispose()


@pytest.mark.integration
def test_only_one_pending_revision_is_allowed_per_candle_lineage() -> None:
    engine = create_db_engine(_database_url())
    open_time = datetime(2026, 9, 1, 4, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 1, 5, 0, tzinfo=UTC)
    observed_at = datetime(2026, 9, 7, 12, 30, tzinfo=UTC)
    accepted_at = datetime(2026, 9, 7, 12, 30, 1, tzinfo=UTC)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                market_id = connection.execute(
                    markets.insert()
                    .values(
                        venue="binance",
                        base_asset="BTC",
                        quote_asset="USDC",
                        market_type="spot",
                        canonical_symbol="test:binance:BTC-USDC:pending",
                    )
                    .returning(markets.c.market_id)
                ).scalar_one()
                connection.execute(
                    candles.insert().values(
                        market_id=market_id,
                        timeframe="1h",
                        open_time=open_time,
                        end_time=end_time,
                        available_at=end_time,
                        ingested_at=accepted_at,
                        current_revision_seq=1,
                    )
                )
                connection.execute(
                    candle_revisions.insert().values(
                        market_id=market_id,
                        timeframe="1h",
                        open_time=open_time,
                        revision_seq=1,
                        open=Decimal("62000"),
                        high=Decimal("62500"),
                        low=Decimal("61800"),
                        close=Decimal("62300"),
                        base_volume=Decimal("123.45"),
                        source="ccxt.binance",
                        source_symbol="BTC/USDC",
                        observed_at=observed_at,
                        accepted_at=accepted_at,
                        revision_status="accepted_current",
                        after_values_fingerprint="sha256:current",
                    )
                )
                connection.execute(
                    candle_revisions.insert().values(
                        market_id=market_id,
                        timeframe="1h",
                        open_time=open_time,
                        revision_seq=2,
                        open=Decimal("62001"),
                        high=Decimal("62500"),
                        low=Decimal("61800"),
                        close=Decimal("62300"),
                        base_volume=Decimal("123.45"),
                        source="ccxt.binance",
                        source_symbol="BTC/USDC",
                        observed_at=observed_at,
                        accepted_at=None,
                        revision_status="pending_confirmation",
                        before_values_fingerprint="sha256:current",
                        after_values_fingerprint="sha256:pending-2",
                    )
                )

                with pytest.raises(IntegrityError):
                    with connection.begin_nested():
                        connection.execute(
                            candle_revisions.insert().values(
                                market_id=market_id,
                                timeframe="1h",
                                open_time=open_time,
                                revision_seq=3,
                                open=Decimal("62002"),
                                high=Decimal("62500"),
                                low=Decimal("61800"),
                                close=Decimal("62300"),
                                base_volume=Decimal("123.45"),
                                source="ccxt.binance",
                                source_symbol="BTC/USDC",
                                observed_at=observed_at,
                                accepted_at=None,
                                revision_status="pending_confirmation",
                                before_values_fingerprint="sha256:current",
                                after_values_fingerprint="sha256:pending-3",
                            )
                        )

                pending_count = connection.scalar(
                    select(func.count())
                    .select_from(candle_revisions)
                    .where(
                        candle_revisions.c.market_id == market_id,
                        candle_revisions.c.timeframe == "1h",
                        candle_revisions.c.open_time == open_time,
                        candle_revisions.c.revision_status == "pending_confirmation",
                    )
                )
                assert pending_count == 1
            finally:
                transaction.rollback()
    finally:
        engine.dispose()
