"""Frontières d’accès, normalisation, validation et ingestion des données de marché."""

from btc_analytics.market_data.ccxt_binance import CcxtBinanceMarketDataProvider
from btc_analytics.market_data.provider import (
    MarketDataProvider,
    MarketDataProviderError,
    ProviderCapabilityError,
    ProviderDataError,
    ProviderOHLCV,
    UnsupportedMarketError,
)
from btc_analytics.market_data.revisions import (
    PendingRevision,
    RevisionFingerprintError,
    RevisionObservation,
    RevisionOperation,
    RevisionPolicyError,
    RevisionReference,
    RevisionResult,
    RevisionStore,
    RevisionTimestampError,
)

__all__ = [
    "CcxtBinanceMarketDataProvider",
    "MarketDataProvider",
    "MarketDataProviderError",
    "ProviderCapabilityError",
    "ProviderDataError",
    "ProviderOHLCV",
    "PendingRevision",
    "RevisionFingerprintError",
    "RevisionObservation",
    "RevisionOperation",
    "RevisionPolicyError",
    "RevisionReference",
    "RevisionResult",
    "RevisionStore",
    "RevisionTimestampError",
    "UnsupportedMarketError",
]
