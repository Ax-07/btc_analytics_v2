"""Adaptateur CCXT synchrone pour les OHLCV publics de Binance Spot."""

from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Protocol, cast

from btc_analytics.domain import Market, Timeframe
from btc_analytics.market_data.provider import (
    MarketDataProviderError,
    ProviderCapabilityError,
    ProviderDataError,
    ProviderOHLCV,
    UnsupportedMarketError,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_SOURCE = "ccxt:binance"


class _CcxtExchange(Protocol):
    has: Mapping[str, object]
    timeframes: Mapping[str, object] | None

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: int | None = None,
        limit: int | None = None,
        params: Mapping[str, object] | None = None,
    ) -> list[list[object]]: ...


type Clock = Callable[[], datetime]


class CcxtBinanceMarketDataProvider:
    """Implémentation P1C de ``MarketDataProvider`` pour Binance Spot via CCXT."""

    def __init__(
        self,
        *,
        source_symbol_by_market: Mapping[Market, str],
        exchange: _CcxtExchange | None = None,
        clock: Clock | None = None,
    ) -> None:
        if not source_symbol_by_market:
            raise ValueError("source_symbol_by_market ne doit pas être vide")
        symbols: dict[Market, str] = {}
        for market, symbol in source_symbol_by_market.items():
            if not symbol.strip():
                raise ValueError("un source_symbol CCXT ne doit pas être vide")
            symbols[market] = symbol
        self._source_symbol_by_market = symbols
        self._exchange = exchange if exchange is not None else _new_ccxt_binance()
        self._clock = clock if clock is not None else _utc_now

    def fetch_closed_ohlcv(
        self,
        *,
        market: Market,
        timeframe: Timeframe,
        since: datetime,
        limit: int,
    ) -> tuple[ProviderOHLCV, ...]:
        """Récupère un lot explicite et exclut toute bougie encore ouverte."""
        _require_utc("since", since)
        validated_limit = _require_positive_int("limit", limit)

        try:
            source_symbol = self._source_symbol_by_market[market]
        except KeyError as exc:
            raise UnsupportedMarketError(
                "le marché demandé n'est pas configuré pour Binance"
            ) from exc

        if not self._exchange.has.get("fetchOHLCV"):
            raise ProviderCapabilityError("CCXT Binance ne déclare pas la capacité fetchOHLCV")
        timeframes = self._exchange.timeframes
        if timeframes is not None and timeframe.value not in timeframes:
            raise ProviderCapabilityError(
                f"le timeframe {timeframe.value} n'est pas déclaré par CCXT Binance"
            )

        since_ms = _datetime_to_unix_ms(since)
        request_started_at = self._clock()
        _require_utc("request_started_at", request_started_at)
        try:
            raw_rows = self._exchange.fetch_ohlcv(
                source_symbol,
                timeframe.value,
                since_ms,
                validated_limit,
                {},
            )
        except Exception as exc:
            raise MarketDataProviderError("échec de récupération OHLCV via CCXT Binance") from exc

        observed_at = self._clock()
        _require_utc("observed_at", observed_at)
        if observed_at < request_started_at:
            raise ValueError("observed_at ne doit pas précéder request_started_at")

        observations: list[ProviderOHLCV] = []
        for index, raw_row in enumerate(raw_rows):
            observation = _parse_row(
                raw_row,
                row_index=index,
                market=market,
                timeframe=timeframe,
                source_symbol=source_symbol,
                observed_at=observed_at,
            )
            if _is_closed(observation, request_started_at):
                observations.append(observation)
        return tuple(observations)


def _parse_row(
    raw_row: list[object],
    *,
    row_index: int,
    market: Market,
    timeframe: Timeframe,
    source_symbol: str,
    observed_at: datetime,
) -> ProviderOHLCV:
    if len(raw_row) < 6:
        raise ProviderDataError(
            f"la ligne OHLCV CCXT à l'index {row_index} contient moins de 6 éléments"
        )
    timestamp = raw_row[0]
    if isinstance(timestamp, bool) or not isinstance(timestamp, int):
        raise ProviderDataError(
            f"la ligne OHLCV CCXT à l'index {row_index} possède un timestamp invalide"
        )

    try:
        return ProviderOHLCV(
            market=market,
            timeframe=timeframe,
            source=_SOURCE,
            source_symbol=source_symbol,
            open_time_ms=timestamp,
            open=_as_provider_number(raw_row[1], row_index=row_index, field_name="open"),
            high=_as_provider_number(raw_row[2], row_index=row_index, field_name="high"),
            low=_as_provider_number(raw_row[3], row_index=row_index, field_name="low"),
            close=_as_provider_number(raw_row[4], row_index=row_index, field_name="close"),
            base_volume=_as_provider_number(
                raw_row[5],
                row_index=row_index,
                field_name="base_volume",
            ),
            observed_at=observed_at,
        )
    except ValueError as exc:
        raise ProviderDataError(f"la ligne OHLCV CCXT à l'index {row_index} est invalide") from exc


def _as_provider_number(value: object, *, row_index: int, field_name: str) -> int | float | str:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise ProviderDataError(
            f"{field_name} invalide dans la ligne OHLCV CCXT à l'index {row_index}"
        )
    if isinstance(value, str) and not value.strip():
        raise ProviderDataError(f"{field_name} vide dans la ligne OHLCV CCXT à l'index {row_index}")
    return value


def _is_closed(observation: ProviderOHLCV, observed_at: datetime) -> bool:
    open_time = _EPOCH + timedelta(milliseconds=observation.open_time_ms)
    return open_time + observation.timeframe.duration <= observed_at


def _datetime_to_unix_ms(value: datetime) -> int:
    return (value - _EPOCH) // timedelta(milliseconds=1)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _new_ccxt_binance() -> _CcxtExchange:
    ccxt_module = import_module("ccxt")
    factory = cast(
        Callable[[Mapping[str, object]], _CcxtExchange],
        getattr(ccxt_module, "binance"),
    )
    return factory(
        {
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
    )


def _require_positive_int(field_name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} doit être un entier strictement positif")
    return value


def _require_utc(field_name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} doit être un datetime timezone-aware en UTC")
