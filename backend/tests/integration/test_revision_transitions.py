"""Tests PostgreSQL de la machine transactionnelle de révisions P1E."""

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from threading import Barrier
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import Engine, func, select

from btc_analytics.domain.market_data import Market, Timeframe
from btc_analytics.market_data.revisions import (
    RevisionObservation,
    RevisionOperation,
    RevisionPolicyError,
    RevisionTimestampError,
)
from btc_analytics.storage.database import create_db_engine
from btc_analytics.storage.revisions import PostgresRevisionStore
from btc_analytics.storage.schema import candle_revisions, candles, markets


class MutableClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value


@dataclass(slots=True)
class RevisionHarness:
    engine: Engine
    market: Market
    open_time: datetime
    observed_at: datetime
    clock: MutableClock
    store: PostgresRevisionStore


def _database_url() -> str:
    database_url = os.environ.get("BTC_ANALYTICS_DATABASE_URL")
    if database_url is None:
        pytest.skip("BTC_ANALYTICS_DATABASE_URL n’est pas configurée")
    return database_url


@pytest.fixture
def revision_harness() -> Iterator[RevisionHarness]:
    engine = create_db_engine(_database_url())
    unique = uuid4().hex
    market = Market(
        venue="binance",
        base_asset="BTC",
        quote_asset="USDC",
        market_type="spot",
        canonical_symbol=f"test:p1e:{unique}",
    )
    open_time = datetime(2026, 9, 1, 0, 0, tzinfo=UTC)
    observed_at = datetime(2026, 9, 7, 12, 0, tzinfo=UTC)
    clock = MutableClock(datetime(2026, 9, 7, 12, 5, tzinfo=UTC))
    harness = RevisionHarness(
        engine=engine,
        market=market,
        open_time=open_time,
        observed_at=observed_at,
        clock=clock,
        store=PostgresRevisionStore(engine, clock=clock),
    )
    try:
        yield harness
    finally:
        _cleanup_market(engine, market)
        engine.dispose()


def _observation(
    harness: RevisionHarness,
    *,
    price_delta: int = 0,
    fingerprint: str | None = None,
    source: str = "ccxt:binance",
    observed_delta_seconds: int = 0,
) -> RevisionObservation:
    delta = Decimal(price_delta)
    open_value = Decimal("62000") + delta
    return RevisionObservation(
        market=harness.market,
        timeframe=Timeframe.H1,
        open_time=harness.open_time,
        end_time=harness.open_time + timedelta(hours=1),
        available_at=harness.open_time + timedelta(hours=1),
        open=open_value,
        high=Decimal("62500") + delta,
        low=Decimal("61800") + delta,
        close=Decimal("62300") + delta,
        base_volume=Decimal("123.45") + delta,
        quote_volume=Decimal("7654321.0") + delta,
        trade_count=100 + price_delta,
        source=source,
        source_symbol="BTC/USDC",
        observed_at=harness.observed_at + timedelta(seconds=observed_delta_seconds),
        after_values_fingerprint=fingerprint or f"sha256:values:{price_delta}",
    )


def _market_id(engine: Engine, market: Market) -> int:
    with engine.connect() as connection:
        value = connection.execute(
            select(markets.c.market_id).where(
                markets.c.venue == market.venue,
                markets.c.base_asset == market.base_asset,
                markets.c.quote_asset == market.quote_asset,
                markets.c.market_type == market.market_type,
                markets.c.canonical_symbol == market.canonical_symbol,
            )
        ).scalar_one()
        return cast(int, value)


def _revision_rows(harness: RevisionHarness) -> list[dict[str, object]]:
    market_id = _market_id(harness.engine, harness.market)
    with harness.engine.connect() as connection:
        rows = (
            connection.execute(
                select(
                    candle_revisions.c.revision_seq,
                    candle_revisions.c.revision_status,
                    candle_revisions.c.observed_at,
                    candle_revisions.c.accepted_at,
                    candle_revisions.c.after_values_fingerprint,
                )
                .where(
                    candle_revisions.c.market_id == market_id,
                    candle_revisions.c.timeframe == Timeframe.H1.value,
                    candle_revisions.c.open_time == harness.open_time,
                )
                .order_by(candle_revisions.c.revision_seq)
            )
            .mappings()
            .all()
        )
    return [dict(row) for row in rows]


def _assert_current_integrity(harness: RevisionHarness) -> None:
    market_id = _market_id(harness.engine, harness.market)
    with harness.engine.connect() as connection:
        current_status = connection.execute(
            select(candle_revisions.c.revision_status)
            .select_from(
                candles.join(
                    candle_revisions,
                    (candles.c.market_id == candle_revisions.c.market_id)
                    & (candles.c.timeframe == candle_revisions.c.timeframe)
                    & (candles.c.open_time == candle_revisions.c.open_time)
                    & (candles.c.current_revision_seq == candle_revisions.c.revision_seq),
                )
            )
            .where(
                candles.c.market_id == market_id,
                candles.c.timeframe == Timeframe.H1.value,
                candles.c.open_time == harness.open_time,
            )
        ).scalar_one()
        assert current_status == "accepted_current"
        current_count = connection.scalar(
            select(func.count())
            .select_from(candle_revisions)
            .where(
                candle_revisions.c.market_id == market_id,
                candle_revisions.c.timeframe == Timeframe.H1.value,
                candle_revisions.c.open_time == harness.open_time,
                candle_revisions.c.revision_status == "accepted_current",
            )
        )
        pending_count = connection.scalar(
            select(func.count())
            .select_from(candle_revisions)
            .where(
                candle_revisions.c.market_id == market_id,
                candle_revisions.c.timeframe == Timeframe.H1.value,
                candle_revisions.c.open_time == harness.open_time,
                candle_revisions.c.revision_status == "pending_confirmation",
            )
        )
        assert current_count == 1
        assert pending_count in {0, 1}


@pytest.mark.integration
def test_initial_ingestion_and_current_reobservation_are_idempotent(
    revision_harness: RevisionHarness,
) -> None:
    first = revision_harness.store.observe(_observation(revision_harness))
    repeated = revision_harness.store.observe(
        _observation(revision_harness, source="another:provenance")
    )

    assert first.operation is RevisionOperation.INITIAL_ACCEPTED
    assert first.reference.revision_seq == 1
    assert repeated.operation is RevisionOperation.CURRENT_UNCHANGED
    rows = _revision_rows(revision_harness)
    assert len(rows) == 1
    assert rows[0]["revision_status"] == "accepted_current"
    assert rows[0]["observed_at"] == revision_harness.observed_at
    assert rows[0]["accepted_at"] == revision_harness.clock.value
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_pending_is_persisted_then_serializes_following_observations(
    revision_harness: RevisionHarness,
) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    same_pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    blocked = revision_harness.store.observe(_observation(revision_harness, price_delta=2))

    assert pending.operation is RevisionOperation.PENDING_CREATED
    assert pending.reference.revision_seq == 2
    assert same_pending.operation is RevisionOperation.PENDING_UNCHANGED
    assert blocked.operation is RevisionOperation.BLOCKED_BY_PENDING
    assert blocked.reference.revision_seq == 2
    rows = _revision_rows(revision_harness)
    assert [row["revision_status"] for row in rows] == [
        "accepted_current",
        "pending_confirmation",
    ]
    assert rows[1]["accepted_at"] is None
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_pending_survives_store_restart(revision_harness: RevisionHarness) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    created = revision_harness.store.observe(_observation(revision_harness, price_delta=1))

    restarted_store = PostgresRevisionStore(revision_harness.engine, clock=revision_harness.clock)
    recovered = restarted_store.get_pending(
        market=revision_harness.market,
        timeframe=Timeframe.H1,
        open_time=revision_harness.open_time,
    )

    assert recovered is not None
    assert recovered.reference == created.reference
    assert recovered.after_values_fingerprint == "sha256:values:1"
    assert recovered.observed_at == revision_harness.observed_at


@pytest.mark.integration
def test_quarantine_keeps_current_and_never_reuses_sequence(
    revision_harness: RevisionHarness,
) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    quarantined = revision_harness.store.quarantine(
        pending.reference,
        confirmation_source="native:binance",
        audit_reason="native_disagreement",
    )
    replay = revision_harness.store.quarantine(
        pending.reference,
        confirmation_source="native:binance",
        audit_reason="native_disagreement",
    )
    next_pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))

    assert quarantined.operation is RevisionOperation.QUARANTINED
    assert replay.operation is RevisionOperation.ALREADY_QUARANTINED
    assert next_pending.operation is RevisionOperation.PENDING_CREATED
    assert next_pending.reference.revision_seq == 3
    rows = _revision_rows(revision_harness)
    assert [row["revision_status"] for row in rows] == [
        "accepted_current",
        "quarantined",
        "pending_confirmation",
    ]
    assert rows[1]["accepted_at"] is None
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_promotion_is_atomic_and_replay_is_idempotent(revision_harness: RevisionHarness) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    revision_harness.clock.value = datetime(2026, 9, 7, 12, 10, tzinfo=UTC)

    promoted = revision_harness.store.promote(
        pending.reference,
        confirmation_source="native:binance",
        audit_reason="native_confirmation_agreed",
    )
    replay = revision_harness.store.promote(
        pending.reference,
        confirmation_source="native:binance",
        audit_reason="native_confirmation_agreed",
    )

    assert promoted.operation is RevisionOperation.PROMOTED
    assert replay.operation is RevisionOperation.ALREADY_PROMOTED
    rows = _revision_rows(revision_harness)
    assert [row["revision_status"] for row in rows] == [
        "accepted_superseded",
        "accepted_current",
    ]
    assert rows[1]["accepted_at"] == revision_harness.clock.value
    market_id = _market_id(revision_harness.engine, revision_harness.market)
    with revision_harness.engine.connect() as connection:
        candle_row = connection.execute(
            select(candles.c.current_revision_seq, candles.c.ingested_at).where(
                candles.c.market_id == market_id,
                candles.c.timeframe == Timeframe.H1.value,
                candles.c.open_time == revision_harness.open_time,
            )
        ).one()
    assert candle_row.current_revision_seq == 2
    assert candle_row.ingested_at == revision_harness.clock.value
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_quarantined_revision_cannot_be_promoted(revision_harness: RevisionHarness) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    revision_harness.store.quarantine(
        pending.reference,
        audit_reason="confirmation_unavailable",
    )

    with pytest.raises(RevisionPolicyError, match="pending_confirmation"):
        revision_harness.store.promote(
            pending.reference,
            confirmation_source="native:binance",
            audit_reason="late_confirmation",
        )
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_quarantine_rejects_invalid_current_pointer(revision_harness: RevisionHarness) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    market_id = _market_id(revision_harness.engine, revision_harness.market)

    with revision_harness.engine.begin() as connection:
        connection.execute(
            candles.update()
            .where(
                candles.c.market_id == market_id,
                candles.c.timeframe == Timeframe.H1.value,
                candles.c.open_time == revision_harness.open_time,
            )
            .values(current_revision_seq=pending.reference.revision_seq)
        )

    with pytest.raises(RevisionPolicyError, match="accepted_current"):
        revision_harness.store.quarantine(
            pending.reference,
            confirmation_source="native:binance",
            audit_reason="native_disagreement",
        )

    rows = _revision_rows(revision_harness)
    assert rows[1]["revision_status"] == "pending_confirmation"

    with revision_harness.engine.begin() as connection:
        connection.execute(
            candles.update()
            .where(
                candles.c.market_id == market_id,
                candles.c.timeframe == Timeframe.H1.value,
                candles.c.open_time == revision_harness.open_time,
            )
            .values(current_revision_seq=1)
        )
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_out_of_order_old_revision_result_is_rejected(revision_harness: RevisionHarness) -> None:
    initial = revision_harness.store.observe(_observation(revision_harness))
    pending = revision_harness.store.observe(_observation(revision_harness, price_delta=1))
    revision_harness.store.promote(
        pending.reference,
        confirmation_source="native:binance",
        audit_reason="native_confirmation_agreed",
    )
    revision_harness.store.observe(_observation(revision_harness, price_delta=2))

    with pytest.raises(RevisionPolicyError, match="pending_confirmation"):
        revision_harness.store.promote(
            initial.reference,
            confirmation_source="native:binance",
            audit_reason="stale_result",
        )
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_acceptance_timestamp_cannot_precede_observation(
    revision_harness: RevisionHarness,
) -> None:
    revision_harness.clock.value = revision_harness.observed_at - timedelta(seconds=1)
    with pytest.raises(RevisionTimestampError):
        revision_harness.store.observe(_observation(revision_harness))

    with revision_harness.engine.connect() as connection:
        count = connection.scalar(
            select(func.count())
            .select_from(markets)
            .where(markets.c.canonical_symbol == revision_harness.market.canonical_symbol)
        )
    assert count == 0


@pytest.mark.integration
def test_concurrent_initial_same_observation_creates_one_revision(
    revision_harness: RevisionHarness,
) -> None:
    barrier = Barrier(2)

    def worker() -> RevisionOperation:
        barrier.wait()
        return revision_harness.store.observe(_observation(revision_harness)).operation

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker), executor.submit(worker)]
        operations = {future.result() for future in futures}

    assert operations == {
        RevisionOperation.INITIAL_ACCEPTED,
        RevisionOperation.CURRENT_UNCHANGED,
    }
    assert len(_revision_rows(revision_harness)) == 1
    _assert_current_integrity(revision_harness)


@pytest.mark.integration
def test_concurrent_distinct_candidates_allocate_only_one_pending(
    revision_harness: RevisionHarness,
) -> None:
    revision_harness.store.observe(_observation(revision_harness))
    barrier = Barrier(2)

    def worker(price_delta: int) -> RevisionOperation:
        barrier.wait()
        return revision_harness.store.observe(
            _observation(revision_harness, price_delta=price_delta)
        ).operation

    with ThreadPoolExecutor(max_workers=2) as executor:
        operations = {
            future.result() for future in [executor.submit(worker, 1), executor.submit(worker, 2)]
        }

    assert operations == {
        RevisionOperation.PENDING_CREATED,
        RevisionOperation.BLOCKED_BY_PENDING,
    }
    rows = _revision_rows(revision_harness)
    assert [row["revision_seq"] for row in rows] == [1, 2]
    assert sum(row["revision_status"] == "pending_confirmation" for row in rows) == 1
    _assert_current_integrity(revision_harness)


def _cleanup_market(engine: Engine, market: Market) -> None:
    with engine.begin() as connection:
        market_id = connection.execute(
            select(markets.c.market_id).where(
                markets.c.venue == market.venue,
                markets.c.base_asset == market.base_asset,
                markets.c.quote_asset == market.quote_asset,
                markets.c.market_type == market.market_type,
                markets.c.canonical_symbol == market.canonical_symbol,
            )
        ).scalar_one_or_none()
        if market_id is None:
            return
        connection.execute(
            candle_revisions.delete().where(candle_revisions.c.market_id == market_id)
        )
        connection.execute(candles.delete().where(candles.c.market_id == market_id))
        connection.execute(markets.delete().where(markets.c.market_id == market_id))
