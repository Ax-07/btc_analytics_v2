from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from btc_analytics.domain.market_data import (
    Candle,
    CandleRevision,
    Market,
    RevisionStatus,
    Timeframe,
)

MARKET = Market(
    venue="binance",
    base_asset="BTC",
    quote_asset="USDC",
    market_type="spot",
    canonical_symbol="BTC-USDC-SPOT",
)
OPEN_TIME = datetime(2026, 9, 7, 8, 0, tzinfo=UTC)
END_TIME = datetime(2026, 9, 7, 9, 0, tzinfo=UTC)

VALID_CANDLE = Candle(
    market=MARKET,
    timeframe=Timeframe.H1,
    open_time=OPEN_TIME,
    end_time=END_TIME,
    open=Decimal("110000.1"),
    high=Decimal("111000.2"),
    low=Decimal("109500.3"),
    close=Decimal("110500.4"),
    base_volume=Decimal("12.5"),
    quote_volume=Decimal("1381250.0"),
    trade_count=1250,
    source="ccxt:binance",
    source_symbol="BTC/USDC",
    available_at=END_TIME,
    ingested_at=END_TIME + timedelta(seconds=2),
    current_revision_seq=1,
)

VALID_REVISION = CandleRevision(
    market=MARKET,
    timeframe=Timeframe.H1,
    open_time=OPEN_TIME,
    revision_seq=1,
    open=VALID_CANDLE.open,
    high=VALID_CANDLE.high,
    low=VALID_CANDLE.low,
    close=VALID_CANDLE.close,
    base_volume=VALID_CANDLE.base_volume,
    quote_volume=VALID_CANDLE.quote_volume,
    trade_count=VALID_CANDLE.trade_count,
    source=VALID_CANDLE.source,
    source_symbol=VALID_CANDLE.source_symbol,
    observed_at=END_TIME + timedelta(seconds=1),
    accepted_at=END_TIME + timedelta(seconds=2),
    revision_status=RevisionStatus.ACCEPTED_CURRENT,
    after_values_fingerprint="fixture-values-v1",
)


def test_timeframes_are_exact_p1_native_values() -> None:
    assert [timeframe.value for timeframe in Timeframe] == ["1h", "4h", "1d"]
    assert Timeframe.H1.duration == timedelta(hours=1)
    assert Timeframe.H4.duration == timedelta(hours=4)
    assert Timeframe.D1.duration == timedelta(days=1)


def test_timeframe_alignment_is_utc_grid_based() -> None:
    assert Timeframe.H1.is_aligned(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    assert Timeframe.H4.is_aligned(datetime(2026, 9, 7, 8, 0, tzinfo=UTC))
    assert not Timeframe.H4.is_aligned(datetime(2026, 9, 7, 10, 0, tzinfo=UTC))
    assert Timeframe.D1.is_aligned(datetime(2026, 9, 7, 0, 0, tzinfo=UTC))
    assert not Timeframe.D1.is_aligned(datetime(2026, 9, 7, 4, 0, tzinfo=UTC))


def test_timeframe_rejects_non_utc_datetime() -> None:
    with pytest.raises(ValueError, match="UTC"):
        Timeframe.H1.is_aligned(datetime(2026, 9, 7, 8, 0))
    with pytest.raises(ValueError, match="UTC"):
        Timeframe.H1.is_aligned(datetime(2026, 9, 7, 8, 0, tzinfo=timezone(timedelta(hours=2))))


def test_market_is_hashable_identity_value() -> None:
    assert hash(MARKET) == hash(
        Market(
            venue="binance",
            base_asset="BTC",
            quote_asset="USDC",
            market_type="spot",
            canonical_symbol="BTC-USDC-SPOT",
        )
    )


def test_market_rejects_blank_identity_field() -> None:
    with pytest.raises(ValueError, match="canonical_symbol"):
        replace(MARKET, canonical_symbol="   ")


def test_candle_identity_matches_canonical_tuple() -> None:
    assert VALID_CANDLE.identity == (MARKET, Timeframe.H1, OPEN_TIME)
    assert VALID_CANDLE.available_at == VALID_CANDLE.end_time


def test_candle_requires_exact_interval_duration() -> None:
    with pytest.raises(ValueError, match=r"open_time \+ durée"):
        replace(
            VALID_CANDLE,
            end_time=END_TIME + timedelta(minutes=1),
            available_at=END_TIME + timedelta(minutes=1),
        )


def test_candle_requires_aligned_open_time() -> None:
    shifted = OPEN_TIME + timedelta(minutes=1)
    with pytest.raises(ValueError, match="aligné"):
        replace(
            VALID_CANDLE,
            open_time=shifted,
            end_time=shifted + timedelta(hours=1),
            available_at=shifted + timedelta(hours=1),
        )


def test_candle_requires_available_at_equal_end_time() -> None:
    with pytest.raises(ValueError, match="available_at"):
        replace(VALID_CANDLE, available_at=END_TIME + timedelta(seconds=1))


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("high", Decimal("109000")),
        ("low", Decimal("112000")),
        ("base_volume", Decimal("-0.1")),
        ("quote_volume", Decimal("-0.1")),
        ("trade_count", -1),
    ],
)
def test_candle_rejects_invalid_ohlcv(field_name: str, value: Decimal | int) -> None:
    with pytest.raises(ValueError):
        replace(VALID_CANDLE, **{field_name: value})


def test_candle_rejects_non_finite_decimal() -> None:
    with pytest.raises(ValueError, match="fini"):
        replace(VALID_CANDLE, close=Decimal("NaN"))


def test_candle_requires_positive_current_revision_sequence() -> None:
    with pytest.raises(ValueError, match="current_revision_seq"):
        replace(VALID_CANDLE, current_revision_seq=0)


def test_revision_identity_matches_exact_canonical_reference() -> None:
    assert VALID_REVISION.identity == (MARKET, Timeframe.H1, OPEN_TIME, 1)


def test_revision_status_values_match_p0_contract() -> None:
    assert {status.value for status in RevisionStatus} == {
        "pending_confirmation",
        "accepted_current",
        "accepted_superseded",
        "quarantined",
    }


def test_accepted_revision_requires_accepted_at() -> None:
    with pytest.raises(ValueError, match="accepted_at"):
        replace(VALID_REVISION, accepted_at=None)


def test_pending_revision_must_not_have_accepted_at() -> None:
    with pytest.raises(ValueError, match="pending/quarantined"):
        replace(
            VALID_REVISION,
            revision_seq=2,
            revision_status=RevisionStatus.PENDING_CONFIRMATION,
            before_values_fingerprint="fixture-values-v1",
            after_values_fingerprint="fixture-values-v2",
        )


def test_first_revision_cannot_be_pending_or_quarantined() -> None:
    for status in (RevisionStatus.PENDING_CONFIRMATION, RevisionStatus.QUARANTINED):
        with pytest.raises(ValueError, match="revision_seq = 1"):
            replace(VALID_REVISION, revision_status=status, accepted_at=None)


def test_quarantined_revision_without_accepted_at_is_valid() -> None:
    revision = replace(
        VALID_REVISION,
        revision_seq=2,
        revision_status=RevisionStatus.QUARANTINED,
        accepted_at=None,
        before_values_fingerprint="fixture-values-v1",
        after_values_fingerprint="fixture-values-v2",
        audit_reason="native_confirmation_disagreement",
    )
    assert revision.accepted_at is None
    assert revision.revision_seq == 2


def test_revision_rejects_acceptance_before_observation() -> None:
    with pytest.raises(ValueError, match="observed_at"):
        replace(VALID_REVISION, accepted_at=VALID_REVISION.observed_at - timedelta(microseconds=1))


def test_revision_sequence_starts_at_one_or_higher() -> None:
    with pytest.raises(ValueError, match="revision_seq"):
        replace(VALID_REVISION, revision_seq=0)
