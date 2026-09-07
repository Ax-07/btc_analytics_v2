"""Créer le schéma PostgreSQL canonique des données de marché P1D."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_market_data_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "markets",
        sa.Column("market_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("venue", sa.Text(), nullable=False),
        sa.Column("base_asset", sa.Text(), nullable=False),
        sa.Column("quote_asset", sa.Text(), nullable=False),
        sa.Column("market_type", sa.Text(), nullable=False),
        sa.Column("canonical_symbol", sa.Text(), nullable=False),
        sa.CheckConstraint("btrim(venue) <> ''", name="ck_markets_venue_non_blank"),
        sa.CheckConstraint(
            "btrim(base_asset) <> ''",
            name="ck_markets_base_asset_non_blank",
        ),
        sa.CheckConstraint(
            "btrim(quote_asset) <> ''",
            name="ck_markets_quote_asset_non_blank",
        ),
        sa.CheckConstraint(
            "btrim(market_type) <> ''",
            name="ck_markets_market_type_non_blank",
        ),
        sa.CheckConstraint(
            "btrim(canonical_symbol) <> ''",
            name="ck_markets_canonical_symbol_non_blank",
        ),
        sa.PrimaryKeyConstraint("market_id", name="pk_markets"),
        sa.UniqueConstraint(
            "venue",
            "base_asset",
            "quote_asset",
            "market_type",
            "canonical_symbol",
            name="uq_markets_domain_identity",
        ),
    )

    op.create_table(
        "candles",
        sa.Column("market_id", sa.BigInteger(), nullable=False),
        sa.Column("timeframe", sa.Text(), nullable=False),
        sa.Column("open_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_revision_seq", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "timeframe IN ('1h', '4h', '1d')",
            name="ck_candles_timeframe",
        ),
        sa.CheckConstraint(
            """
            (
                (timeframe = '1h' AND mod(EXTRACT(EPOCH FROM open_time), 3600) = 0)
                OR (timeframe = '4h' AND mod(EXTRACT(EPOCH FROM open_time), 14400) = 0)
                OR (timeframe = '1d' AND mod(EXTRACT(EPOCH FROM open_time), 86400) = 0)
            )
            """,
            name="ck_candles_open_time_alignment",
        ),
        sa.CheckConstraint(
            """
            end_time = open_time + CASE timeframe
                WHEN '1h' THEN INTERVAL '1 hour'
                WHEN '4h' THEN INTERVAL '4 hours'
                WHEN '1d' THEN INTERVAL '24 hours'
            END
            """,
            name="ck_candles_end_time",
        ),
        sa.CheckConstraint("available_at = end_time", name="ck_candles_available_at"),
        sa.CheckConstraint(
            "current_revision_seq >= 1",
            name="ck_candles_current_revision_seq",
        ),
        sa.ForeignKeyConstraint(
            ["market_id"],
            ["markets.market_id"],
            name="fk_candles_market",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "market_id",
            "timeframe",
            "open_time",
            name="pk_candles",
        ),
    )

    op.create_table(
        "candle_revisions",
        sa.Column("market_id", sa.BigInteger(), nullable=False),
        sa.Column("timeframe", sa.Text(), nullable=False),
        sa.Column("open_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revision_seq", sa.Integer(), nullable=False),
        sa.Column("open", sa.Numeric(), nullable=False),
        sa.Column("high", sa.Numeric(), nullable=False),
        sa.Column("low", sa.Numeric(), nullable=False),
        sa.Column("close", sa.Numeric(), nullable=False),
        sa.Column("base_volume", sa.Numeric(), nullable=False),
        sa.Column("quote_volume", sa.Numeric(), nullable=True),
        sa.Column("trade_count", sa.BigInteger(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_symbol", sa.Text(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revision_status", sa.Text(), nullable=False),
        sa.Column("before_values_fingerprint", sa.Text(), nullable=True),
        sa.Column("after_values_fingerprint", sa.Text(), nullable=False),
        sa.Column("confirmation_source", sa.Text(), nullable=True),
        sa.Column("audit_reason", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "timeframe IN ('1h', '4h', '1d')",
            name="ck_candle_revisions_timeframe",
        ),
        sa.CheckConstraint(
            """
            (
                (timeframe = '1h' AND mod(EXTRACT(EPOCH FROM open_time), 3600) = 0)
                OR (timeframe = '4h' AND mod(EXTRACT(EPOCH FROM open_time), 14400) = 0)
                OR (timeframe = '1d' AND mod(EXTRACT(EPOCH FROM open_time), 86400) = 0)
            )
            """,
            name="ck_candle_revisions_open_time_alignment",
        ),
        sa.CheckConstraint(
            "revision_seq >= 1",
            name="ck_candle_revisions_revision_seq",
        ),
        sa.CheckConstraint(
            "revision_status IN "
            "('pending_confirmation', 'accepted_current', 'accepted_superseded', 'quarantined')",
            name="ck_candle_revisions_status",
        ),
        sa.CheckConstraint(
            "revision_seq <> 1 OR revision_status IN ('accepted_current', 'accepted_superseded')",
            name="ck_candle_revisions_initial_status",
        ),
        sa.CheckConstraint(
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
        sa.CheckConstraint(
            "accepted_at IS NULL OR observed_at <= accepted_at",
            name="ck_candle_revisions_observed_before_accepted",
        ),
        sa.CheckConstraint(
            "open::text NOT IN ('NaN', 'Infinity', '-Infinity')",
            name="ck_candle_revisions_open_finite",
        ),
        sa.CheckConstraint(
            "high::text NOT IN ('NaN', 'Infinity', '-Infinity')",
            name="ck_candle_revisions_high_finite",
        ),
        sa.CheckConstraint(
            "low::text NOT IN ('NaN', 'Infinity', '-Infinity')",
            name="ck_candle_revisions_low_finite",
        ),
        sa.CheckConstraint(
            "close::text NOT IN ('NaN', 'Infinity', '-Infinity')",
            name="ck_candle_revisions_close_finite",
        ),
        sa.CheckConstraint(
            "base_volume::text NOT IN ('NaN', 'Infinity', '-Infinity')",
            name="ck_candle_revisions_base_volume_finite",
        ),
        sa.CheckConstraint(
            "quote_volume IS NULL OR quote_volume::text NOT IN ('NaN', 'Infinity', '-Infinity')",
            name="ck_candle_revisions_quote_volume_finite",
        ),
        sa.CheckConstraint(
            "high >= GREATEST(open, close, low)",
            name="ck_candle_revisions_high",
        ),
        sa.CheckConstraint(
            "low <= LEAST(open, close, high)",
            name="ck_candle_revisions_low",
        ),
        sa.CheckConstraint(
            "base_volume >= 0",
            name="ck_candle_revisions_base_volume",
        ),
        sa.CheckConstraint(
            "quote_volume IS NULL OR quote_volume >= 0",
            name="ck_candle_revisions_quote_volume",
        ),
        sa.CheckConstraint(
            "trade_count IS NULL OR trade_count >= 0",
            name="ck_candle_revisions_trade_count",
        ),
        sa.CheckConstraint(
            "btrim(source) <> ''",
            name="ck_candle_revisions_source_non_blank",
        ),
        sa.CheckConstraint(
            "btrim(source_symbol) <> ''",
            name="ck_candle_revisions_source_symbol_non_blank",
        ),
        sa.CheckConstraint(
            "btrim(after_values_fingerprint) <> ''",
            name="ck_candle_revisions_after_fingerprint_non_blank",
        ),
        sa.CheckConstraint(
            "before_values_fingerprint IS NULL OR btrim(before_values_fingerprint) <> ''",
            name="ck_candle_revisions_before_fingerprint_non_blank",
        ),
        sa.CheckConstraint(
            "confirmation_source IS NULL OR btrim(confirmation_source) <> ''",
            name="ck_candle_revisions_confirmation_source_non_blank",
        ),
        sa.CheckConstraint(
            "audit_reason IS NULL OR btrim(audit_reason) <> ''",
            name="ck_candle_revisions_audit_reason_non_blank",
        ),
        sa.ForeignKeyConstraint(
            ["market_id", "timeframe", "open_time"],
            ["candles.market_id", "candles.timeframe", "candles.open_time"],
            name="fk_candle_revisions_candle",
            deferrable=True,
            initially="DEFERRED",
        ),
        sa.PrimaryKeyConstraint(
            "market_id",
            "timeframe",
            "open_time",
            "revision_seq",
            name="pk_candle_revisions",
        ),
    )

    op.create_index(
        "uq_candle_revisions_one_current",
        "candle_revisions",
        ["market_id", "timeframe", "open_time"],
        unique=True,
        postgresql_where=sa.text("revision_status = 'accepted_current'"),
    )
    op.create_index(
        "uq_candle_revisions_one_pending",
        "candle_revisions",
        ["market_id", "timeframe", "open_time"],
        unique=True,
        postgresql_where=sa.text("revision_status = 'pending_confirmation'"),
    )
    op.create_index(
        "ix_candle_revisions_pit",
        "candle_revisions",
        ["market_id", "timeframe", "open_time", sa.text("accepted_at DESC")],
        unique=False,
        postgresql_where=sa.text("accepted_at IS NOT NULL"),
    )

    op.create_foreign_key(
        "fk_candles_current_revision",
        "candles",
        "candle_revisions",
        ["market_id", "timeframe", "open_time", "current_revision_seq"],
        ["market_id", "timeframe", "open_time", "revision_seq"],
        deferrable=True,
        initially="DEFERRED",
    )


def downgrade() -> None:
    op.drop_constraint("fk_candles_current_revision", "candles", type_="foreignkey")
    op.drop_index("ix_candle_revisions_pit", table_name="candle_revisions")
    op.drop_index("uq_candle_revisions_one_pending", table_name="candle_revisions")
    op.drop_index("uq_candle_revisions_one_current", table_name="candle_revisions")
    op.drop_table("candle_revisions")
    op.drop_table("candles")
    op.drop_table("markets")
