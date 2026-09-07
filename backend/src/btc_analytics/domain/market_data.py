"""Primitives canoniques du domaine des données de marché."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum


class Timeframe(StrEnum):
    """Unités de temps natives canoniques de P1."""

    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

    @property
    def duration(self) -> timedelta:
        """Retourne la durée canonique de l'unité de temps."""
        if self is Timeframe.H1:
            return timedelta(hours=1)
        if self is Timeframe.H4:
            return timedelta(hours=4)
        return timedelta(days=1)

    def is_aligned(self, instant: datetime) -> bool:
        """Indique si un instant UTC est aligné sur la grille canonique."""
        _require_utc("instant", instant)
        if instant.minute != 0 or instant.second != 0 or instant.microsecond != 0:
            return False
        if self is Timeframe.H1:
            return True
        if self is Timeframe.H4:
            return instant.hour % 4 == 0
        return instant.hour == 0


class RevisionStatus(StrEnum):
    """États canoniques d'une ``CandleRevision``."""

    PENDING_CONFIRMATION = "pending_confirmation"
    ACCEPTED_CURRENT = "accepted_current"
    ACCEPTED_SUPERSEDED = "accepted_superseded"
    QUARANTINED = "quarantined"


@dataclass(frozen=True, slots=True, kw_only=True)
class Market:
    """Identité de marché indépendante de la notation fournisseur."""

    venue: str
    base_asset: str
    quote_asset: str
    market_type: str
    canonical_symbol: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("venue", self.venue),
            ("base_asset", self.base_asset),
            ("quote_asset", self.quote_asset),
            ("market_type", self.market_type),
            ("canonical_symbol", self.canonical_symbol),
        ):
            _require_non_blank(field_name, value)


@dataclass(frozen=True, slots=True, kw_only=True)
class Candle:
    """Bougie OHLCV canonique clôturée et révision courante acceptée."""

    market: Market
    timeframe: Timeframe
    open_time: datetime
    end_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    base_volume: Decimal
    source: str
    source_symbol: str
    available_at: datetime
    ingested_at: datetime
    current_revision_seq: int
    quote_volume: Decimal | None = None
    trade_count: int | None = None

    def __post_init__(self) -> None:
        _validate_candle_identity_times(self.timeframe, self.open_time, self.end_time)
        _require_utc("available_at", self.available_at)
        _require_utc("ingested_at", self.ingested_at)
        if self.available_at != self.end_time:
            raise ValueError("available_at doit être égal à end_time pour une bougie clôturée P1")
        _validate_ohlcv(
            self.open,
            self.high,
            self.low,
            self.close,
            self.base_volume,
            self.quote_volume,
            self.trade_count,
        )
        _require_non_blank("source", self.source)
        _require_non_blank("source_symbol", self.source_symbol)
        if self.current_revision_seq < 1:
            raise ValueError("current_revision_seq doit être supérieur ou égal à 1")

    @property
    def identity(self) -> tuple[Market, Timeframe, datetime]:
        """Retourne l'identité canonique stable de la bougie."""
        return (self.market, self.timeframe, self.open_time)


@dataclass(frozen=True, slots=True, kw_only=True)
class CandleRevision:
    """Observation versionnée append-only des valeurs logiques d'une bougie."""

    market: Market
    timeframe: Timeframe
    open_time: datetime
    revision_seq: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    base_volume: Decimal
    source: str
    source_symbol: str
    observed_at: datetime
    revision_status: RevisionStatus
    after_values_fingerprint: str
    quote_volume: Decimal | None = None
    trade_count: int | None = None
    accepted_at: datetime | None = None
    before_values_fingerprint: str | None = None
    confirmation_source: str | None = None
    audit_reason: str | None = None

    def __post_init__(self) -> None:
        _require_utc("open_time", self.open_time)
        if not self.timeframe.is_aligned(self.open_time):
            raise ValueError("open_time n'est pas aligné sur le timeframe canonique")
        _require_utc("observed_at", self.observed_at)
        if self.accepted_at is not None:
            _require_utc("accepted_at", self.accepted_at)
        if self.revision_seq < 1:
            raise ValueError("revision_seq doit être supérieur ou égal à 1")
        if self.revision_seq == 1 and self.revision_status in {
            RevisionStatus.PENDING_CONFIRMATION,
            RevisionStatus.QUARANTINED,
        }:
            raise ValueError("revision_seq = 1 doit représenter une révision acceptée")
        _validate_ohlcv(
            self.open,
            self.high,
            self.low,
            self.close,
            self.base_volume,
            self.quote_volume,
            self.trade_count,
        )
        _require_non_blank("source", self.source)
        _require_non_blank("source_symbol", self.source_symbol)
        _require_non_blank("after_values_fingerprint", self.after_values_fingerprint)
        if self.before_values_fingerprint is not None:
            _require_non_blank("before_values_fingerprint", self.before_values_fingerprint)
        if self.confirmation_source is not None:
            _require_non_blank("confirmation_source", self.confirmation_source)
        if self.audit_reason is not None:
            _require_non_blank("audit_reason", self.audit_reason)
        self._validate_acceptance_state()

    def _validate_acceptance_state(self) -> None:
        accepted = self.revision_status in {
            RevisionStatus.ACCEPTED_CURRENT,
            RevisionStatus.ACCEPTED_SUPERSEDED,
        }
        if accepted and self.accepted_at is None:
            raise ValueError("une révision acceptée doit posséder accepted_at")
        if not accepted and self.accepted_at is not None:
            raise ValueError("une révision pending/quarantined ne doit pas posséder accepted_at")
        if self.accepted_at is not None and self.observed_at > self.accepted_at:
            raise ValueError("observed_at doit être inférieur ou égal à accepted_at")

    @property
    def identity(self) -> tuple[Market, Timeframe, datetime, int]:
        """Retourne la référence locale exacte et stable de la révision."""
        return (self.market, self.timeframe, self.open_time, self.revision_seq)


def _validate_candle_identity_times(
    timeframe: Timeframe,
    open_time: datetime,
    end_time: datetime,
) -> None:
    _require_utc("open_time", open_time)
    _require_utc("end_time", end_time)
    if not timeframe.is_aligned(open_time):
        raise ValueError("open_time n'est pas aligné sur le timeframe canonique")
    if end_time != open_time + timeframe.duration:
        raise ValueError("end_time doit être égal à open_time + durée du timeframe")


def _validate_ohlcv(
    open_: Decimal,
    high: Decimal,
    low: Decimal,
    close: Decimal,
    base_volume: Decimal,
    quote_volume: Decimal | None,
    trade_count: int | None,
) -> None:
    values = {
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "base_volume": base_volume,
    }
    if quote_volume is not None:
        values["quote_volume"] = quote_volume
    for field_name, value in values.items():
        if not value.is_finite():
            raise ValueError(f"{field_name} doit être un Decimal fini")
    if high < max(open_, close, low):
        raise ValueError("high doit être supérieur ou égal à open, close et low")
    if low > min(open_, close, high):
        raise ValueError("low doit être inférieur ou égal à open, close et high")
    if base_volume < 0:
        raise ValueError("base_volume doit être positif ou nul")
    if quote_volume is not None and quote_volume < 0:
        raise ValueError("quote_volume doit être positif ou nul")
    if trade_count is not None and trade_count < 0:
        raise ValueError("trade_count doit être positif ou nul")


def _require_utc(field_name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} doit être un datetime timezone-aware en UTC")


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} ne doit pas être vide")
