"""Implémentation PostgreSQL transactionnelle de la politique de révisions P1E."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast

from sqlalchemy import Connection, Engine, RowMapping, func, select, update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from btc_analytics.domain.market_data import Market, RevisionStatus, Timeframe
from btc_analytics.market_data.revisions import (
    LogicalCandleValues,
    PendingRevision,
    RevisionObservation,
    RevisionOperation,
    RevisionPolicyError,
    RevisionReference,
    RevisionResult,
    RevisionTimestampError,
    ensure_consistent_fingerprint,
)
from btc_analytics.storage.schema import candle_revisions, candles, markets


@dataclass(frozen=True, slots=True)
class _StoredRevision:
    revision_seq: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    base_volume: Decimal
    quote_volume: Decimal | None
    trade_count: int | None
    source: str
    source_symbol: str
    observed_at: datetime
    accepted_at: datetime | None
    revision_status: str
    before_values_fingerprint: str | None
    after_values_fingerprint: str

    @property
    def logical_values(self) -> LogicalCandleValues:
        return (
            self.open,
            self.high,
            self.low,
            self.close,
            self.base_volume,
            self.quote_volume,
            self.trade_count,
        )


class PostgresRevisionStore:
    """Store P1E sérialisé par lignée via ``SELECT ... FOR UPDATE``."""

    def __init__(
        self,
        engine: Engine,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._engine = engine
        self._clock = clock or _utc_now

    def observe(self, observation: RevisionObservation) -> RevisionResult:
        with self._engine.connect().execution_options(
            isolation_level="READ COMMITTED"
        ) as connection:
            with connection.begin():
                market_id = self._resolve_market_id(connection, observation.market)
                current_seq = self._lock_candle_current_seq(
                    connection,
                    market_id=market_id,
                    timeframe=observation.timeframe,
                    open_time=observation.open_time,
                )
                if current_seq is None:
                    self._lock_market(connection, market_id)
                    current_seq = self._lock_candle_current_seq(
                        connection,
                        market_id=market_id,
                        timeframe=observation.timeframe,
                        open_time=observation.open_time,
                    )
                    if current_seq is None:
                        return self._insert_initial(connection, market_id, observation)

                current = self._load_revision(
                    connection,
                    market_id=market_id,
                    timeframe=observation.timeframe,
                    open_time=observation.open_time,
                    revision_seq=current_seq,
                )
                if current.revision_status != RevisionStatus.ACCEPTED_CURRENT.value:
                    raise RevisionPolicyError(
                        "candles.current_revision_seq doit pointer une accepted_current"
                    )

                pending = self._load_pending(
                    connection,
                    market_id=market_id,
                    timeframe=observation.timeframe,
                    open_time=observation.open_time,
                )
                if pending is not None:
                    identical_to_pending = ensure_consistent_fingerprint(
                        logical_values=observation.logical_values,
                        stored_logical_values=pending.logical_values,
                        fingerprint=observation.after_values_fingerprint,
                        stored_fingerprint=pending.after_values_fingerprint,
                    )
                    operation = (
                        RevisionOperation.PENDING_UNCHANGED
                        if identical_to_pending
                        else RevisionOperation.BLOCKED_BY_PENDING
                    )
                    return RevisionResult(
                        operation=operation,
                        reference=self._reference(
                            observation.market,
                            observation.timeframe,
                            observation.open_time,
                            pending.revision_seq,
                        ),
                    )

                identical_to_current = ensure_consistent_fingerprint(
                    logical_values=observation.logical_values,
                    stored_logical_values=current.logical_values,
                    fingerprint=observation.after_values_fingerprint,
                    stored_fingerprint=current.after_values_fingerprint,
                )
                if identical_to_current:
                    return RevisionResult(
                        operation=RevisionOperation.CURRENT_UNCHANGED,
                        reference=self._reference(
                            observation.market,
                            observation.timeframe,
                            observation.open_time,
                            current.revision_seq,
                        ),
                    )

                next_seq = self._next_revision_seq(
                    connection,
                    market_id=market_id,
                    timeframe=observation.timeframe,
                    open_time=observation.open_time,
                )
                connection.execute(
                    candle_revisions.insert().values(
                        market_id=market_id,
                        timeframe=observation.timeframe.value,
                        open_time=observation.open_time,
                        revision_seq=next_seq,
                        open=observation.open,
                        high=observation.high,
                        low=observation.low,
                        close=observation.close,
                        base_volume=observation.base_volume,
                        quote_volume=observation.quote_volume,
                        trade_count=observation.trade_count,
                        source=observation.source,
                        source_symbol=observation.source_symbol,
                        observed_at=observation.observed_at,
                        accepted_at=None,
                        revision_status=RevisionStatus.PENDING_CONFIRMATION.value,
                        before_values_fingerprint=current.after_values_fingerprint,
                        after_values_fingerprint=observation.after_values_fingerprint,
                        confirmation_source=None,
                        audit_reason="source_values_changed",
                    )
                )
                return RevisionResult(
                    operation=RevisionOperation.PENDING_CREATED,
                    reference=self._reference(
                        observation.market,
                        observation.timeframe,
                        observation.open_time,
                        next_seq,
                    ),
                )

    def get_pending(
        self,
        *,
        market: Market,
        timeframe: Timeframe,
        open_time: datetime,
    ) -> PendingRevision | None:
        _require_utc("open_time", open_time)
        with self._engine.connect() as connection:
            market_id = self._find_market_id(connection, market)
            if market_id is None:
                return None
            pending = self._load_pending(
                connection,
                market_id=market_id,
                timeframe=timeframe,
                open_time=open_time,
            )
            if pending is None:
                return None
            return PendingRevision(
                reference=self._reference(market, timeframe, open_time, pending.revision_seq),
                open=pending.open,
                high=pending.high,
                low=pending.low,
                close=pending.close,
                base_volume=pending.base_volume,
                quote_volume=pending.quote_volume,
                trade_count=pending.trade_count,
                source=pending.source,
                source_symbol=pending.source_symbol,
                observed_at=pending.observed_at,
                before_values_fingerprint=pending.before_values_fingerprint,
                after_values_fingerprint=pending.after_values_fingerprint,
            )

    def promote(
        self,
        reference: RevisionReference,
        *,
        confirmation_source: str,
        audit_reason: str,
    ) -> RevisionResult:
        _require_non_blank("confirmation_source", confirmation_source)
        _require_non_blank("audit_reason", audit_reason)
        with self._engine.connect().execution_options(
            isolation_level="READ COMMITTED"
        ) as connection:
            with connection.begin():
                market_id = self._require_market_id(connection, reference.market)
                current_seq = self._require_locked_candle(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                )
                target = self._load_revision(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                    revision_seq=reference.revision_seq,
                )
                if target.revision_status == RevisionStatus.ACCEPTED_CURRENT.value:
                    if current_seq == reference.revision_seq:
                        return RevisionResult(
                            operation=RevisionOperation.ALREADY_PROMOTED,
                            reference=reference,
                        )
                    raise RevisionPolicyError(
                        "une accepted_current non pointée par la Candle est incohérente"
                    )
                if target.revision_status != RevisionStatus.PENDING_CONFIRMATION.value:
                    raise RevisionPolicyError(
                        "seule une révision pending_confirmation peut être promue"
                    )

                pending = self._load_pending(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                )
                if pending is None or pending.revision_seq != reference.revision_seq:
                    raise RevisionPolicyError("résultat de confirmation hors ordre")

                current = self._load_revision(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                    revision_seq=current_seq,
                )
                if current.revision_status != RevisionStatus.ACCEPTED_CURRENT.value:
                    raise RevisionPolicyError(
                        "candles.current_revision_seq doit pointer une accepted_current"
                    )

                accepted_at = self._accepted_now(target.observed_at)
                lineage = self._lineage_where(
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                )
                connection.execute(
                    update(candle_revisions)
                    .where(lineage, candle_revisions.c.revision_seq == current_seq)
                    .values(revision_status=RevisionStatus.ACCEPTED_SUPERSEDED.value)
                )
                connection.execute(
                    update(candle_revisions)
                    .where(lineage, candle_revisions.c.revision_seq == reference.revision_seq)
                    .values(
                        revision_status=RevisionStatus.ACCEPTED_CURRENT.value,
                        accepted_at=accepted_at,
                        confirmation_source=confirmation_source,
                        audit_reason=audit_reason,
                    )
                )
                connection.execute(
                    update(candles)
                    .where(
                        candles.c.market_id == market_id,
                        candles.c.timeframe == reference.timeframe.value,
                        candles.c.open_time == reference.open_time,
                    )
                    .values(
                        current_revision_seq=reference.revision_seq,
                        ingested_at=accepted_at,
                    )
                )
                return RevisionResult(
                    operation=RevisionOperation.PROMOTED,
                    reference=reference,
                )

    def quarantine(
        self,
        reference: RevisionReference,
        *,
        audit_reason: str,
        confirmation_source: str | None = None,
    ) -> RevisionResult:
        _require_non_blank("audit_reason", audit_reason)
        if confirmation_source is not None:
            _require_non_blank("confirmation_source", confirmation_source)
        with self._engine.connect().execution_options(
            isolation_level="READ COMMITTED"
        ) as connection:
            with connection.begin():
                market_id = self._require_market_id(connection, reference.market)
                current_seq = self._require_locked_candle(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                )
                current = self._load_revision(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                    revision_seq=current_seq,
                )
                if current.revision_status != RevisionStatus.ACCEPTED_CURRENT.value:
                    raise RevisionPolicyError(
                        "candles.current_revision_seq doit pointer une accepted_current"
                    )

                target = self._load_revision(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                    revision_seq=reference.revision_seq,
                )
                if target.revision_status == RevisionStatus.QUARANTINED.value:
                    return RevisionResult(
                        operation=RevisionOperation.ALREADY_QUARANTINED,
                        reference=reference,
                    )
                if target.revision_status != RevisionStatus.PENDING_CONFIRMATION.value:
                    raise RevisionPolicyError(
                        "seule une révision pending_confirmation peut être mise en quarantaine"
                    )
                pending = self._load_pending(
                    connection,
                    market_id=market_id,
                    timeframe=reference.timeframe,
                    open_time=reference.open_time,
                )
                if pending is None or pending.revision_seq != reference.revision_seq:
                    raise RevisionPolicyError("résultat de confirmation hors ordre")

                connection.execute(
                    update(candle_revisions)
                    .where(
                        self._lineage_where(
                            market_id=market_id,
                            timeframe=reference.timeframe,
                            open_time=reference.open_time,
                        ),
                        candle_revisions.c.revision_seq == reference.revision_seq,
                    )
                    .values(
                        revision_status=RevisionStatus.QUARANTINED.value,
                        confirmation_source=confirmation_source,
                        audit_reason=audit_reason,
                    )
                )
                return RevisionResult(
                    operation=RevisionOperation.QUARANTINED,
                    reference=reference,
                )

    def _insert_initial(
        self,
        connection: Connection,
        market_id: int,
        observation: RevisionObservation,
    ) -> RevisionResult:
        accepted_at = self._accepted_now(observation.observed_at)
        connection.execute(
            candles.insert().values(
                market_id=market_id,
                timeframe=observation.timeframe.value,
                open_time=observation.open_time,
                end_time=observation.end_time,
                available_at=observation.available_at,
                ingested_at=accepted_at,
                current_revision_seq=1,
            )
        )
        connection.execute(
            candle_revisions.insert().values(
                market_id=market_id,
                timeframe=observation.timeframe.value,
                open_time=observation.open_time,
                revision_seq=1,
                open=observation.open,
                high=observation.high,
                low=observation.low,
                close=observation.close,
                base_volume=observation.base_volume,
                quote_volume=observation.quote_volume,
                trade_count=observation.trade_count,
                source=observation.source,
                source_symbol=observation.source_symbol,
                observed_at=observation.observed_at,
                accepted_at=accepted_at,
                revision_status=RevisionStatus.ACCEPTED_CURRENT.value,
                before_values_fingerprint=None,
                after_values_fingerprint=observation.after_values_fingerprint,
                confirmation_source=None,
                audit_reason="initial_ingestion",
            )
        )
        return RevisionResult(
            operation=RevisionOperation.INITIAL_ACCEPTED,
            reference=self._reference(
                observation.market,
                observation.timeframe,
                observation.open_time,
                1,
            ),
        )

    def _resolve_market_id(self, connection: Connection, market: Market) -> int:
        existing = self._find_market_id(connection, market)
        if existing is not None:
            return existing
        statement = (
            postgresql_insert(markets)
            .values(
                venue=market.venue,
                base_asset=market.base_asset,
                quote_asset=market.quote_asset,
                market_type=market.market_type,
                canonical_symbol=market.canonical_symbol,
            )
            .on_conflict_do_nothing(constraint="uq_markets_domain_identity")
            .returning(markets.c.market_id)
        )
        inserted = connection.execute(statement).scalar_one_or_none()
        if inserted is not None:
            return cast(int, inserted)
        existing = self._find_market_id(connection, market)
        if existing is None:
            raise RevisionPolicyError("impossible de résoudre le market_id canonique")
        return existing

    def _find_market_id(self, connection: Connection, market: Market) -> int | None:
        value = connection.execute(
            select(markets.c.market_id).where(
                markets.c.venue == market.venue,
                markets.c.base_asset == market.base_asset,
                markets.c.quote_asset == market.quote_asset,
                markets.c.market_type == market.market_type,
                markets.c.canonical_symbol == market.canonical_symbol,
            )
        ).scalar_one_or_none()
        if value is None:
            return None
        return cast(int, value)

    def _require_market_id(self, connection: Connection, market: Market) -> int:
        market_id = self._find_market_id(connection, market)
        if market_id is None:
            raise RevisionPolicyError("marché inconnu pour cette référence de révision")
        return market_id

    def _lock_market(self, connection: Connection, market_id: int) -> None:
        locked = connection.execute(
            select(markets.c.market_id).where(markets.c.market_id == market_id).with_for_update()
        ).scalar_one_or_none()
        if locked is None:
            raise RevisionPolicyError("market_id disparu pendant la transaction")

    def _lock_candle_current_seq(
        self,
        connection: Connection,
        *,
        market_id: int,
        timeframe: Timeframe,
        open_time: datetime,
    ) -> int | None:
        value = connection.execute(
            select(candles.c.current_revision_seq)
            .where(
                candles.c.market_id == market_id,
                candles.c.timeframe == timeframe.value,
                candles.c.open_time == open_time,
            )
            .with_for_update()
        ).scalar_one_or_none()
        if value is None:
            return None
        return cast(int, value)

    def _require_locked_candle(
        self,
        connection: Connection,
        *,
        market_id: int,
        timeframe: Timeframe,
        open_time: datetime,
    ) -> int:
        current_seq = self._lock_candle_current_seq(
            connection,
            market_id=market_id,
            timeframe=timeframe,
            open_time=open_time,
        )
        if current_seq is None:
            raise RevisionPolicyError("Candle inconnue pour cette référence de révision")
        return current_seq

    def _load_revision(
        self,
        connection: Connection,
        *,
        market_id: int,
        timeframe: Timeframe,
        open_time: datetime,
        revision_seq: int,
    ) -> _StoredRevision:
        row = (
            connection.execute(
                self._revision_select().where(
                    self._lineage_where(
                        market_id=market_id,
                        timeframe=timeframe,
                        open_time=open_time,
                    ),
                    candle_revisions.c.revision_seq == revision_seq,
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise RevisionPolicyError("révision exacte introuvable")
        return _stored_revision(row)

    def _load_pending(
        self,
        connection: Connection,
        *,
        market_id: int,
        timeframe: Timeframe,
        open_time: datetime,
    ) -> _StoredRevision | None:
        row = (
            connection.execute(
                self._revision_select().where(
                    self._lineage_where(
                        market_id=market_id,
                        timeframe=timeframe,
                        open_time=open_time,
                    ),
                    candle_revisions.c.revision_status == RevisionStatus.PENDING_CONFIRMATION.value,
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return _stored_revision(row)

    def _next_revision_seq(
        self,
        connection: Connection,
        *,
        market_id: int,
        timeframe: Timeframe,
        open_time: datetime,
    ) -> int:
        value = connection.execute(
            select(func.max(candle_revisions.c.revision_seq)).where(
                self._lineage_where(
                    market_id=market_id,
                    timeframe=timeframe,
                    open_time=open_time,
                )
            )
        ).scalar_one()
        if value is None:
            raise RevisionPolicyError("une Candle existante doit posséder au moins une révision")
        return cast(int, value) + 1

    @staticmethod
    def _revision_select():
        return select(
            candle_revisions.c.revision_seq,
            candle_revisions.c.open,
            candle_revisions.c.high,
            candle_revisions.c.low,
            candle_revisions.c.close,
            candle_revisions.c.base_volume,
            candle_revisions.c.quote_volume,
            candle_revisions.c.trade_count,
            candle_revisions.c.source,
            candle_revisions.c.source_symbol,
            candle_revisions.c.observed_at,
            candle_revisions.c.accepted_at,
            candle_revisions.c.revision_status,
            candle_revisions.c.before_values_fingerprint,
            candle_revisions.c.after_values_fingerprint,
        )

    @staticmethod
    def _lineage_where(
        *,
        market_id: int,
        timeframe: Timeframe,
        open_time: datetime,
    ):
        return (
            (candle_revisions.c.market_id == market_id)
            & (candle_revisions.c.timeframe == timeframe.value)
            & (candle_revisions.c.open_time == open_time)
        )

    @staticmethod
    def _reference(
        market: Market,
        timeframe: Timeframe,
        open_time: datetime,
        revision_seq: int,
    ) -> RevisionReference:
        return RevisionReference(
            market=market,
            timeframe=timeframe,
            open_time=open_time,
            revision_seq=revision_seq,
        )

    def _accepted_now(self, observed_at: datetime) -> datetime:
        accepted_at = self._clock()
        _require_utc("accepted_at", accepted_at)
        if accepted_at < observed_at:
            raise RevisionTimestampError("accepted_at ne peut pas précéder observed_at")
        return accepted_at


def _stored_revision(row: RowMapping) -> _StoredRevision:
    return _StoredRevision(
        revision_seq=cast(int, row["revision_seq"]),
        open=cast(Decimal, row["open"]),
        high=cast(Decimal, row["high"]),
        low=cast(Decimal, row["low"]),
        close=cast(Decimal, row["close"]),
        base_volume=cast(Decimal, row["base_volume"]),
        quote_volume=cast(Decimal | None, row["quote_volume"]),
        trade_count=cast(int | None, row["trade_count"]),
        source=cast(str, row["source"]),
        source_symbol=cast(str, row["source_symbol"]),
        observed_at=cast(datetime, row["observed_at"]),
        accepted_at=cast(datetime | None, row["accepted_at"]),
        revision_status=cast(str, row["revision_status"]),
        before_values_fingerprint=cast(str | None, row["before_values_fingerprint"]),
        after_values_fingerprint=cast(str, row["after_values_fingerprint"]),
    )


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _require_utc(field_name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} doit être un datetime timezone-aware en UTC")


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} ne doit pas être vide")
