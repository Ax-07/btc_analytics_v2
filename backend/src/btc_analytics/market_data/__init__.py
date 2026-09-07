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

__all__ = [
    "CcxtBinanceMarketDataProvider",
    "MarketDataProvider",
    "MarketDataProviderError",
    "ProviderCapabilityError",
    "ProviderDataError",
    "ProviderOHLCV",
    "UnsupportedMarketError",
]
