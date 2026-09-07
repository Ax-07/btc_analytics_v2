"""Contrats internes d'accès aux données de marché fournisseur."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from btc_analytics.domain import Market, Timeframe

type ProviderNumber = int | float | str


class MarketDataProviderError(RuntimeError):
    """Erreur générique à la frontière d'un fournisseur de données de marché."""


class ProviderCapabilityError(MarketDataProviderError):
    """Le fournisseur ne possède pas une capacité requise par le contrat."""


class UnsupportedMarketError(MarketDataProviderError):
    """Le marché canonique demandé n'est pas configuré pour ce fournisseur."""


class ProviderDataError(MarketDataProviderError):
    """La réponse du fournisseur ne respecte pas la forme minimale attendue."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderOHLCV:
    """Observation OHLCV fournisseur stabilisée avant normalisation canonique."""

    market: Market
    timeframe: Timeframe
    source: str
    source_symbol: str
    open_time_ms: int
    open: ProviderNumber
    high: ProviderNumber
    low: ProviderNumber
    close: ProviderNumber
    base_volume: ProviderNumber
    observed_at: datetime

    def __post_init__(self) -> None:
        _require_non_blank("source", self.source)
        _require_non_blank("source_symbol", self.source_symbol)
        _require_non_negative_int("open_time_ms", self.open_time_ms)
        for field_name, value in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
            ("base_volume", self.base_volume),
        ):
            _require_provider_number(field_name, value)
        _require_utc("observed_at", self.observed_at)


class MarketDataProvider(Protocol):
    """Frontière interne synchrone pour l'accès aux OHLCV clôturés."""

    def fetch_closed_ohlcv(
        self,
        *,
        market: Market,
        timeframe: Timeframe,
        since: datetime,
        limit: int,
    ) -> tuple[ProviderOHLCV, ...]:
        """Récupère un lot borné d'observations OHLCV déjà clôturées."""
        ...


def _require_non_negative_int(field_name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} doit être un entier Unix en millisecondes")
    if value < 0:
        raise ValueError(f"{field_name} doit être positif ou nul")


def _require_provider_number(field_name: str, value: object) -> None:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} ne doit pas être un booléen")
    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{field_name} ne doit pas être une chaîne vide")
    if not isinstance(value, int | float | str):
        raise ValueError(f"{field_name} doit être un nombre ou une chaîne numérique fournisseur")


def _require_utc(field_name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} doit être un datetime timezone-aware en UTC")


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} ne doit pas être vide")
