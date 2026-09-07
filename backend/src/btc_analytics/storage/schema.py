"""Schéma SQLAlchemy canonique PostgreSQL des données de marché P1D."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    MetaData,
    Numeric,
    PrimaryKeyConstraint,
    Table,
    Text,
    UniqueConstraint,
    text,
)

metadata = MetaData()

MARKET_TABLE_NAME = "markets"
CANDLE_TABLE_NAME = "candles"
CANDLE_REVISION_TABLE_NAME = "candle_revisions"

_TIMEFRAME_CHECK = "timeframe IN ('1h', '4h', '1d')"
_OPEN_TIME_ALIGNMENT_CHECK = """
(
    (timeframe = '1h' AND mod(EXTRACT(EPOCH FROM open_time), 3600) = 0)
    OR (timeframe = '4h' AND mod(EXTRACT(EPOCH FROM open_time), 14400) = 0)
    OR (timeframe = '1d' AND mod(EXTRACT(EPOCH FROM open_time), 86400) = 0)
)
"""


def _non_blank(column_name: str) -> str:
    return f"btrim({column_name}) <> ''"


def _optional_non_blank(column_name: str) -> str:
    return f"({column_name} IS NULL OR btrim({column_name}) <> '')"


def _finite_numeric(column_name: str) -> str:
    return f"{column_name}::text NOT IN ('NaN', 'Infinity', '-Infinity')"


markets = Table(
    MARKET_TABLE_NAME,
    metadata,
    Column("market_id", BigInteger, Identity(), nullable=False),
    Column("venue", Text, nullable=False),
    Column("base_asset", Text, nullable=False),
    Column("quote_asset", Text, nullable=False),
    Column("market_type", Text, nullable=False),
    Column("canonical_symbol", Text, nullable=False),
    PrimaryKeyConstraint("market_id", name="pk_markets"),
    UniqueConstraint(
        "venue",
        "base_asset",
        "quote_asset",
        "market_type",
        "canonical_symbol",
        name="uq_markets_domain_identity",
    ),
    CheckConstraint(_non_blank("venue"), name="ck_markets_venue_non_blank"),
    CheckConstraint(_non_blank("base_asset"), name="ck_markets_base_asset_non_blank"),
    CheckConstraint(_non_blank("quote_asset"), name="ck_markets_quote_asset_non_blank"),
    CheckConstraint(_non_blank("market_type"), name="ck_markets_market_type_non_blank"),
    CheckConstraint(
        _non_blank("canonical_symbol"),
        name="ck_markets_canonical_symbol_non_blank",
    ),
)

candles = Table(
    CANDLE_TABLE_NAME,
    metadata,
    Column(
        "market_id",
        BigInteger,
        ForeignKey("markets.market_id", name="fk_candles_market", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("timeframe", Text, nullable=False),
    Column("open_time", DateTime(timezone=True), nullable=False),
    Column("end_time", DateTime(timezone=True), nullable=False),
    Column("available_at", DateTime(timezone=True), nullable=False),
    Column("ingested_at", DateTime(timezone=True), nullable=False),
    Column("current_revision_seq", Integer, nullable=False),
    PrimaryKeyConstraint("market_id", "timeframe", "open_time", name="pk_candles"),
    CheckConstraint(_TIMEFRAME_CHECK, name="ck_candles_timeframe"),
    CheckConstraint(_OPEN_TIME_ALIGNMENT_CHECK, name="ck_candles_open_time_alignment"),
    CheckConstraint(
        """
        end_time = open_time + CASE timeframe
            WHEN '1h' THEN INTERVAL '1 hour'
            WHEN '4h' THEN INTERVAL '4 hours'
            WHEN '1d' THEN INTERVAL '24 hours'
        END
        """,
        name="ck_candles_end_time",
    ),
    CheckConstraint("available_at = end_time", name="ck_candles_available_at"),
    CheckConstraint("current_revision_seq >= 1", name="ck_candles_current_revision_seq"),
    ForeignKeyConstraint(
        ["market_id", "timeframe", "open_time", "current_revision_seq"],
        [
            "candle_revisions.market_id",
            "candle_revisions.timeframe",
            "candle_revisions.open_time",
            "candle_revisions.revision_seq",
        ],
        name="fk_candles_current_revision",
        deferrable=True,
        initially="DEFERRED",
        use_alter=True,
    ),
)

candle_revisions = Table(
    CANDLE_REVISION_TABLE_NAME,
    metadata,
    Column("market_id", BigInteger, nullable=False),
    Column("timeframe", Text, nullable=False),
    Column("open_time", DateTime(timezone=True), nullable=False),
    Column("revision_seq", Integer, nullable=False),
    Column("open", Numeric(), nullable=False),
    Column("high", Numeric(), nullable=False),
    Column("low", Numeric(), nullable=False),
    Column("close", Numeric(), nullable=False),
    Column("base_volume", Numeric(), nullable=False),
    Column("quote_volume", Numeric(), nullable=True),
    Column("trade_count", BigInteger, nullable=True),
    Column("source", Text, nullable=False),
    Column("source_symbol", Text, nullable=False),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=True),
    Column("revision_status", Text, nullable=False),
    Column("before_values_fingerprint", Text, nullable=True),
    Column("after_values_fingerprint", Text, nullable=False),
    Column("confirmation_source", Text, nullable=True),
    Column("audit_reason", Text, nullable=True),
    PrimaryKeyConstraint(
        "market_id",
        "timeframe",
        "open_time",
        "revision_seq",
        name="pk_candle_revisions",
    ),
    ForeignKeyConstraint(
        ["market_id", "timeframe", "open_time"],
        ["candles.market_id", "candles.timeframe", "candles.open_time"],
        name="fk_candle_revisions_candle",
        deferrable=True,
        initially="DEFERRED",
    ),
    CheckConstraint(_TIMEFRAME_CHECK, name="ck_candle_revisions_timeframe"),
    CheckConstraint(
        _OPEN_TIME_ALIGNMENT_CHECK,
        name="ck_candle_revisions_open_time_alignment",
    ),
    CheckConstraint("revision_seq >= 1", name="ck_candle_revisions_revision_seq"),
    CheckConstraint(
        "revision_status IN "
        "('pending_confirmation', 'accepted_current', 'accepted_superseded', 'quarantined')",
        name="ck_candle_revisions_status",
    ),
    CheckConstraint(
        "revision_seq <> 1 OR revision_status IN ('accepted_current', 'accepted_superseded')",
        name="ck_candle_revisions_initial_status",
    ),
    CheckConstraint(
        """
        (
            revision_status IN ('accepted_current', 'accepted_superseded')
            AND accepted_at IS NOT NULL
        ) OR (
            revision_status IN ('pending_confirmation', 'quarantined')
            AND accepted_at IS NULL
        )
        """,
        name="ck_candle_revisions_acceptance_state",
    ),
    CheckConstraint(
        "accepted_at IS NULL OR observed_at <= accepted_at",
        name="ck_candle_revisions_observed_before_accepted",
    ),
    CheckConstraint(_finite_numeric("open"), name="ck_candle_revisions_open_finite"),
    CheckConstraint(_finite_numeric("high"), name="ck_candle_revisions_high_finite"),
    CheckConstraint(_finite_numeric("low"), name="ck_candle_revisions_low_finite"),
    CheckConstraint(_finite_numeric("close"), name="ck_candle_revisions_close_finite"),
    CheckConstraint(
        _finite_numeric("base_volume"),
        name="ck_candle_revisions_base_volume_finite",
    ),
    CheckConstraint(
        "quote_volume IS NULL OR quote_volume::text NOT IN ('NaN', 'Infinity', '-Infinity')",
        name="ck_candle_revisions_quote_volume_finite",
    ),
    CheckConstraint(
        "high >= GREATEST(open, close, low)",
        name="ck_candle_revisions_high",
    ),
    CheckConstraint(
        "low <= LEAST(open, close, high)",
        name="ck_candle_revisions_low",
    ),
    CheckConstraint("base_volume >= 0", name="ck_candle_revisions_base_volume"),
    CheckConstraint(
        "quote_volume IS NULL OR quote_volume >= 0",
        name="ck_candle_revisions_quote_volume",
    ),
    CheckConstraint(
        "trade_count IS NULL OR trade_count >= 0",
        name="ck_candle_revisions_trade_count",
    ),
    CheckConstraint(_non_blank("source"), name="ck_candle_revisions_source_non_blank"),
    CheckConstraint(
        _non_blank("source_symbol"),
        name="ck_candle_revisions_source_symbol_non_blank",
    ),
    CheckConstraint(
        _non_blank("after_values_fingerprint"),
        name="ck_candle_revisions_after_fingerprint_non_blank",
    ),
    CheckConstraint(
        _optional_non_blank("before_values_fingerprint"),
        name="ck_candle_revisions_before_fingerprint_non_blank",
    ),
    CheckConstraint(
        _optional_non_blank("confirmation_source"),
        name="ck_candle_revisions_confirmation_source_non_blank",
    ),
    CheckConstraint(
        _optional_non_blank("audit_reason"),
        name="ck_candle_revisions_audit_reason_non_blank",
    ),
)

Index(
    "uq_candle_revisions_one_current",
    candle_revisions.c.market_id,
    candle_revisions.c.timeframe,
    candle_revisions.c.open_time,
    unique=True,
    postgresql_where=text("revision_status = 'accepted_current'"),
)
Index(
    "uq_candle_revisions_one_pending",
    candle_revisions.c.market_id,
    candle_revisions.c.timeframe,
    candle_revisions.c.open_time,
    unique=True,
    postgresql_where=text("revision_status = 'pending_confirmation'"),
)
Index(
    "ix_candle_revisions_pit",
    candle_revisions.c.market_id,
    candle_revisions.c.timeframe,
    candle_revisions.c.open_time,
    candle_revisions.c.accepted_at.desc(),
    postgresql_where=text("accepted_at IS NOT NULL"),
)
