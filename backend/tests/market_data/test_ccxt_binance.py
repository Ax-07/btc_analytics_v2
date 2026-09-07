"""Tests de la frontière P1C et de l'adaptateur CCXT Binance."""

import os
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import cast

import pytest

from btc_analytics.domain import Market, Timeframe
from btc_analytics.market_data import (
    CcxtBinanceMarketDataProvider,
    MarketDataProvider,
    MarketDataProviderError,
    ProviderCapabilityError,
    ProviderDataError,
    UnsupportedMarketError,
)

BINANCE_MARKET = Market(
    venue="binance",
    base_asset="BTC",
    quote_asset="USDC",
    market_type="spot",
    canonical_symbol="BTC-USDC-SPOT",
)


class FakeExchange:
    def __init__(
        self,
        rows: Sequence[Sequence[object]] | None = None,
        *,
        fetch_ohlcv_supported: bool = True,
        timeframes: Mapping[str, object] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.has: Mapping[str, object] = {"fetchOHLCV": fetch_ohlcv_supported}
        self.timeframes: Mapping[str, object] | None = (
            {"1h": "1h", "4h": "4h", "1d": "1d"} if timeframes is None else timeframes
        )
        self.rows: list[list[object]] = [] if rows is None else [list(row) for row in rows]
        self.error = error
        self.calls: list[tuple[str, str, int | None, int | None, Mapping[str, object] | None]] = []

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: int | None = None,
        limit: int | None = None,
        params: Mapping[str, object] | None = None,
    ) -> list[list[object]]:
        self.calls.append((symbol, timeframe, since, limit, params))
        if self.error is not None:
            raise self.error
        return self.rows


def fixed_clock() -> datetime:
    return datetime(2026, 9, 7, 12, 30, tzinfo=UTC)


def make_provider(exchange: FakeExchange) -> CcxtBinanceMarketDataProvider:
    return CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
        exchange=exchange,
        clock=fixed_clock,
    )


def test_adapter_satisfies_market_data_provider_protocol() -> None:
    provider: MarketDataProvider = make_provider(FakeExchange())

    assert provider is not None


def test_constructor_requires_market_mapping() -> None:
    with pytest.raises(ValueError, match="source_symbol_by_market"):
        CcxtBinanceMarketDataProvider(source_symbol_by_market={}, exchange=FakeExchange())


def test_constructor_rejects_blank_source_symbol() -> None:
    with pytest.raises(ValueError, match="source_symbol"):
        CcxtBinanceMarketDataProvider(
            source_symbol_by_market={BINANCE_MARKET: "   "},
            exchange=FakeExchange(),
        )


def test_fetch_requires_configured_market() -> None:
    provider = make_provider(FakeExchange())
    other_market = Market(
        venue="binance",
        base_asset="ETH",
        quote_asset="USDC",
        market_type="spot",
        canonical_symbol="ETH-USDC-SPOT",
    )

    with pytest.raises(UnsupportedMarketError):
        provider.fetch_closed_ohlcv(
            market=other_market,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 1, tzinfo=UTC),
            limit=2,
        )


def test_fetch_requires_utc_since() -> None:
    provider = make_provider(FakeExchange())

    with pytest.raises(ValueError, match="since"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 1),
            limit=2,
        )


@pytest.mark.parametrize("limit", [0, -1, True, 1.5, "2"])
def test_fetch_requires_strictly_positive_integer_limit(limit: object) -> None:
    provider = make_provider(FakeExchange())

    with pytest.raises(ValueError, match="limit"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 1, tzinfo=UTC),
            limit=cast(int, limit),
        )


def test_fetch_requires_ohlcv_capability() -> None:
    provider = make_provider(FakeExchange(fetch_ohlcv_supported=False))

    with pytest.raises(ProviderCapabilityError, match="fetchOHLCV"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 1, tzinfo=UTC),
            limit=2,
        )


def test_fetch_checks_declared_timeframe() -> None:
    provider = make_provider(FakeExchange(timeframes={"1h": "1h"}))

    with pytest.raises(ProviderCapabilityError, match="4h"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H4,
            since=datetime(2026, 9, 1, tzinfo=UTC),
            limit=2,
        )


def test_fetch_forwards_explicit_request_and_filters_open_candle() -> None:
    rows = [
        [1788778800000, 100.0, 105.0, 99.0, 103.0, 12.5],
        [1788782400000, 103.0, 106.0, 102.0, 104.0, 4.0],
    ]
    exchange = FakeExchange(rows)
    provider = make_provider(exchange)

    result = provider.fetch_closed_ohlcv(
        market=BINANCE_MARKET,
        timeframe=Timeframe.H1,
        since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
        limit=2,
    )

    assert exchange.calls == [("BTC/USDC", "1h", 1788778800000, 2, {})]
    assert len(result) == 1
    observation = result[0]
    assert observation.open_time_ms == 1788778800000
    assert observation.source == "ccxt:binance"
    assert observation.source_symbol == "BTC/USDC"
    assert observation.base_volume == 12.5
    assert observation.observed_at == fixed_clock()


def test_fetch_includes_candle_at_exact_close_boundary() -> None:
    provider = CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
        exchange=FakeExchange([[1788778800000, 100.0, 105.0, 99.0, 103.0, 12.5]]),
        clock=lambda: datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
    )

    result = provider.fetch_closed_ohlcv(
        market=BINANCE_MARKET,
        timeframe=Timeframe.H1,
        since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
        limit=1,
    )

    assert len(result) == 1


def test_fetch_excludes_candle_that_closes_while_request_is_in_flight() -> None:
    clock_values = iter(
        [
            datetime(2026, 9, 7, 11, 59, 59, tzinfo=UTC),
            datetime(2026, 9, 7, 12, 0, 1, tzinfo=UTC),
        ]
    )
    provider = CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
        exchange=FakeExchange([[1788778800000, 100.0, 105.0, 99.0, 103.0, 12.5]]),
        clock=lambda: next(clock_values),
    )

    result = provider.fetch_closed_ohlcv(
        market=BINANCE_MARKET,
        timeframe=Timeframe.H1,
        since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
        limit=1,
    )

    assert result == ()


def test_fetch_preserves_provider_order_and_gaps() -> None:
    rows = [
        [1788768000000, 100.0, 101.0, 99.0, 100.5, 1.0],
        [1788775200000, 102.0, 103.0, 101.0, 102.5, 2.0],
    ]
    provider = make_provider(FakeExchange(rows))

    result = provider.fetch_closed_ohlcv(
        market=BINANCE_MARKET,
        timeframe=Timeframe.H1,
        since=datetime(2026, 9, 7, 8, 0, tzinfo=UTC),
        limit=2,
    )

    assert [row.open_time_ms for row in result] == [1788768000000, 1788775200000]


def test_fetch_rejects_short_row() -> None:
    provider = make_provider(FakeExchange([[1788778800000, 100.0, 105.0]]))

    with pytest.raises(ProviderDataError, match="moins de 6"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )


@pytest.mark.parametrize("timestamp", ["1788778800000", True, 10.5])
def test_fetch_rejects_non_integer_timestamp(timestamp: object) -> None:
    provider = make_provider(FakeExchange([[timestamp, 100.0, 105.0, 99.0, 103.0, 12.5]]))

    with pytest.raises(ProviderDataError, match="timestamp"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )


@pytest.mark.parametrize("bad_value", [None, True, object(), "   "])
def test_fetch_rejects_invalid_provider_number(bad_value: object) -> None:
    provider = make_provider(FakeExchange([[1788778800000, bad_value, 105.0, 99.0, 103.0, 12.5]]))

    with pytest.raises(ProviderDataError):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )


def test_fetch_wraps_exchange_error() -> None:
    provider = make_provider(FakeExchange(error=RuntimeError("network")))

    with pytest.raises(MarketDataProviderError, match="CCXT Binance") as exc_info:
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )

    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_fetch_rejects_non_utc_request_started_clock() -> None:
    provider = CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
        exchange=FakeExchange(),
        clock=lambda: datetime(2026, 9, 7, 12, 30),
    )

    with pytest.raises(ValueError, match="request_started_at"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )


def test_fetch_rejects_non_utc_observed_at_clock() -> None:
    clock_values = iter(
        [
            datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
            datetime(2026, 9, 7, 12, 0, 1),
        ]
    )
    provider = CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
        exchange=FakeExchange(),
        clock=lambda: next(clock_values),
    )

    with pytest.raises(ValueError, match="observed_at"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )


def test_fetch_rejects_clock_regression_after_provider_call() -> None:
    clock_values = iter(
        [
            datetime(2026, 9, 7, 12, 0, 1, tzinfo=UTC),
            datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
        ]
    )
    provider = CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
        exchange=FakeExchange(),
        clock=lambda: next(clock_values),
    )

    with pytest.raises(ValueError, match="précéder request_started_at"):
        provider.fetch_closed_ohlcv(
            market=BINANCE_MARKET,
            timeframe=Timeframe.H1,
            since=datetime(2026, 9, 7, 11, 0, tzinfo=UTC),
            limit=1,
        )


@pytest.mark.binance_integration
@pytest.mark.skipif(
    os.environ.get("BTC_ANALYTICS_RUN_BINANCE_INTEGRATION") != "1",
    reason="BTC_ANALYTICS_RUN_BINANCE_INTEGRATION n'est pas activé",
)
def test_binance_public_ohlcv_smoke() -> None:
    provider = CcxtBinanceMarketDataProvider(
        source_symbol_by_market={BINANCE_MARKET: "BTC/USDC"},
    )

    result = provider.fetch_closed_ohlcv(
        market=BINANCE_MARKET,
        timeframe=Timeframe.H1,
        since=datetime(2026, 9, 1, tzinfo=UTC),
        limit=2,
    )

    assert result
    assert all(row.source == "ccxt:binance" for row in result)
    assert all(row.source_symbol == "BTC/USDC" for row in result)
    assert all(row.timeframe is Timeframe.H1 for row in result)
