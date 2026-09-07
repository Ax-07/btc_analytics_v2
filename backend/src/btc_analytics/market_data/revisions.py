"""Contrat applicatif P1E de gestion des révisions de bougies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from btc_analytics.domain.market_data import Market, Timeframe

LogicalCandleValues = tuple[
    Decimal,
    Decimal,
    Decimal,
    Decimal,
    Decimal,
    Decimal | None,
    int | None,
]


class RevisionOperation(StrEnum):
    """Résultats normaux des opérations transactionnelles P1E."""

    INITIAL_ACCEPTED = "initial_accepted"
    CURRENT_UNCHANGED = "current_unchanged"
    PENDING_CREATED = "pending_created"
    PENDING_UNCHANGED = "pending_unchanged"
    BLOCKED_BY_PENDING = "blocked_by_pending"
    PROMOTED = "promoted"
    ALREADY_PROMOTED = "already_promoted"
    QUARANTINED = "quarantined"
    ALREADY_QUARANTINED = "already_quarantined"


class RevisionPolicyError(RuntimeError):
    """État incohérent ou transition interdite par la politique D-020."""


class RevisionFingerprintError(RevisionPolicyError):
    """Deux valeurs logiquement identiques portent des fingerprints incompatibles."""


class RevisionTimestampError(RevisionPolicyError):
    """Un timestamp d'acceptation viole la causalité temporelle P0."""


@dataclass(frozen=True, slots=True, kw_only=True)
class RevisionObservation:
    """Observation canonique déjà normalisée et validée avant persistance P1E."""

    market: Market
    timeframe: Timeframe
    open_time: datetime
    end_time: datetime
    available_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    base_volume: Decimal
    source: str
    source_symbol: str
    observed_at: datetime
    after_values_fingerprint: str
    quote_volume: Decimal | None = None
    trade_count: int | None = None

    def __post_init__(self) -> None:
        _require_utc("open_time", self.open_time)
        _require_utc("end_time", self.end_time)
        _require_utc("available_at", self.available_at)
        _require_utc("observed_at", self.observed_at)
        if not self.timeframe.is_aligned(self.open_time):
            raise ValueError("open_time n'est pas aligné sur le timeframe canonique")
        if self.end_time != self.open_time + self.timeframe.duration:
            raise ValueError("end_time doit être égal à open_time + durée du timeframe")
        if self.available_at != self.end_time:
            raise ValueError("available_at doit être égal à end_time pour P1")
        _require_non_blank("source", self.source)
        _require_non_blank("source_symbol", self.source_symbol)
        _require_non_blank("after_values_fingerprint", self.after_values_fingerprint)

    @property
    def logical_values(self) -> LogicalCandleValues:
        """Valeurs qui définissent l'égalité logique d'une observation P1E."""
        return (
            self.open,
            self.high,
            self.low,
            self.close,
            self.base_volume,
            self.quote_volume,
            self.trade_count,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class RevisionReference:
    """Référence exacte et stable d'une ``CandleRevision``."""

    market: Market
    timeframe: Timeframe
    open_time: datetime
    revision_seq: int

    def __post_init__(self) -> None:
        _require_utc("open_time", self.open_time)
        if not self.timeframe.is_aligned(self.open_time):
            raise ValueError("open_time n'est pas aligné sur le timeframe canonique")
        if self.revision_seq < 1:
            raise ValueError("revision_seq doit être supérieur ou égal à 1")


@dataclass(frozen=True, slots=True, kw_only=True)
class PendingRevision:
    """Candidate pending persistée et récupérable après interruption."""

    reference: RevisionReference
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    base_volume: Decimal
    source: str
    source_symbol: str
    observed_at: datetime
    after_values_fingerprint: str
    quote_volume: Decimal | None = None
    trade_count: int | None = None
    before_values_fingerprint: str | None = None

    @property
    def logical_values(self) -> LogicalCandleValues:
        """Valeurs canoniques à confirmer contre la source native."""
        return (
            self.open,
            self.high,
            self.low,
            self.close,
            self.base_volume,
            self.quote_volume,
            self.trade_count,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class RevisionResult:
    """Résultat explicite d'une opération normale de la machine P1E."""

    operation: RevisionOperation
    reference: RevisionReference


class RevisionStore(Protocol):
    """Frontière de persistance transactionnelle des révisions."""

    def observe(self, observation: RevisionObservation) -> RevisionResult:
        """Persister/idempotencer une observation normalisée."""
        ...

    def get_pending(
        self,
        *,
        market: Market,
        timeframe: Timeframe,
        open_time: datetime,
    ) -> PendingRevision | None:
        """Retrouver l'unique candidate pending d'une lignée, si elle existe."""
        ...

    def promote(
        self,
        reference: RevisionReference,
        *,
        confirmation_source: str,
        audit_reason: str,
    ) -> RevisionResult:
        """Promouvoir une candidate exacte après confirmation native concordante."""
        ...

    def quarantine(
        self,
        reference: RevisionReference,
        *,
        audit_reason: str,
        confirmation_source: str | None = None,
    ) -> RevisionResult:
        """Mettre en quarantaine une candidate exacte sans modifier la current."""
        ...


def ensure_consistent_fingerprint(
    *,
    logical_values: LogicalCandleValues,
    stored_logical_values: LogicalCandleValues,
    fingerprint: str,
    stored_fingerprint: str,
) -> bool:
    """Comparer les valeurs et refuser deux fingerprints pour des valeurs identiques."""
    identical = logical_values == stored_logical_values
    if identical and fingerprint != stored_fingerprint:
        raise RevisionFingerprintError(
            "des valeurs logiquement identiques portent deux fingerprints différents"
        )
    return identical


def _require_utc(field_name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} doit être un datetime timezone-aware en UTC")


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} ne doit pas être vide")
