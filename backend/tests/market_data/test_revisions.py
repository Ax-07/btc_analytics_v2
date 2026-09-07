"""Tests unitaires du contrat applicatif de révisions P1E."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from btc_analytics.domain.market_data import Market, Timeframe
from btc_analytics.market_data.revisions import (
    RevisionFingerprintError,
    RevisionObservation,
    RevisionOperation,
    RevisionReference,
    ensure_consistent_fingerprint,
)

MARKET = Market(
    venue="binance",
    base_asset="BTC",
    quote_asset="USDC",
    market_type="spot",
    canonical_symbol="BTC-USDC-SPOT",
)
OPEN_TIME = datetime(2026, 9, 1, 0, 0, tzinfo=UTC)
END_TIME = datetime(2026, 9, 1, 1, 0, tzinfo=UTC)
OBSERVED_AT = datetime(2026, 9, 7, 12, 0, tzinfo=UTC)


def _observation(
    *,
    source: str = "ccxt:binance",
    fingerprint: str = "sha256:values",
) -> RevisionObservation:
    return RevisionObservation(
        market=MARKET,
        timeframe=Timeframe.H1,
        open_time=OPEN_TIME,
        end_time=END_TIME,
        available_at=END_TIME,
        open=Decimal("62000"),
        high=Decimal("62500"),
        low=Decimal("61800"),
        close=Decimal("62300"),
        base_volume=Decimal("123.45"),
        quote_volume=Decimal("7654321.0"),
        trade_count=100,
        source=source,
        source_symbol="BTC/USDC",
        observed_at=OBSERVED_AT,
        after_values_fingerprint=fingerprint,
    )


def test_logical_values_exclude_provider_provenance() -> None:
    first = _observation(source="ccxt:binance")
    second = _observation(source="native:binance")
    assert first.logical_values == second.logical_values


def test_identical_values_require_the_same_fingerprint() -> None:
    values = _observation().logical_values
    with pytest.raises(RevisionFingerprintError):
        ensure_consistent_fingerprint(
            logical_values=values,
            stored_logical_values=values,
            fingerprint="sha256:first",
            stored_fingerprint="sha256:second",
        )


def test_distinct_values_do_not_claim_idempotence() -> None:
    first = _observation()
    second_values = (
        Decimal("62001"),
        *first.logical_values[1:],
    )
    assert not ensure_consistent_fingerprint(
        logical_values=second_values,
        stored_logical_values=first.logical_values,
        fingerprint="sha256:changed",
        stored_fingerprint=first.after_values_fingerprint,
    )


def test_observation_requires_utc_timestamps() -> None:
    with pytest.raises(ValueError, match="observed_at"):
        RevisionObservation(
            market=MARKET,
            timeframe=Timeframe.H1,
            open_time=OPEN_TIME,
            end_time=END_TIME,
            available_at=END_TIME,
            open=Decimal("62000"),
            high=Decimal("62500"),
            low=Decimal("61800"),
            close=Decimal("62300"),
            base_volume=Decimal("123.45"),
            source="ccxt:binance",
            source_symbol="BTC/USDC",
            observed_at=datetime(2026, 9, 7, 12, 0),
            after_values_fingerprint="sha256:values",
        )


def test_revision_reference_rejects_invalid_sequence() -> None:
    with pytest.raises(ValueError, match="revision_seq"):
        RevisionReference(
            market=MARKET,
            timeframe=Timeframe.H1,
            open_time=OPEN_TIME,
            revision_seq=0,
        )


def test_operation_vocabulary_is_explicit_and_stable() -> None:
    assert {operation.value for operation in RevisionOperation} == {
        "initial_accepted",
        "current_unchanged",
        "pending_created",
        "pending_unchanged",
        "blocked_by_pending",
        "promoted",
        "already_promoted",
        "quarantined",
        "already_quarantined",
    }
