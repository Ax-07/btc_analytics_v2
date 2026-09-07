"""Tests unitaires du schéma SQLAlchemy P1D."""

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint

from btc_analytics.storage.schema import candle_revisions, candles, markets, metadata


def _constraint_names(table_name: str, constraint_type: type[object]) -> set[str]:
    table = metadata.tables[table_name]
    return {
        str(constraint.name)
        for constraint in table.constraints
        if isinstance(constraint, constraint_type) and constraint.name is not None
    }


def test_market_data_tables_are_registered() -> None:
    assert set(metadata.tables) == {"markets", "candles", "candle_revisions"}


def test_candle_identity_is_the_canonical_composite_key() -> None:
    primary_keys = _constraint_names("candles", PrimaryKeyConstraint)
    assert primary_keys == {"pk_candles"}
    assert [column.name for column in candles.primary_key.columns] == [
        "market_id",
        "timeframe",
        "open_time",
    ]


def test_revision_identity_is_the_exact_canonical_reference() -> None:
    assert [column.name for column in candle_revisions.primary_key.columns] == [
        "market_id",
        "timeframe",
        "open_time",
        "revision_seq",
    ]


def test_candle_current_revision_foreign_key_is_deferred() -> None:
    foreign_keys = [
        constraint
        for constraint in candles.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    ]
    current_revision = next(
        constraint
        for constraint in foreign_keys
        if constraint.name == "fk_candles_current_revision"
    )
    assert current_revision.deferrable is True
    assert current_revision.initially == "DEFERRED"


def test_revision_constraints_cover_p0_state_invariants() -> None:
    check_names = _constraint_names("candle_revisions", CheckConstraint)
    assert {
        "ck_candle_revisions_revision_seq",
        "ck_candle_revisions_status",
        "ck_candle_revisions_initial_status",
        "ck_candle_revisions_acceptance_state",
        "ck_candle_revisions_observed_before_accepted",
        "ck_candle_revisions_high",
        "ck_candle_revisions_low",
        "ck_candle_revisions_base_volume",
        "ck_candle_revisions_quote_volume",
        "ck_candle_revisions_trade_count",
    } <= check_names


def test_partial_indexes_serialize_current_and_pending_states() -> None:
    indexes = {
        str(index.name): index for index in candle_revisions.indexes if index.name is not None
    }
    assert indexes["uq_candle_revisions_one_current"].unique is True
    assert indexes["uq_candle_revisions_one_pending"].unique is True
    assert indexes["ix_candle_revisions_pit"].unique is False


def test_market_has_storage_key_without_redefining_canonical_symbol() -> None:
    assert markets.c.market_id.primary_key is True
    assert markets.c.canonical_symbol.unique is None
