"""
Momentum calculation module.
"""

from typing import cast

import pandas as pd
from loguru import logger


class MomentumCalculator:
    """Handles momentum calculations for dual momentum strategy."""

    def __init__(self) -> None:
        pass

    def calculate_total_return(self, price_series: pd.Series) -> float:
        """
        Calculate total return over the entire period.

        Args:
            price_series: Price series for a single symbol

        Returns:
            Total return as decimal (e.g., 0.15 for 15%)
        """
        max_series_length = 2

        if len(price_series) < max_series_length:
            logger.warning("Price series too short for return calculation")
            return 0.0

        clean_series = price_series.dropna()

        if len(clean_series) < max_series_length:
            logger.warning("Not enough clean data points for return calculation")
            return 0.0

        start_price = clean_series.iloc[0]
        end_price = clean_series.iloc[-1]

        if start_price <= 0:
            logger.warning(f"Invalid start price: {start_price}")
            return 0.0

        return (end_price / start_price) - 1

    def calculate_momentum(self, price_data: pd.DataFrame) -> pd.Series:
        """
        Calculate momentum for all symbols in the dataset.

        Args:
            price_data: DataFrame with price data for multiple symbols

        Returns:
            Series with momentum values for each symbol
        """
        logger.info("Calculating momentum for all symbols")

        momentum_results = {}

        for symbol in price_data.columns:
            momentum = self.calculate_total_return(cast("pd.Series", price_data[symbol]))
            momentum_results[symbol] = momentum

            logger.info(f"{symbol}: {momentum:.4f} ({momentum:.2%})")

        momentum_series = pd.Series(momentum_results)

        momentum_series = momentum_series.sort_values(ascending=False)

        logger.info(f"Best performer: {momentum_series.index[0]} with {momentum_series.iloc[0]:.2%}")

        return momentum_series

    def get_momentum_statistics(self, momentum_results: pd.Series) -> dict[str, float]:
        """
        Calculate momentum statistics.

        Args:
            momentum_results: Series with momentum values

        Returns:
            Dictionary with statistics
        """
        return cast(
            "dict[str, float]",
            {
                "best_momentum": momentum_results.max(),
                "worst_momentum": momentum_results.min(),
                "average_momentum": momentum_results.mean(),
                "momentum_std": momentum_results.std(),
                "momentum_spread": momentum_results.max() - momentum_results.min(),
            },
        )
